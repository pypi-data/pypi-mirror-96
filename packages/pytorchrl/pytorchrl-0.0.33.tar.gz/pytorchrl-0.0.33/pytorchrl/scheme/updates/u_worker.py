import sys
import ray
import time
import torch
import queue
import threading
from collections import defaultdict
from ..base.worker import Worker as W
from ..utils import ray_get_and_free, average_gradients, broadcast_message


class UWorker(W):
    """
    Update worker. Handles actor updates.

    This worker receives gradients from gradient workers and then handle actor
    model updates. Updated weights are broadcasted back to gradient workers
    if required by the training scheme.

    Parameters
    ----------
    grad_workers_factory : func
        A function that creates a set of gradientc omputation workers.
    index_worker : int
        Worker index.
    col_fraction_workers : float
        Minimum fraction of samples required to stop if collection is
        synchronously coordinated and most workers have finished their
        collection task.
    grad_execution : str
        Execution patterns for gradients computation.
    grad_communication : str
        Communication coordination pattern for gradient computation workers.
    decentralized_update_execution : bool
        Whether the gradients are applied in the update workers (central update)
        or broadcasted to all gradient workers for a decentralized update.
    local_device : str
        "cpu" or specific GPU "cuda:number`" to use for computation.

    Attributes
    ----------
    grad_execution : str
        Execution patterns for gradients computation.
    grad_communication : str
        Communication coordination pattern for gradient computation workers.
    grad_workers : GWorkerSet
        A GWorkerSet class instance.
    local_worker : GWorker
        grad_workers local worker.
    remote_workers : List
        grad_workers remote data collection workers.
    num_workers : int
        Number of gradient remote workers.
    updater : UpdaterThread
        Class handling updates, calling grad_workers to get gradients,
        performing update steps and placing update information into the
        output queue `outqueue`.
    """

    def __init__(self,
                 grad_workers_factory,
                 index_worker=0,
                 col_fraction_workers=1.0,
                 grad_execution="parallelised",
                 grad_communication="synchronous",
                 decentralized_update_execution=False,
                 local_device=None):

        super(UWorker, self).__init__(index_worker)

        self.grad_execution = grad_execution
        self.grad_communication = grad_communication

        # Computation device
        dev = local_device or "cuda" if torch.cuda.is_available() else "cpu"

        self.grad_workers = grad_workers_factory(dev, index_worker)
        self.local_worker = self.grad_workers.local_worker()
        self.remote_workers = self.grad_workers.remote_workers()
        self.num_workers = len(self.grad_workers.remote_workers())

        # Create CWorkerSet instance
        if decentralized_update_execution:
            # Setup the distributed processes for gradient averaging
            ip = ray.get(self.remote_workers[0].get_node_ip.remote())
            port = ray.get(self.remote_workers[0].find_free_port.remote())
            address = "tcp://{ip}:{port}".format(ip=ip, port=port)
            ray.get([worker.setup_torch_data_parallel.remote(
                address, i, len(self.remote_workers), "nccl")
                     for i, worker in enumerate(self.remote_workers)])

        # Create UpdaterThread
        self.updater = UpdaterThread(
            local_worker=self.local_worker,
            remote_workers=self.remote_workers,
            col_fraction_workers=col_fraction_workers,
            grad_communication=grad_communication,
            grad_execution=grad_execution,
            decentralized_update_execution=decentralized_update_execution,
        )

        # Print worker information
        if index_worker > 0: self.print_worker_info()

    @property
    def actor_version(self):
        """Number of times Actor has been updated."""
        version = self.local_worker.actor_version
        return version

    def step(self):
        """Pulls information from update operations from  `self.updater.outqueue`."""

        if self.grad_communication == "synchronous": self.updater.step()
        new_info = self.updater.outqueue.get()
        return new_info

    def save_model(self, fname):
        """
        Save current version of actor as a torch loadable checkpoint.

        Parameters
        ----------
        fname : str
            Filename given to the checkpoint.

        Returns
        -------
        save_name : str
            Path to saved file.
        """

        if not self.updater.decentralized_update_execution:
            save_name = self.local_worker.save_model(fname)
        else:
            save_name = ray.get(self.remote_workers[0].save_model.remote(fname))

        return save_name

    def stop(self):
        """Stop remote workers"""
        self.updater.stopped = True

        self.grad_workers.local_worker().stop()
        for e in self.grad_workers.remote_workers():
            e.stop.remote()
            e.terminate_worker.remote()

    def update_algo_parameter(self, parameter_name, new_parameter_value):
        """
        If `parameter_name` is an attribute of Worker.algo, change its value to
        `new_parameter_value value`.

        Parameters
        ----------
        parameter_name : str
            Algorithm attribute name
        """
        self.local_worker.update_algo_parameter(parameter_name, new_parameter_value)
        for e in self.remote_workers:
            e.update_algo_parameter.remote(parameter_name, new_parameter_value)


class UpdaterThread(threading.Thread):
    """
    This class receives data from the workers and continuously updates central actor.

    Parameters
    ----------
    outqueue : queue.Queue
        Queue to store the info dicts resulting from the model update operation.
    local_worker : GWorker
        Local GWorker that acts as a parameter server.
    remote_workers : List
        grad_workers remote data collection workers.
    decentralized_update_execution : bool
        Whether decentralized execution pattern for update steps is enabled or not.
    col_fraction_workers : float
        Minimum fraction of samples required to stop if collection is
        synchronously coordinated and most workers have finished their
        collection task.
    grad_execution : str
        Execution patterns for gradients computation.
    grad_communication : str
        Communication coordination pattern for gradient computation workers.

    Attributes
    ----------
    stopped : bool
        Whether or not the thread in running.
    outqueue : queue.Queue
        Queue to store the info dicts resulting from the model update operation.
    local_worker : Worker
        Local worker that acts as a parameter server.
    remote_workers : List
        Minimum fraction of samples required to stop if collection is
        synchronously coordinated and most workers have finished their
        collection task.
    num_workers : int
        Number of gradient remote workers.
    decentralized_update_execution : bool
        Whether decentralized execution pattern for update steps is enabled or not.
    col_fraction_workers : float
        Minimum fraction of samples required to stop if collection is
        synchronously coordinated and most workers have finished their
        collection task.
    grad_execution : str
        Execution patterns for gradients computation.
    grad_communication : str
        Communication coordination pattern for gradient computation workers.
    """

    def __init__(self,
                 local_worker,
                 remote_workers,
                 decentralized_update_execution,
                 col_fraction_workers=1.0,
                 grad_execution="distributed",
                 grad_communication="synchronous"):

        threading.Thread.__init__(self)

        self.stopped = False
        self.outqueue = queue.SimpleQueue()
        self.local_worker = local_worker
        self.remote_workers = remote_workers
        self.num_workers = len(remote_workers)
        self.decentralized_update_execution = decentralized_update_execution
        self.grad_execution = grad_execution
        self.fraction_workers = col_fraction_workers
        self.grad_communication = grad_communication

        if grad_execution == "centralised" and grad_communication == "synchronous":
            pass

        elif grad_execution == "centralised" and grad_communication == "asynchronous":
            self.start() # Start UpdaterThread

        elif grad_execution == "parallelised" and grad_communication == "synchronous":
            pass

        elif grad_execution == "parallelised" and grad_communication == "asynchronous":
            self.start() # Start UpdaterThread

    def run(self):
        while not self.stopped:
            self.step()
        sys.exit()

    def step(self):
        """
        Takes a logical optimization step and places output information in the
        output queue.
        """

        if self.grad_execution == "centralised" and self.grad_communication == "synchronous":
            _, info = self.local_worker.step(self.decentralized_update_execution)
            info["update_version"] = self.local_worker.actor_version
            self.local_worker.apply_gradients()

        elif self.grad_execution == "centralised" and self.grad_communication == "asynchronous":
            _, info = self.local_worker.step(self.decentralized_update_execution)
            info["update_version"] = self.local_worker.actor_version
            self.local_worker.apply_gradients()

        elif self.grad_execution == "parallelised" and self.grad_communication == "synchronous":

            to_average = []
            step_metrics = defaultdict(float)

            # Start get data in all workers that have sync collection
            broadcast_message("sync", b"start-continue")
            pending_tasks = [e.get_data.remote() for e in self.remote_workers]

            # Keep checking how many workers have finished until percent% are ready
            if self.fraction_workers < 1.0:
                samples_ready = []
                while len(samples_ready) < (self.num_workers * self.fraction_workers):
                    samples_ready, samples_not_ready = ray.wait(pending_tasks,
                      num_returns=len(pending_tasks), timeout=0.005)
                # Send stop message to the workers that have sync collection
                broadcast_message("sync", b"stop")

            # Start gradient computation in all workers
            pending = {e.get_grads.remote(
                self.decentralized_update_execution): e for e in self.remote_workers}

            # Compute model updates
            while pending:

                # Get gradients
                out = ray.wait(list(pending.keys()))[0][0]
                gradients, info = ray_get_and_free(out)
                pending.pop(out)

                # Update info dict
                info["update_version"] = self.local_worker.actor_version

                # Update counters
                for k, v in info.items(): step_metrics[k] += v

                # Store gradients to average later
                to_average.append(gradients)

            # Update info dict
            info = {k: v / self.num_workers if k != "collected_samples" else
            v for k, v in step_metrics.items()}

            if not self.decentralized_update_execution:
                # Average and apply gradients
                t = time.time()
                self.local_worker.apply_gradients(average_gradients(to_average))
                avg_grads_t = time.time() - t
                info.update({"debug/avg_grads_time": avg_grads_t})

                # Update workers with current weights
                t = time.time()
                self.sync_weights()
                sync_grads_t = time.time() - t
                info.update({"debug/sync_grads_time": sync_grads_t})

            else:
                self.local_worker.local_worker.actor_version += 1

        elif self.grad_execution == "parallelised" and self.grad_communication == "asynchronous":

            # If first call, call for gradients from all workers
            if self.local_worker.actor_version == 0:
                self.pending_gradients = {}
                for e in self.remote_workers:
                    future = e.step.remote()
                    self.pending_gradients[future] = e

            # Wait for first gradients ready
            wait_results = ray.wait(list(self.pending_gradients.keys()), timeout=60)

            future = wait_results[0][0]

            # Get gradients
            gradients, info = ray_get_and_free(future)
            e = self.pending_gradients.pop(future)

            # Update info dict
            info["update_version"] = self.local_worker.actor_version

            # Update local worker weights
            self.local_worker.apply_gradients(gradients)

            # Update remote worker model version
            weights = ray.put({
                "version": self.local_worker.actor_version,
                "weights": self.local_worker.get_weights()})
            e.set_weights.remote(weights)

            # Call compute_gradients in remote worker again
            future = e.step.remote()
            self.pending_gradients[future] = e

        # Add step info to queue
        self.outqueue.put(info)

    def sync_weights(self):
        """Synchronize gradient worker models with updater worker model"""
        weights = ray.put({
            "version": self.local_worker.actor_version,
            "weights": self.local_worker.get_weights()})
        for e in self.remote_workers: e.set_weights.remote(weights)
