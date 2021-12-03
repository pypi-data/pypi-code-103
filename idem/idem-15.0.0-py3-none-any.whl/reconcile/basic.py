import asyncio


# Reconciliation loop stops after MAX_RERUNS_WO_CHANGE reruns without change.
# This is to make sure we do not retry forever on failures that cannot be fixed by
# reconciliation.
# TODO: For now there is no way to differentiate between "failures" that can be fixed
# by reconciliation (re-runs) or not. Plugins will be enhanced to return 'pending'
# result for failures that can be fixed by re-conciliation.
MAX_RERUNS_WO_CHANGE = 3
# Sleep time in seconds between re-runs
RECONCILE_WAIT = 3


async def loop(
    hub,
    name,
    sls_sources,
    render,
    runtime,
    cache_dir,
    sls,
    test,
    acct_file,
    acct_key,
    acct_profile,
):
    """
    This loop attempts to apply states.
    This function returns once all the states are successful or after MAX_RERUNS_WO_CHANGE, whichever occur first.
    The sleep time between each attempt will be determined by a plugin and might change between each iterations.
    Reconciliation is required if the state has pending changes (present) or result that is not 'True'.
    TODO: this is till the plugins implement a pending state and other failure values that should
    TODO: not be re-conciliated
    :param hub:
    :param name:
    :param sls_sources:
    :param render:
    :param runtime:
    :param cache_dir:
    :param sls:
    :param test:
    :param acct_file:
    :param acct_key:
    :param acct_profile:
    :return: dictionary { "re_runs_count": <number of re-runs that occurred>,
                "require_re_run": <True/False whether the last run require more reconciliation> }
    """
    last_run = hub.idem.RUNS[name]["running"]
    if has_passed(last_run):
        return {"re_runs_count": 0, "require_re_run": False}

    # TODO for now reconcile wait hard coded
    # will make it per hub and implemented by plugin to support
    # exponential backoff
    sleep_time_sec = getattr(hub, "RECONCILE_WAIT", RECONCILE_WAIT)
    if not sleep_time_sec:
        hub.log.debug(
            f"Reconciliation wait time is not defined. Skipping reconciliation."
        )
        print(f"Reconciliation wait time is not defined. Skipping reconciliation.")
        return {"re_runs_count": 0, "require_re_run": True}

    count = 0
    count_wo_change = 0
    while count_wo_change < MAX_RERUNS_WO_CHANGE:
        hub.log.debug(f"Sleeping {sleep_time_sec} seconds for {name}")
        print(f"Sleeping {sleep_time_sec} seconds for {name}")
        await asyncio.sleep(sleep_time_sec)

        count = count + 1
        hub.log.debug(f"Retry {count} for {name}")
        print(f"Retry {count} for {name}")
        await hub.idem.state.apply(
            name=name,
            sls_sources=sls_sources,
            render=render,
            runtime=runtime,
            subs=["states"],
            cache_dir=cache_dir,
            sls=sls,
            test=test,
            acct_file=acct_file,
            acct_key=acct_key,
            acct_profile=acct_profile,
        )

        current_run = hub.idem.RUNS[name]["running"]
        if has_passed(current_run):
            return {"re_runs_count": count, "require_re_run": False}

        if is_same_result(last_run, current_run):
            count_wo_change = count_wo_change + 1
        else:
            # reset the count w/o changes upon a change
            count_wo_change = 0

        last_run = current_run

    hub.log.debug(
        f"Reconciliation loop returns after {count} runs total, and {count_wo_change} runs without any change."
    )
    print(
        f"Reconciliation loop returns after {count} runs total, and {count_wo_change} executions without any change."
    )

    return {
        "re_runs_count": count,
        "require_re_run": True,
    }


def has_passed(runs):
    # If result is not True or there are changes - then return false and reconcile
    for tag in runs:
        if not runs[tag]["result"] is True or bool(runs[tag]["changes"]) is True:
            return False
    return True


def is_same_result(run1, run2):
    for tag in run1:
        if (
            run2[tag]
            and run1[tag]["result"] == run2[tag]["result"]
            and run1[tag]["changes"] == run2[tag]["changes"]
        ):
            continue
        else:
            return False

    return True
