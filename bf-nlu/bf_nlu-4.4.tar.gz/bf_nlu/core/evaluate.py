import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":  # pragma: no cover
    raise RuntimeError(
        "Calling `bf_nlu.core.evaluate` directly is no longer supported. Please use "
        "`bf_nlu test` to test a combined Core and NLU model or `bf_nlu test core` "
        "to test a Core model."
    )
