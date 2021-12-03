"""
Tools for scheduling sequences of actions to execute at prescribed times.
"""
import os
import re
import threading
import time
import logging
import bisect
import datetime

from typing import List, Union, Iterable, Callable

from .timepoint import ActionTimePoint
from .action import Action, ConfiguredAction
from .sequencing import ConfiguredSequence
from .mixin import InstanceRegistry, DumpableState

logger = logging.getLogger(__name__)


class SamplingScheduler(InstanceRegistry, DumpableState):
    # pause time between cycle checks
    CYCLE_TIME = 0.5

    # default state for whether to wait for completion of previous trigger if busy
    WAIT_IF_BUSY = True

    UUID_PREFIX = 'sched-'

    def __init__(self,
                 *actions: Union[str, callable, Action, ConfiguredAction],
                 time_deltas: List[float] = None,
                 sequence_name: str = None,
                 ):
        """
        Scheduler for sequences of configured actions. Actions are stored in a configured sequence (sequence attribute).

        :param time_deltas: a list of time deltas to initialize the sequence with (passed directly to
            insert_time_point_list)
        :param actions: callable action or the name of a callable action previously defined as a SchedulerAction
        :param sequence_name: convenience reference name for the current experiment
        """
        InstanceRegistry.__init__(self)
        logger.debug(f'creating scheduler {self._uuid[:5]}')
        self.logger = logger.getChild(f'{self.__class__.__name__} {self._uuid[:5]}')

        # event control of killswitch for stop command
        self._killswitch = threading.Event()

        # create sequence
        self.sequence: ConfiguredSequence = ConfiguredSequence(
            *actions,
            sequence_name=sequence_name,
        )

        # time stamp for Scheduler creation
        self.created = time.time()
        # start time for auto-stepping
        self._start_time: float = None
        # thread for the sequence
        self._sequence_thread: threading.Thread = threading.Thread(
            target=self._sequence_loop,
            name=f'{self.__class__.__name__} sequence thread',
            daemon=True,
        )
        self._sequence_pause: threading.Event = threading.Event()
        # dictionary for time points
        self._time_points: List[ActionTimePoint] = []

        if time_deltas is not None:
            self.insert_time_point_list(*time_deltas)

        # store experiment name for reference
        self.sequence_name: str = sequence_name

        # todo implement databasing
        #   - add method which reinstantiates from database
        # todo have the experiment be named based on the sample number in the sequence
        # todo implement ability to change action associated with time points
        # todo generalize action parsing
        # todo add run_forever method
        # todo add attribute that defines default behaviour when all timepoints are completed (auto kill/cleanup)
        # todo add restart method (restarts the whole thing)

    def __repr__(self):
        return (
            f'{self.__class__.__name__} {self._uuid[:5]} '
            f'{" STARTED" if self.started is True else ""} '
            f'{" TERMINATED" if self.terminated else ""}'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def uuid(self) -> str:
        """uuid4 for the scheduler"""
        return self.UUID_PREFIX + self._uuid

    @property
    def started(self) -> bool:
        """whether the sequence has been started"""
        return self._sequence_thread.is_alive()

    @property
    def terminated(self) -> bool:
        """whether the sequence has been terminated"""
        return self._killswitch.is_set()

    @property
    def current_time(self) -> float:
        """the current time since starting the scheduler"""
        if self._start_time is not None:
            return time.time() - self._start_time

    @property
    def time_points(self) -> List[ActionTimePoint]:
        """list of time points for the sequence"""
        return self._time_points

    @property
    def total_time_points(self) -> int:
        """total number of time points associated with the scheduler instance"""
        return len(self.time_points)

    @property
    def triggered_time_points(self) -> int:
        """number of triggered time points"""
        return len([tp for tp in self.time_points if tp.triggered is True])

    @property
    def remaining_time_points(self) -> int:
        """number of time points remaining to be sampled"""
        return len([tp for tp in self.time_points if tp.triggered is False])

    @property
    def completed_time_points(self) -> int:
        """number of time points which have been completed"""
        return len([tp for tp in self.time_points if tp.status_code == 3 or tp.status_code < 0])

    @property
    def uncompleted_time_points(self) -> int:
        """number of time points which have not been completed"""
        return len([tp for tp in self.time_points if 0 < tp.status_code < 3])

    @property
    def next_time_point(self) -> Union[ActionTimePoint, None]:
        """The next time point for triggering"""
        # todo filter out non-action points
        # filter to untriggered time points
        unsampled = [tp for tp in self._time_points if tp.triggered is False]
        if len(unsampled) == 0:
            return
        # return first up
        return min(
            unsampled,
            key=lambda x: x.time_delta
        )

    @property
    def estimated_time_until_next_point(self) -> float:
        """estimated time in seconds until next time point"""
        raise NotImplementedError('not yet implemented')
        return  # todo

    @property
    def last_triggered_time_point(self) -> ActionTimePoint:
        """The last time point which was triggered"""
        # list of triggered time points
        triggered = [tp for tp in self.time_points if tp.triggered is True]
        # if there are triggered points, return most recent one
        if len(triggered) > 0:
            return triggered[-1]

    @property
    def busy(self) -> bool:
        """whether there are any time points currently executing"""
        last_point = self.last_triggered_time_point
        if last_point is not None and last_point.in_progress is True:
            return True
        return False

    @classmethod
    def get_newest_instance(cls) -> "SamplingScheduler":
        """Gets the newest instance of the sampling scheduler"""
        try:
            return cls.class_registry[-1]
        except IndexError:
            raise IndexError(f'The {cls.__name__} has no instances. ')

    def _determine_actions(self,
                           additional_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                           specified_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                           ) -> ConfiguredSequence:
        """
        Determines the actions for a time point. If no actions are provided, the default actions of the
        instance are used. If additional actions are provided, those actions will be performed in addition to the
        default actions (actions will be performed in order after the default actions are complete). If
        specified_actions are provided, only those actions will be performed.

        :param additional_actions: actions to run in addition to the default actions of the scheduler instance.
            These actions will be run after the default actions.
        :param specified_actions: actions to run instead of the default actions of the instance
        :return: actions for a time point
        """
        # establish list of actions
        if additional_actions is not None:
            actions = self.sequence.duplicate_configuration()
            actions.action_sequence.extend(additional_actions)
        elif specified_actions is not None:
            actions = ConfiguredSequence(*specified_actions)
        else:
            actions = self.sequence.duplicate_configuration()
        return actions

    def trigger(self,
                additional_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                specified_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                wait: bool = None,
                timepoint_name: str = None,
                **action_kwargs
                ) -> ActionTimePoint:
        """
        Manually triggers the sequence with the actions provided. If no actions are provided, the default actions of the
        instance are used. If additional actions are provided, those actions will be performed in addition to the
        default actions (actions will be performed in order after the default actions are complete). If
        specified_actions are provided, only those actions will be performed.

        :param additional_actions: actions to run in addition to the default actions of the scheduler instance.
            These actions will be run after the default actions.
        :param specified_actions: actions to run instead of the default actions of the instance
        :param wait: whether to wait for completion of the actions before returning
        :param timepoint_name: optional name for the timepoint
        :param action_kwargs: keyword arguments for the actions. Keyword arguments will be passed through to their
            respective methods. See ActionTimePoint.trigger for details on kwarg handling
        :return: created ActionTimePoint instance
        """
        if self.busy is True:
            self.logger.warning(
                'trigger was called but the previous time point is still being executed. waiting...'
            )
            self.wait_for_time_point_completion()

        action_sequence = self._determine_actions(
            additional_actions=additional_actions,
            specified_actions=specified_actions,
        )

        # create a manual time point
        manual_time_point = ActionTimePoint(
            time.time() - self._start_time if self._start_time is not None else 0.,
            configuration=action_sequence,
            name=timepoint_name,
        )
        # store start time if set
        if self._start_time is not None:
            manual_time_point.sequence_time_started = self._start_time
        # insert time point into list
        bisect.insort(
            self._time_points,
            manual_time_point
        )
        self.apply_default_timepoint_names()
        manual_time_point.trigger(
            wait=wait,
            **action_kwargs,
        )
        return manual_time_point

    def _sequence_loop(self):
        """
        Sequence loop that watches time points and triggers actions at the appropriate times. This loop retrieves the
        next time point of the instance and triggers the sequence of actions associated with the instance.

        If an action is already executing, this loop will block until that previous timepoint is completed before
        triggering the next time point up.
        """
        while True:
            # if the pause flag has been set
            if self._sequence_pause.is_set() is False:
                # todo consider how to handle missed time points
                #   - continue loop and note if missed?
                #   - rapid-fire sample to catch up?
                self.logger.info(f'sequence is paused, waiting for start_sequence call...')
                self._sequence_pause.wait()
                self.logger.info(f'sequence has been resumed')
            if self._killswitch.is_set():  # if killswitch is thrown, break out of thread
                # todo consider a timeout argument
                while self.busy is True:  # waits for current actions to be complete (if active)
                    time.sleep(0.1)
                # todo perform cleanup actions (if any)
                break
            # get next time point
            next_timepoint = self.next_time_point
            # if there is no next time point, break out
            if next_timepoint is None:
                self.logger.info('all time points have been completed, sequence is pausing pending more time points')
                self._sequence_pause.clear()
            # if the timepoint has happened, trigger and store time
            elif time.time() >= self._start_time + next_timepoint.time_delta:
                self.logger.info(f'{next_timepoint} reached')
                if self.busy is True:
                    self.logger.warning(
                        'the next time point has been reached but the previous time point '
                        'is still being executed. waiting...'
                    )
                    self.wait_for_time_point_completion()
                next_timepoint.sequence_time_started = self._start_time
                next_timepoint.trigger()
            # otherwise wait predefined time and continue loop
            else:
                time.sleep(self.CYCLE_TIME)

    def wait_for_time_point_completion(self):
        """If a time point is being executed, this method will wait for it to be complete"""
        if self.busy is True:
            self.logger.info('waiting for completion of previous trigger')
            while self.busy is True:
                time.sleep(0.5)

    def apply_default_timepoint_names(self, prefix: str = 'Time Point #'):
        """
        Applies default timepoint naming across the timepoint list, ensuring consistent naming order.

        :param prefix: prefix to use for naming
        """
        name_re = re.compile(f'^{prefix}')
        counter = 1
        for tp in self._time_points:
            # if no name is defined or the pattern matches the prefix, apply default naming
            #   pattern matching is implemented to not overwrite custom-defined names
            if tp.name is None or name_re.search(tp.name):
                tp.name = f'{prefix}{counter}'
                counter += 1

    def insert_time_point(self,
                          time_delta: float = None,
                          position: int = -1,
                          relative_to: str = 'start',
                          shift_subsequent: bool = True,
                          number_of_points: int = 1,
                          timepoint_name: str = None,
                          additional_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                          specified_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                          ):
        """
        Inserts a time point into the list of time points.

        :param time_delta: time delta in seconds from the reference (relative_to)
        :param position: position in the time point list to insert the new time point (default is the end of of the list)
        :param relative_to: whether the specified time delta should be relative to the sequence time ('start') or
            the time point previous to the insertion point ('previous')
        :param shift_subsequent: whether to shift subsequent time points in the time point list by the time delta
        :param number_of_points: number of points with these specification to add
        :param timepoint_name: optional name for inserted time point. If multiple points are specified, a counter will
            be applied.
        """
        action_sequence = self._determine_actions(
            additional_actions=additional_actions,
            specified_actions=specified_actions,
        )

        # todo adjust insert_time_point to differentiate between sampling and standard time points
        # if end of list position is desired
        if position == -1:
            position = len(self._time_points)

        # determine offset based on specification
        if relative_to.lower() == 'previous':
            if len(self._time_points) == 0:  # special case where there are no previous points
                delta_offset = 0.
            elif position == 0:  # special case at the beginning of the list
                delta_offset = 0.
            else:
                delta_offset = self._time_points[position - 1].time_delta
        elif relative_to.lower() == 'start':
            delta_offset = 0.
        else:
            raise ValueError(f'The relative_to value "{relative_to}" is invalid. Choose from "start" or "previous".')

        # add time points
        self.logger.debug(f'Adding {number_of_points} timepoints at {time_delta} s spacing in position {position}.')
        for i in range(number_of_points):
            delta = (i + 1) * time_delta + delta_offset
            # create an incremented name if a name was specified
            tp_name = f'{timepoint_name}{f"#{i + 1}" if number_of_points > 1 else ""}' if timepoint_name else None
            bisect.insort(
                self._time_points,
                ActionTimePoint(
                    delta,
                    configuration=action_sequence,
                    name=tp_name,
                )
            )

        # if shifting of subsequent timepoints is desired
        if shift_subsequent is True:
            for subsequent_timepoint in self._time_points[i + 1 + position:]:
                subsequent_timepoint.time_delta += (i + 1) * time_delta
        self.apply_default_timepoint_names()
        # if there the thread is alive and paused (pending more time points), clear flag to resume
        if self._sequence_thread.is_alive() is True and self._sequence_pause.is_set() is False:
            self._sequence_pause.set()

    def insert_time_point_list(self,
                               *time_deltas: float,
                               position: int = -1,
                               relative_to: str = 'previous',
                               additional_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                               specified_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                               ):
        """
        Inserts a list of time points into the current list of time points.

        :param time_deltas: list of time deltas (seconds)
        :param position: position in the current list to insert the incoming time points
        :param relative_to: whether the specified time delta should be relative to the sequence time ('start') or
            the time point previous to the insertion point ('previous'; default)
        """
        if position == -1:
            position = len(self._time_points)
        for ind, time_delta in enumerate(time_deltas):
            self.insert_time_point(
                time_delta=time_delta,
                position=position + ind,
                relative_to=relative_to,
                additional_actions=additional_actions,
                specified_actions=specified_actions,
            )

    def insert_time_point_list_pairs(self,
                                     *num_delta_pairs,
                                     position: int = -1,
                                     relative_to: str = 'previous',
                                     additional_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                                     specified_actions: Iterable[Union[str, callable, ActionTimePoint]] = None,
                                     ):
        """
        Inserts a list of time points in number-of-points/time-delta form.

        e.g. 3, 10 will result in 3 time points with 10 second spacing. 3, 10, 5, 20 will results in 3 time points
        with 10 second spacing followed by 5 time points with 20 second spacing.

        Pairs may also be provided in number/time-delta tuples. e.g. (3, 10), (5, 20)

        :param num_delta_pairs: pairs of arguments in (number-of-points, time_delta) form
        :param position: position in the current list to insert the incoming time points
        :param relative_to: whether the specified time delta should be relative to the sequence time ('start') or
            the time point previous to the insertion point ('previous'; default)
        """
        if type(num_delta_pairs[0]) in [tuple, list]:
            pass
        elif len(num_delta_pairs) % 2 == 0:
            num_delta_pairs = [num_delta_pairs[i:i + 2] for i in range(0, len(num_delta_pairs), 2)]
        else:
            raise ValueError('The arguments for this method are expected to be either a tuple of num/time_delta pairs '
                             'or a list of com')
        expanded = []
        for num, time_delta in num_delta_pairs:
            expanded.extend(
                [time_delta] * num
                # [time_delta * (i + 1) for i in range(num)]
            )
        # todo fix functionality for adding points relative to the start
        #   current functionality adds n times the same time delta relative to the start
        self.insert_time_point_list(
            *expanded,
            position=position,
            relative_to=relative_to,
            additional_actions=additional_actions,
            specified_actions=specified_actions,
        )

    def start_sequence(self):
        """
        Starts the sequence loop and triggers time points as specified
        """
        # set the GO flag
        self._sequence_pause.set()
        # if thread has not been started, store start time and start thread
        if self._sequence_thread.is_alive() is False:
            self.logger.info('starting sequence thread')
            self._start_time = time.time()
            if any([tp.triggered for tp in self.time_points]):  # if any have already been triggered
                for tp in self.time_points:
                    if tp.triggered:
                        # todo figure out a better catch for time=0
                        # store the start time and calculate the effective time delta
                        tp.sequence_time_started = self._start_time
                        tp.time_delta = tp.relative_start_times[
                            min(tp.relative_start_times, key=lambda x: tp.relative_start_times[x])
                        ]
            self._sequence_thread.start()

    @property
    def paused(self) -> bool:
        """whether the sequence is paused"""
        return not self._sequence_pause.is_set()

    def pause_sequence(self):
        """Pauses the sequence (actions will not be automatically triggered until resumed)"""
        self._sequence_pause.clear()

    def kill_sequence(self):
        """This method will kill the sequence and perform cleanup. You will not be able to restart the thread
        after calling this method"""
        self._killswitch.set()  # activates killswitch
        self._sequence_pause.clear()  # clear pause if set (breaks out of wait section in loop)

    def join(self):
        """waits for defined time points in the scheduler to finish"""
        while self.remaining_time_points != 0:
            time.sleep(self.CYCLE_TIME)
        # if the last triggered time point is not complete, wait for completion
        last_timepoint = self.last_triggered_time_point
        if last_timepoint is not None and last_timepoint.complete is False:
            last_timepoint.wait_for_completion()

    def as_dict(self) -> dict:
        """Returns a key: value representation of the instance"""
        out = {
            'uuid': self.uuid,
            'sequence_name': self.sequence_name,
            'instance_actions': [action.name for action in self.sequence.action_sequence],
            'started': self.started,
            'created': self.created,
            'num_time_points': self.total_time_points,  # todo deprecate
            'total_time_points': self.total_time_points,
            'sampled_time_points': self.triggered_time_points,
            'remaining_time_points': self.remaining_time_points,
            'completed_time_points': self.completed_time_points,
            'uncompleted_time_points': self.uncompleted_time_points,
        }
        if self.next_time_point is not None:
            out['next_time_point'] = self.next_time_point.time_delta
        if self._killswitch.is_set() is True:
            out['terminated'] = True
        return out

    def get_time_point_return(self,
                              key: str = None
                              ) -> dict:
        """
        Retrieves the returned values of the specified action time point.

        :param key: identifier key for the desired ActionTimePoint instance. If not specified, the last triggered
            time point will be retrieved.
        :return: method returns
        """
        if key is None:
            tp = self.last_triggered_time_point
        else:
            tp = ActionTimePoint.class_instance_by_id(key)
        return tp.action_returns

    def visualize_timepoints(self):
        raise NotImplementedError()
        pass  # todo plot a timeline of points for visualization

    def write_timepoints_to_csv(self,
                                file_name: str = None,
                                overwrite: bool = True,
                                ):
        """
        Writes the time point data to the specified csv file. If no filename is passed, the time points will be saved to
        "YYYY-MM-DD scheduler output.csv".

        :param file_name: file name to write to
        :param overwrite: whether to overwrite the filename if it already exists
        """
        # todo update to support new timepoint structure
        raise NotImplementedError()
        if file_name is None:
            file_name = f'{str(datetime.datetime.fromtimestamp(self._start_time).date())} scheduler output'
            if os.path.isfile(f'{file_name}.csv') and overwrite is False:
                i = 1
                while os.path.isfile(f'{file_name} - {i}.csv'):
                    i += 1
                file_name = f'{file_name} - {i}.csv'
            else:
                file_name += '.csv'
        self.logger.info(f'Writing scheduler data to {file_name}')
        with open(file_name, 'wt') as f:
            f.write(
                'Target Time (s),'
                'Sampled At (s),'
                'Timestamp,'
                # 'Metadata,'  # todo save this to file
                '\n'
            )
            if self.started is True:
                f.write(f'0.,0.,{str(datetime.datetime.fromtimestamp(self._start_time))}\n')
            # todo sort through time points and save negative timepoints before zero
            for tp in self.time_points:
                f.write(f'{tp.time_delta},')
                if tp.sampled_time is not None:
                    f.write(
                        f'{tp.sampled_time_relative if tp.sequence_time_started is not None else ""},'
                        f'{str(datetime.datetime.fromtimestamp(tp.sampled_time))},'
                    )
                f.write('\n')


class ExecuteOnTimePoints(ConfiguredAction):
    def __init__(self,
                 action: Callable,
                 *timepoints,
                 configuration_name: str = None,
                 enabled: bool = True,
                 **kwargs,
                 ):
        """
        Class for executing an action on the specified timepoints. When the action is triggered, the time point list
        of the instance will be checked against the currently executing timepoint name. If the condition matches,
        the action will be executed.

        :param action: action to execute when triggered and the conditions are met
        :param timepoints: time point numbers to execute on
        :param configuration_name: name for the configuration
        :param enabled: whether the action should be enabled (use this to disable any execution)
        :param kwargs: kwarg pass through to ConfiguredAction
        """
        ConfiguredAction.__init__(
            self,
            action=action,
            configuration_name=configuration_name,
            **kwargs,
        )
        self.timepoints: List[int] = list(timepoints)
        self.enabled: bool = enabled

    @property
    def regex(self):
        """regex pattern for matching timepoint names"""
        value_pattern = "|".join([str(val) for val in self.timepoints])
        return re.compile(
            f'Time Point #({value_pattern})$'
        )

    def evaluate_condition(self) -> bool:
        """Performs the logic check to determine whether the action should be executed"""
        # todo make this check specific to the parent timepoint
        #   currently if any running timepoint name matches any timepoint numbers in the the instance,
        #   True will be returned
        if self.enabled is False:
            logger.debug(f'{self.name} disabled, bypassing logic checks')
            return False
        timepoints = [
            timepoint
            for sched in SamplingScheduler.class_registry
            for timepoint in sched.time_points
            if timepoint.status_code == 2
        ]
        if len(timepoints) == 0:
            logger.debug(f'{self.name} no active timepoints, bypassing')
            return False  # todo consider what to do in this case
        tp = timepoints[0]
        if self.regex.search(tp.name):
            logger.debug(f'{self.name} timepoint number match, performing action')
            return True
        logger.debug(f'{self.name} no conditions met, bypassing')
        return False
