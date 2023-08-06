"""
Streaming Parallel Data Processing
===================================================================

Neuraxle steps for streaming data in parallel in the pipeline

..
    Copyright 2019, Neuraxio Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
import warnings
from abc import abstractmethod
from multiprocessing import Queue
from multiprocessing.context import Process
from threading import Thread
from typing import Tuple, List, Union, Iterable, Any

from neuraxle.base import NamedTupleList, ExecutionContext, BaseStep, MetaStep, BaseSaver, _FittableStep, \
    BaseTransformer, NonFittableMixin, MixinForBaseTransformer
from neuraxle.data_container import DataContainer, ListDataContainer, AbsentValuesNullObject
from neuraxle.pipeline import Pipeline, MiniBatchSequentialPipeline, Joiner
from neuraxle.steps.numpy import NumpyConcatenateOuterBatch


class ObservableQueueMixin(MixinForBaseTransformer):
    """
    A class to represent a step that can put items in a queue.
    It can also notify other queues that have subscribed to him using subscribe.

    .. seealso::
        :class:`BaseStep`,
        :class:`QueuedPipelineTask`,
        :class:`QueueWorker`,
        :class:`BaseQueuedPipeline`,
        :class:`ParallelQueuedPipeline`,
        :class:`SequentialQueuedPipeline`
    """

    def __init__(self, queue):
        MixinForBaseTransformer.__init__(self)
        self.queue = queue
        self.observers = []
        self._add_observable_queue_step_saver()

    def teardown(self):
        self.queue = None
        return self

    def _add_observable_queue_step_saver(self):
        if not hasattr(self, 'savers'):
            warnings.warn(
                'Please initialize Mixins in the good order. ObservableQueueMixin should be initialized after '
                'Appending the ObservableQueueStepSaver to the savers. Saving might fail.'
            )
            self.savers = [ObservableQueueStepSaver()]
        else:
            self.savers.append(ObservableQueueStepSaver())

    def subscribe(self, observer_queue_worker: 'ObservableQueueMixin') -> 'ObservableQueueMixin':
        """
        Subscribe a queue worker.
        The subscribed queue workers get notified when :func:`~neuraxle.distributed.streaming.ObservableQueueMixin.notify` is called.
        """
        self.observers.append(observer_queue_worker.queue)
        return self

    def get(self) -> 'QueuedPipelineTask':
        """
        Get last item in queue.
        """
        return self.queue.get()

    def put(self, value: DataContainer):
        """
        Put a queued pipeline task in queue.
        """
        self.queue.put(QueuedPipelineTask(step_name=self.name, data_container=value.copy()))

    def notify(self, value):
        """
        Notify all subscribed queue workers
        """
        for observer in self.observers:
            observer.put(value)


class QueuedPipelineTask(object):
    """
    Data object to contain the tasks processed by the queued pipeline.

    .. seealso::
        :class:`QueueWorker`,
        :class:`BaseQueuedPipeline`,
        :class:`ParallelQueuedPipeline`,
        :class:`SequentialQueuedPipeline`
    """

    def __init__(self, data_container, step_name=None):
        self.step_name = step_name
        self.data_container = data_container


class ObservableQueueStepSaver(BaseSaver):
    """
    Saver for observable queue steps.

    .. seealso::
        :class:`QueueWorker`,
        :class:`neuraxle.base.BaseSaver`,
        :class:`BaseQueuedPipeline`,
        :class:`ParallelQueuedPipeline`,
        :class:`SequentialQueuedPipeline`
    """

    def save_step(self, step: BaseTransformer, context: 'ExecutionContext') -> BaseTransformer:
        step.queue = None
        step.observers = []
        return step

    def can_load(self, step: BaseTransformer, context: 'ExecutionContext') -> bool:
        return True

    def load_step(self, step: 'BaseTransformer', context: 'ExecutionContext') -> 'BaseTransformer':
        step.queue = Queue()
        return step


class QueueWorker(ObservableQueueMixin, MetaStep):
    """
    Start multiple Process or Thread that process items from the queue of batches to process.
    It is both an observable, and observer.
    It notifies the results of the wrapped step handle transform method.
    It receives the next data container to process.

    .. seealso::
        :class:`Observer`,
        :class:`Observable`,
        :class:`MetaStepMixin`,
        :class:`BaseStep`
    """

    def __init__(
            self,
            wrapped: BaseTransformer,
            max_queue_size: int,
            n_workers: int,
            use_threading: bool,
            additional_worker_arguments=None,
            use_savers=False
    ):
        if not additional_worker_arguments:
            additional_worker_arguments = [[] for _ in range(n_workers)]

        MetaStep.__init__(self, wrapped)
        ObservableQueueMixin.__init__(self, Queue(maxsize=max_queue_size))

        self.use_threading: bool = use_threading
        self.workers: List[Process] = []
        self.n_workers: int = n_workers
        self.observers: List[Queue] = []
        self.additional_worker_arguments = additional_worker_arguments
        self.use_savers = use_savers

    def start(self, context: ExecutionContext):
        """
        Start multiple processes or threads with the worker function as a target.

        :param context: execution context
        :type context: ExecutionContext
        :return:
        """
        target_function = worker_function
        if self.use_savers:
            self.save(context, full_dump=True)
            target_function = worker_function

        self.workers = []
        for _, worker_arguments in zip(range(self.n_workers), self.additional_worker_arguments):
            if self.use_threading:
                p = Thread(target=target_function, args=(self, context, self.use_savers, worker_arguments))
            else:
                p = Process(target=target_function, args=(self, context, self.use_savers, worker_arguments))

            p.daemon = True
            p.start()
            self.workers.append(p)

    def teardown(self):
        """
        Stop all processes on teardown.

        :return: teardowned self
        """
        self.stop()
        return self

    def stop(self):
        """
        Stop all of the workers.

        :return:
        """
        if not self.use_threading:
            [w.terminate() for w in self.workers]

        self.workers = []
        self.observers = []


def worker_function(queue_worker: QueueWorker, context: ExecutionContext, use_savers: bool,
                    additional_worker_arguments):
    """
    Worker function that transforms the items inside the queue of items to process.

    :param queue_worker: step to transform
    :param context: execution context
    :param use_savers: use savers
    :param additional_worker_arguments: any additional arguments that need to be passed to the workers
    :return:
    """
    step = queue_worker.get_step()
    if use_savers:
        saved_queue_worker: QueueWorker = context.load(queue_worker.get_name())
        step = saved_queue_worker.get_step()

    additional_worker_arguments = tuple(
        additional_worker_arguments[i: i + 2] for i in range(0, len(additional_worker_arguments), 2)
    )

    for argument_name, argument_value in additional_worker_arguments:
        step.__dict__.update({argument_name: argument_value})

    while True:
        try:
            task: QueuedPipelineTask = queue_worker.get()
            summary_id = task.data_container.summary_id
            data_container = step.handle_transform(task.data_container, context)
            data_container = data_container.set_summary_id(summary_id)
            queue_worker.notify(QueuedPipelineTask(step_name=queue_worker.name, data_container=data_container))
        except Exception as err:
            queue_worker.notify(QueuedPipelineTask(step_name=queue_worker.name, data_container=err))


QueuedPipelineStepsTuple = Union[
    BaseTransformer,  # step
    Tuple[int, BaseTransformer],  # (n_workers, step)
    Tuple[str, BaseTransformer],  # (step_name, step)
    Tuple[str, int, BaseTransformer],  # (step_name, n_workers, step)
    Tuple[str, int, int, BaseTransformer],  # (step_name, n_workers, max_queue_size, step)
    Tuple[str, int, List[Tuple], BaseTransformer],  # (step_name, n_workers, additional_worker_arguments, step)
    Tuple[str, int, List[Tuple], BaseTransformer]  # (step_name, n_workers, additional_worker_arguments, step)
]


class BaseQueuedPipeline(MiniBatchSequentialPipeline):
    """
    Sub class of :class:`Pipeline`.
    Transform data in many pipeline steps at once in parallel in the pipeline using multiprocessing Queues.

    Example usage :

    .. code-block:: python

        # step name, step

        p = QueuedPipeline([
            ('step_a', Identity()),
            ('step_b', Identity()),
        ], n_workers=1, batch_size=10, max_queue_size=10)

        # step name, number of workers, step

        p = QueuedPipeline([
            ('step_a', 1, Identity()),
            ('step_b', 1, Identity()),
        ], batch_size=10, max_queue_size=10)

        # step name, number of workers, and max size

        p = QueuedPipeline([
            ('step_a', 1, 10, Identity()),
            ('step_b', 1, 10, Identity()),
        ], batch_size=10)

        # step name, number of workers for each step, and additional argument for each worker

        p = QueuedPipeline([
            ('step_a', 1, [('host', 'host1'), ('host', 'host2')], 10, Identity())
        ], batch_size=10)

        # step name, number of workers for each step, additional argument for each worker, and max size

        p = QueuedPipeline([
            ('step_a', 1, [('host', 'host1'), ('host', 'host2')], 10, Identity())
        ], batch_size=10)

    :param steps: pipeline steps
    :param batch_size: number of elements to combine into a single batch
    :param n_workers_per_step: number of workers to spawn per step
    :param max_queue_size: max number of elements inside the processing queue
    :param data_joiner: transformer step to join streamed batches together at the end of the pipeline
    :param use_threading: (Optional.) use threading for parallel processing. multiprocessing.context.Process is used by default.
    :param use_savers: use savers to serialize steps for parallel processing.
    :param include_incomplete_batch: (Optional.) A bool representing
    whether the last batch should be dropped in the case it has fewer than
    `batch_size` elements; the default behavior is not to drop the smaller
    batch.
    :param default_value_data_inputs: expected_outputs default fill value
    for padding and values outside iteration range, or :class:`~neuraxle.data_container.DataContainer.AbsentValuesNullObject`
    to trim absent values from the batch
    :param default_value_expected_outputs: expected_outputs default fill value
    for padding and values outside iteration range, or :class:`~neuraxle.data_container.DataContainer.AbsentValuesNullObject`
    to trim absent values from the batch
    :param cache_folder: cache_folder if its at the root of the pipeline

    .. seealso::
        :class:`QueueWorker`,
        :class:`QueueJoiner`,
        :class:`CustomPipelineMixin`,
        :class:`Pipeline`
    """

    def __init__(
            self,
            steps: List[QueuedPipelineStepsTuple],
            batch_size: int,
            n_workers_per_step: int = None,
            max_queue_size: int = None,
            data_joiner = None,
            use_threading: bool = False,
            use_savers: bool = False,
            include_incomplete_batch: bool = False,
            default_value_data_inputs: Union[Any, AbsentValuesNullObject] = None,
            default_value_expected_outputs: Union[Any, AbsentValuesNullObject] = None,
            cache_folder: str = None,
    ):
        if data_joiner is None:
            data_joiner = NumpyConcatenateOuterBatch()
        self.data_joiner = data_joiner
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.n_workers_per_step = n_workers_per_step
        self.use_threading = use_threading
        self.use_savers = use_savers

        self.batch_size: int = batch_size
        self.include_incomplete_batch: bool = include_incomplete_batch
        self.default_value_data_inputs: Union[Any, AbsentValuesNullObject] = default_value_data_inputs
        self.default_value_expected_outputs: Union[Any, AbsentValuesNullObject] = default_value_expected_outputs

        MiniBatchSequentialPipeline.__init__(
            self,
            steps=self._initialize_steps_as_tuple(steps),
            cache_folder=cache_folder,
            batch_size=batch_size,
            include_incomplete_batch=include_incomplete_batch,
            default_value_data_inputs=default_value_data_inputs,
            default_value_expected_outputs=default_value_expected_outputs
        )
        self._refresh_steps()

    def _initialize_steps_as_tuple(self, steps):
        """
        Wrap each step by a :class:`QueueWorker` to  allow data to flow in many pipeline steps at once in parallel.

        :param steps: (name, n_workers, step)
        :type steps: NameNWorkerStepTupleList
        :return: steps as tuple
        :rtype: NamedTupleList
        """
        steps_as_tuple: NamedTupleList = []
        for step in steps:
            queue_worker = self._create_queue_worker(step)
            steps_as_tuple.append((queue_worker.name, queue_worker))

        steps_as_tuple.append(('queue_joiner', QueueJoiner(batch_size=self.batch_size)))

        return steps_as_tuple

    def _create_queue_worker(self, step: QueuedPipelineStepsTuple):
        name, n_workers, additional_worker_arguments, max_queue_size, actual_step = self._get_step_params(step)

        return QueueWorker(
            actual_step,
            n_workers=n_workers,
            use_threading=self.use_threading,
            max_queue_size=max_queue_size,
            additional_worker_arguments=additional_worker_arguments,
            use_savers=self.use_savers
        ).set_name('QueueWorker{}'.format(name))

    def _get_step_params(self, step):
        """
        Return all params necessary to create the QueuedPipeline for the given step.

        :param step: tuple
        :type step: QueuedPipelineStepsTupleList

        :return: return name, n_workers, max_queue_size, actual_step
        :rtype: tuple(str, int, int, BaseStep)
        """
        if isinstance(step, BaseTransformer):
            actual_step = step
            name = step.name
            max_queue_size = self.max_queue_size
            n_workers = self.n_workers_per_step
            additional_arguments = []
        elif len(step) == 2:
            if isinstance(step[0], str):
                name, actual_step = step
                n_workers = self.n_workers_per_step
            else:
                n_workers, actual_step = step
                name = actual_step.name
            max_queue_size = self.max_queue_size
            additional_arguments = []
        elif len(step) == 3:
            name, n_workers, actual_step = step
            max_queue_size = self.max_queue_size
            additional_arguments = []
        elif len(step) == 4:
            if isinstance(step[2], Iterable):
                name, n_workers, additional_arguments, actual_step = step
                max_queue_size = self.max_queue_size
            else:
                name, n_workers, max_queue_size, actual_step = step
                additional_arguments = []
        elif len(step) == 5:
            name, n_workers, additional_arguments, max_queue_size, actual_step = step
        else:
            raise Exception('Invalid Queued Pipeline Steps Shape.')

        return name, n_workers, additional_arguments, max_queue_size, actual_step

    def _will_process(self, data_container: DataContainer, context: ExecutionContext) -> (
    DataContainer, ExecutionContext):
        """
        Setup streaming pipeline before any handler methods.

        :param data_container: data container
        :param context: execution context
        :return:
        """
        self.setup(context=context)
        return data_container, context

    def setup(self, context: ExecutionContext = None) -> 'BaseTransformer':
        """
        Connect the queued workers together so that the data can correctly flow through the pipeline.

        :param context: execution context
        :return: step
        :rtype: BaseStep
        """
        if not self.is_initialized:
            self.connect_queued_pipeline()
        super().setup(context=context)
        return self

    def fit_transform_data_container(self, data_container: DataContainer, context: ExecutionContext) -> (
    'Pipeline', DataContainer):
        """
        Fit transform sequentially if any step is fittable. Otherwise transform in parallel.

        :param data_container: data container
        :type data_container: DataContainer
        :param context: execution context
        :type context: ExecutionContext
        :return:
        """
        all_steps_are_not_fittable = True

        for _, step in self[:-1]:
            if isinstance(step.get_step(), _FittableStep) and not isinstance(step.get_step(), NonFittableMixin):
                all_steps_are_not_fittable = False

        if all_steps_are_not_fittable:
            data_container = self.transform_data_container(data_container, context)
            data_container = self._did_transform(data_container, context)
            return self, data_container

        self.is_invalidated = True

        return super().fit_transform_data_container(data_container, context)

    def transform_data_container(self, data_container: DataContainer, context: ExecutionContext) -> DataContainer:
        """
        Transform data container

        :param data_container: data container to transform.
        :type data_container: DataContainer
        :param context: execution context
        :type context: ExecutionContext
        :return: data container
        """
        data_container_batches = data_container.minibatches(
            batch_size=self.batch_size,
            include_incomplete_batch=self.include_incomplete_batch,
            default_value_data_inputs=self.default_value_data_inputs,
            default_value_expected_outputs=self.default_value_expected_outputs
        )

        n_batches = self.get_n_batches(data_container)
        self[-1].set_n_batches(n_batches)

        for name, step in self[:-1]:
            step.start(context)

        batch_index = 0
        for data_container_batch in data_container_batches:
            self.send_batch_to_queued_pipeline(batch_index=batch_index, data_container=data_container_batch)
            batch_index += 1

        data_container = self[-1].join(original_data_container=data_container)
        return data_container

    def _did_transform(self, data_container: DataContainer, context: ExecutionContext) -> DataContainer:
        """
        Stop all of the workers after transform. Also, join the data using self.data_joiner.

        :param data_container: data container
        :type data_container: DataContainer
        :param context: execution context
        :type context: ExecutionContext
        :return: data container
        :rtype: DataContainer
        """
        for name, step in self[:-1]:
            step.stop()

        return self.data_joiner.handle_transform(data_container, context)

    @abstractmethod
    def get_n_batches(self, data_container) -> int:
        """
        Get the total number of batches that the queue joiner is supposed to receive.

        :param data_container: data container to transform
        :type data_container: DataContainer
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def connect_queued_pipeline(self):
        """
        Connect all the queued workers together so that the data can flow through each step.

        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def send_batch_to_queued_pipeline(self, batch_index: int, data_container: DataContainer):
        """
        Send batches to queued pipeline. It is blocking if there is no more space available in the multiprocessing queues.
        Workers might return batches in a different order, but the queue joiner will reorder them at the end.
        The queue joiner will use the summary ids to reorder all of the received batches.

        :param batch_index: batch index
        :param data_container: data container batch
        :return:
        """
        raise NotImplementedError()


class SequentialQueuedPipeline(BaseQueuedPipeline):
    """
    Using :class:`QueueWorker`, run all steps sequentially even if they are in separate processes or threads.

    .. seealso::
        :func:`~neuraxle.data_container.DataContainer.minibatches`,
        :class:`~neuraxle.data_container.DataContainer.AbsentValuesNullObject`,
        :class:`QueueWorker`,
        :class:`BaseQueuedPipeline`,
        :class:`ParallelQueuedPipeline`,
        :class:`QueueJoiner`,
        :class:`Observer`,
        :class:`Observable`
    """

    def get_n_batches(self, data_container) -> int:
        """
        Get the number of batches to process.

        :param data_container: data container to transform
        :return: number of batches
        """
        return data_container.get_n_batches(
            batch_size=self.batch_size,
            include_incomplete_batch=self.include_incomplete_batch
        )

    def connect_queued_pipeline(self):
        """
        Sequentially connect of the queued workers.

        :return:
        """
        for i, (name, step) in enumerate(self[1:]):
            self[i].subscribe(step)

    def send_batch_to_queued_pipeline(self, batch_index: int, data_container: DataContainer):
        """
        Send batches to process to the first queued worker.

        :param batch_index: batch index
        :param data_container: data container batch
        :return:
        """
        data_container = data_container.set_summary_id(data_container.hash_summary())
        self[-1].summary_ids.append(data_container.summary_id)
        self[0].put(data_container)


class ParallelQueuedFeatureUnion(BaseQueuedPipeline):
    """
    Using :class:`QueueWorker`, run all steps in parallel using QueueWorkers.

    .. seealso::
        :class:`QueueWorker`,
        :class:`BaseQueuedPipeline`,
        :class:`SequentialQueuedPipeline`,
        :class:`QueueJoiner`,
        :class:`Observer`,
        :class:`Observable`
    """

    def get_n_batches(self, data_container):
        """
        Get the number of batches to process by the queue joiner.

        :return:
        """
        return data_container.get_n_batches(self.batch_size) * (len(self) - 1)

    def connect_queued_pipeline(self):
        """
        Connect the queue joiner to all of the queued workers to process data in parallel.

        :return:
        """
        for name, step in self[:-1]:
            step.subscribe(self[-1])

    def send_batch_to_queued_pipeline(self, batch_index: int, data_container: DataContainer):
        """
        Send batches to process to all of the queued workers.

        :param batch_index: batch index
        :param data_container: data container batch
        :return:
        """
        for name, step in self[:-1]:
            data_container = data_container.set_summary_id(data_container.hash_summary())
            self[-1].summary_ids.append(data_container.summary_id)
            step.put(data_container)


class QueueJoiner(ObservableQueueMixin, Joiner):
    """
    Observe the results of the queue worker of type :class:`QueueWorker`.
    Synchronize all of the workers together.

    .. seealso::
        :class:`QueuedPipeline`,
        :class:`Observer`,
        :class:`ListDataContainer`,
        :class:`DataContainer`
    """

    def __init__(self, batch_size, n_batches=None):
        self.n_batches_left_to_do = n_batches
        self.summary_ids = []
        self.result = {}
        Joiner.__init__(self, batch_size=batch_size)
        ObservableQueueMixin.__init__(self, Queue())

    def teardown(self) -> 'BaseTransformer':
        """
        Properly clean queue, summary ids, and results during teardown.

        :return: teardowned self
        """
        ObservableQueueMixin.teardown(self)
        Joiner.teardown(self)
        self.summary_ids = []
        self.result = {}
        return self

    def set_n_batches(self, n_batches):
        self.n_batches_left_to_do = n_batches

    def join(self, original_data_container: DataContainer) -> DataContainer:
        """
        Return the accumulated results received by the on next method of this observer.

        :return: transformed data container
        :rtype: DataContainer
        """
        while self.n_batches_left_to_do > 0:
            task: QueuedPipelineTask = self.queue.get()
            self.n_batches_left_to_do -= 1
            step_name = task.step_name

            if step_name not in self.result:
                if not isinstance(task.data_container, DataContainer):
                    summary_id = None
                else:
                    summary_id = task.data_container.summary_id

                self.result[step_name] = ListDataContainer(
                    current_ids=[],
                    data_inputs=[],
                    expected_outputs=[],
                    summary_id=summary_id
                )

            self.result[step_name].append_data_container_in_data_inputs(task.data_container)

        data_containers = self._join_all_step_results()
        self.result = {}
        return original_data_container.set_data_inputs(data_containers)

    def _join_all_step_results(self):
        """
        Concatenate all resulting data containers together.

        :return:
        """
        results = []
        for step_name, data_containers in self.result.items():
            self._raise_exception_throwned_by_workers_if_needed(data_containers)
            step_results = self._join_step_results(data_containers)
            results.append(step_results)

        return results

    def _raise_exception_throwned_by_workers_if_needed(self, data_containers):
        for dc in data_containers.data_inputs:
            if isinstance(dc, Exception):
                # an exception has been throwned by the worker so reraise it here!
                exception = dc
                raise exception

    def _join_step_results(self, data_containers):
        # reorder results by summary id
        data_containers.data_inputs.sort(key=lambda dc: self.summary_ids.index(dc.summary_id))

        step_results = ListDataContainer.empty()
        for data_container in data_containers.data_inputs:
            data_container = data_container.set_summary_id(data_containers.data_inputs[-1].summary_id)
            step_results.concat(data_container)

        return step_results
