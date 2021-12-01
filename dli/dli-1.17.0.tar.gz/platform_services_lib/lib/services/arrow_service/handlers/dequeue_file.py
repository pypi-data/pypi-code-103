#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

import io
import logging
from pyarrow.lib import Buffer


class DequeueFile(io.IOBase):
    """
    Fake interface to output a arrow IPC stream. A pyarrow
    RecordBatchStreamWriter can only take a file like object.
    Since Flask can't return that without buffering the enitre
    response, which can be Terabytes! we create a fake file object
    that doesn't buffer.

    N.B inherits from io.BytesIO because pyarrow does a typecheck
    on files passed in as a sink.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO investigate using the collections.deque datastructure
        self.queue = []

    def __del__(self):
        """Destructor."""
        self.logger.debug('Destructor called on DequeueFile')

    def write(self, data):
        # TODO ask Artur why this wasn't a problem in testing.
        # sometimes pyarrow seems to be passing in a buffer
        # rather than a byte string. There's possibly a way
        # of steaming this raw buffer without doing a copy, i.e
        # improving how the dequeue function works.
        if type(data) == Buffer:
            self.queue.append(data.to_pybytes())
        else:
            self.queue.append(data)

    def writable(self):
        return True

    def dequeue(self):
        if len(self.queue) == 0:
            self.logger.warning('dequeue returning an empty array')

        yield from self.queue

        # Explicitly clear the list.
        self.queue.clear()
