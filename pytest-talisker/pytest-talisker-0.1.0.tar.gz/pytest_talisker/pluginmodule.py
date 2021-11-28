# This module basically tries to initialize talisker as soon as possible in the
# initialisation process of pytest

import talisker.logs               # noqa
talisker.logs.configure_test_logging()  # noqa

import talisker.testing
talisker.testing.configure_testing()
