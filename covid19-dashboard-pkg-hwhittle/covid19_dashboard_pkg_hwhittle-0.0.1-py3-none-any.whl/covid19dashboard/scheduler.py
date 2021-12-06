"""scheduler

A module for scheduling tasks to be run at a future time.

Queuing a task will start the scheduler

This module exports the following functions
 * queue_task(name, function, update_time, absolute=False, repeat=False)
    -> Queues a task to the scheduler with relative/absolute timing

 * cancel_task(event)
    -> Cancels a task from being run by the scheduler

 * cancel_task_by_name(event_name)
    -> Cancels a task from being run by the scheduler based on the name of the task

 * run_scheduler()
    -> Runs the tasks in the scheduler.

It also consists of the following internal functions
 * create_wrapper(function, event)
    -> Creates a wrapper function around the given function,
        which removes it from the scheduled_update array

 * create_repeating_wrapper(function, event)
    -> Creates a wrapper function around the given function,
        which reschedules the event.

"""

import sched
import time
from types import FunctionType
from typing import Dict

from .logger import log_debug, log_error, log_info

scheduler = sched.scheduler(time.time, time.sleep)

"""
An array of scheduled updates : list[Event]
"""
scheduled_updates = []

def run_scheduler() -> None:
    """
    Runs the tasks in the scheduler.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    log_debug("Running scheduler.")
    try:
        scheduler.run(blocking=False)
    except Exception as err:
        log_error("Unexpected error whilst running scheduled tasks.", err)

def create_wrapper(function: FunctionType, event: Dict) -> FunctionType:
    """
    An internal helper function to remove the update from scheduled_updates

    Parameters
    ----------
    function : function
        The function to schedule

    event : Event dictionary
        A dictionary containing event information
        It's used to remove the event from scheduled_updates

    Returns
    -------
    function
        A function which acts as a wrapper for the original function.
        When called it calls the original function and then removes the event frm scheduled_updates.
    """
    def wrapped_function() -> None:
        log_debug(f"Running update {event['name']}")
        try:
            function()
        except Exception as err:
            log_error("Unexpected error whilst running scheduled tasks.", err)

        scheduled_updates.remove(event)

    return wrapped_function


def create_repeating_wrapper(function: FunctionType, event: Dict) -> FunctionType:
    """
    An internal helper function to make a function which reschedules itself.
    It also removes the event from the scheduled_updates array if it fails to run.

    Parameters
    ----------
    function : function
        The function to schedule

    event : Event dictionary
        A dictionary containing event information
        It should contain
            - event : Event id
            - time : number

    Returns
    -------
    function
        A function which acts as a wrapper for the original function.
        When called it calls the original function and then reschedules itself.

    """
    def wrapped_function() -> None:
        log_debug(f"Running repeated update {event['name']}")
        try:
            function()
        except Exception as err:
            scheduled_updates.remove(event)
            log_error("Unexpected error whilst running scheduled tasks.", err)

        # schedule to return the function again
        event["event"] = scheduler.enterabs(event["time"] + 24 * 60 * 60, 1, wrapped_function)
        event["time"] += 24 * 60 * 60

    return wrapped_function

def queue_task(name: str, function: FunctionType, update_time: float, repeat=False) -> Dict:
    """
    Queues a task in the scheduler with a relative time delay and
    attempts to start the scheduler if it is not already running.

    Parameters
    ----------
    function : function
        The function to run after the given delay

    update_time : number
        The absolute time that the function will run at
            Timing is based on time.time, for 3 seconds in the future do time.time() + 3

    repeat : bool
        Whether the event should repeat

    Returns
    -------
    Event : Event dictionary
        A dictionary representing the event
            - name : str -> name of the event
            - time : number -> time of the event (in seconds or absolute time)
            - repeating : bool -> whether the event repeats
            - event : Event -> the event id returned by the sched module
    """

    log_debug(f"Scheduler queue task called for update '{name}'")

    event = {
        "name": name,
        "time": update_time,
        "repeating": repeat,
        "event": None
    }

    if repeat:
        wrapper = create_repeating_wrapper(function, event)
    else:
        wrapper = create_wrapper(function, event)

    event["event"] = scheduler.enterabs(
        update_time,
        1,
        wrapper
    )

    scheduled_updates.append(event)

    run_scheduler()

    return event

def cancel_task(event: Dict) -> bool:
    """
    Cancels an event from being run by the scheduler and removes it from the scheduled_updates array

    Parameters
    ----------
    event : Event dictionary
        The event object returned by queue_task

    Returns
    -------
    bool
        Whether or not the event was cancelled
            -> False usually indicates that the event did not exist or had already been run
    """
    log_debug("Cancel task called")
    try:
        scheduler.cancel(event["event"])
        scheduled_updates.remove(event)
        return True
    except ValueError:
        return False

def cancel_task_by_name(event_name: str) -> bool:
    """
    Cancels all events in the queue with the given name.

    Parameters
    ----------
    event_name : str
        The name of the event to cancel

    Returns
    -------
    bool
        Whether the function cancelled any events
    """
    log_debug(f"Cancel task with name '{event_name}'")

    # We loop backwards here since we are removing items from
    # the array. If we were to loop forwards we would skip values.

    cancelled = False
    for update in reversed(scheduled_updates):
        if update['name'] == event_name:
            result = cancel_task(update)
            if not cancelled and result:
                cancelled = True

    return cancelled
