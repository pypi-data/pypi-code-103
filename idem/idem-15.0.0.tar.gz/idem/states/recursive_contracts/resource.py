import asyncio
from typing import Any
from typing import Dict
from typing import List


def sig_present(hub, ctx, name: str, *args, **kwargs):
    ...


def sig_absent(hub, ctx, name: str, *args, **kwargs):
    ...


async def sig_describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    ...


def post_present(hub, ctx):
    """
    Conform the output of every state return to this format.
    Valid state modules must return a dictionary with these keys
    """
    try:
        return {
            "changes": ctx.ret["changes"],
            "comment": ctx.ret["comment"],
            "name": ctx.ret["name"],
            "result": ctx.ret["result"],
        }
    except KeyError:
        hub.log.error(f"Improperly formatted state return: {ctx.ref}")
        raise


def post_absent(hub, ctx):
    """
    Conform the output of every state return to this format.
    Valid state modules must return a dictionary with these keys
    """
    try:
        return {
            "changes": ctx.ret["changes"],
            "comment": ctx.ret["comment"],
            "name": ctx.ret["name"],
            "result": ctx.ret["result"],
        }
    except KeyError:
        hub.log.error(f"Improperly formatted state return: {ctx.ref}")
        raise


def _verify_describe(hub, ret: Dict[str, Dict[str, Any]]):
    """
    Verify that the return value looks like
    {
        state_name: { path.present: [{},...] }
    }
    """
    for present_state in ret.values():
        for state_path, state_data in present_state.items():
            assert isinstance(
                state_data, List
            ), "State information should be formatted as a list"
            for item in state_data:
                assert isinstance(item, Dict), "Each item in the list should be a dict"
    return ret


async def _averify_describe(hub, ret):
    """
    Return a coroutine to a function that is expecting a coroutine
    """
    return _verify_describe(hub, await ret)


def post_describe(hub, ctx):
    if asyncio.iscoroutine(ctx.ret):
        return _averify_describe(hub, ctx.ret)
    else:
        return _verify_describe(hub, ctx.ret)
