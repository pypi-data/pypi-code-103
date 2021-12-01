import io
import logging
from abc import ABCMeta
from pyarrow.parquet import ParquetFile

logger = logging.getLogger(__name__)


class ServiceIO(io.RawIOBase, metaclass=ABCMeta):
    backend_type: str
    path: str
    metadata: dict
    size: int

    def to_parquet_file(self) -> ParquetFile:
        # Note the source works when set to the ServiceIO instance, do not
        # just pass in the path.
        return ParquetFile(
            source=self,
            # Buffer size > 0 tells pyarrow to use buffering when
            # deserializing individual column chunks. Setting this to a low
            # value reduces the memory usage and amount of data read. Not
            # setting this will cause the whole column chunk to be read into
            # memory unbuffered.
            buffer_size=0,
            # TODO scott: memorymap = True did not help memory usage with
            #   Rollo's pyarrow 0.16.1, but we haven't tried again in
            #   pyarrow 2.0.0.
            # Tried with buffer_size >0 in pyarrow 2.0.0 but got the error
            # message:
            # File "pyarrow/error.pxi", line 99, in pyarrow.lib.check_status
            # OSError: IOError: An HTTP Client raised an unhandled exception:
            # cannot switch to a different thread. Detail: Python exception:
            # HTTPClientError
        )


class S3File(ServiceIO):
    """
    Abstracts over an S3 object summary to return a *seekable*
    io object. Using the S3 Range header to emulate the seek
    method.
    """

    # NOTE These are additional methods on the
    # file object used later on in serializing metadata
    # all backends (for now just S3 - but  in future
    # and datastore like google cloud azure, SAN filesystems)
    # are expected to implement these methods.
    backend_type = 's3'

    def __init__(
        self,
        key_dict: dict = None,
        bucket_name: str = None,
        get_object=None,
    ):
        self.key_dict = key_dict
        # There is a non trivial overhead to using the OO resource.
        # probably because boto service definitions are defined in
        # json, there's an IO overhead in calling functions. Fetching
        # and binding this ahead of time improves things.
        self.get_object_func = get_object
        self.bucket_name = bucket_name
        self.position = 0

    @property
    def key(self):
        return self.key_dict['Key']

    @property
    def metadata(self):
        return {
            'e_tag': self.key_dict['ETag'].strip('"'),  # e_tag is md5 of file
            'size': self.key_dict['Size'],
            'last_modified': self.key_dict['LastModified']
        }

    @property
    def size(self):
        return int(self.key_dict['Size'])

    @property
    def path(self):
        return self.key_dict['Key']

    def __repr__(self):
        return '<{} bucket_name={} path={}>'.format(
            type(self).__name__,
            self.bucket_name,
            self.path
        )

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = offset
        elif whence == io.SEEK_CUR:
            self.position += offset
        elif whence == io.SEEK_END:
            self.position = self.size + offset
        else:
            raise ValueError(
                'invalid whence ({}, should be {}, {}, {})'.format(
                    whence, io.SEEK_SET, io.SEEK_CUR, io.SEEK_END
                )
            )

        return self.position

    def seekable(self):
        return True

    def read(self, size=-1):
        if size == -1:
            # Read to the end of the file
            logger.debug('Read to the end of the S3File')
            range_header = 'bytes={}-'.format(self.position)
            self.seek(offset=0, whence=io.SEEK_END)

        else:
            new_position = self.position + size

            # AWS doesn't support starting bytes positions
            # at the end of the file (which would return an
            # empty bytes string anyway). i.e this
            # self.get_func(Range='bytes={self.size}-')
            # will fail
            if self.position >= self.size:
                return b''

            # If we're going to read beyond the end of the object, return
            # the entire object.
            if new_position >= self.size:
                return self.read()

            range_header = 'bytes={}-{}'.format(
                self.position, new_position - 1
            )

            self.seek(offset=size, whence=io.SEEK_CUR)

        obj = self.get_object_func(
            Bucket=self.bucket_name,
            Key=self.key,
            Range=range_header,
        )

        return obj['Body'].read()

    def readable(self):
        return True

    def readall(self):
        return self.read()

    def readinto(self, b):
        """
        Read bytes into a pre-allocated, writable bytes-like object b

        :param b: Bytes buffer, might be a bytearray. Cannot use typing on
        this method as we get a mypy error message that contradicts the
        source code:

        Argument 1 of "readinto" is incompatible with supertype "RawIOBase";
        supertype defines the argument type as
        "Union[bytearray, memoryview, array[Any], mmap]".

        :return: Return the number of bytes read. If no bytes are available,
        None is returned.
        """
        # Use a memoryview because it slices without copying the data, which
        # makes it fast/memory efficient.
        # https://julien.danjou.info/high-performance-in-python-with-zero-copy
        # -and-the-buffer-protocol/
        view = memoryview(b)
        # Try to read enough of the file to fill up the buffer.
        data = self.read(len(view))
        # Handle the case of asking for more bytes than there are in the file.
        number_of_bytes_read = len(data)
        view[:number_of_bytes_read] = data
        return number_of_bytes_read

    def write(self, b):
        raise NotImplementedError(
            'We should not be writing, the object should be read-only'
        )