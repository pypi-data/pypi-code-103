from .tensorflow_block import get_params_feed_dict, run_tensorflow_graph

try:
    # Tensorflow 1.14 uses abseil, which breaks the logger.
    # https://github.com/tensorflow/tensorflow/issues/26691
    import absl.logging

    # https://github.com/abseil/abseil-py/issues/99
    absl.logging.root.removeHandler(absl.logging._absl_handler)
    # https://github.com/abseil/abseil-py/issues/102
    absl.logging._warn_preinit_stderr = False
except Exception:
    pass
