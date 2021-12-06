"""test_scheduler module

This module exports functions for testing the functionality of the scheduler module

The following functions are not testable due to their nature:
 - create_repeating_wrapper
 - queue_task
 - cancel_task_by_name

Queue_task is technically testable but it would not be an isolated test,
since it relies on run_scheduler.
The same applies to cancel_task_by_name as it uses cancel_task
"""
import sched
import time

import covid19dashboard.scheduler as scheduler

def reset_test_environment():
    """
    This function resets the test environment so all tests are isolated.]
    It sets scheduler to be a fresh scheduler and clears the update list.
    """
    # This isn't best practice but I don't know any other way of doing it
    scheduler.scheduler = sched.scheduler(time.time, time.sleep)

    scheduler.scheduled_updates = []

def test_run_scheduler():
    """
    This ensures the run_scheduler function calls the scheduled function
    """
    reset_test_environment()

    function_called = False
    def test_function():
        nonlocal function_called
        function_called = True

    scheduler.scheduler.enterabs(0, 1, test_function)

    scheduler.run_scheduler()

    assert function_called is True

def test_create_wrapper():
    """
    This test ensures that the create wrapper function correctly
    removes the event from the array after the function has been run
    """
    reset_test_environment()

    function_called = False
    def test_function():
        nonlocal function_called

        function_called = True

    event = {
        "name": "Example Event"
    }

    scheduler.scheduled_updates.append(event)

    wrapper_function = scheduler.create_wrapper(test_function, event)

    wrapper_function()

    assert function_called is True
    assert len(scheduler.scheduled_updates) == 0

def test_cancel_task():
    """
    This test ensures that cancel_task will remove an event from the scheduled_updates list.
    """
    reset_test_environment()

    event_id = scheduler.scheduler.enter(0, 1, print)

    event = {
        "unique_identifier": 123456,
        "event": event_id
    }

    scheduler.scheduled_updates = [
        event
    ]

    result = scheduler.cancel_task(event)

    assert result is True

def test_cancel_task_failure():
    """
    This test ensures that cancel_task will return False if a ValueError is thrown
    """
    reset_test_environment()

    result = scheduler.cancel_task({
        "event": None
    })

    assert result is False
