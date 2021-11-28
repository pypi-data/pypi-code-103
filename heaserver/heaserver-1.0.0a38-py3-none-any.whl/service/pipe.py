"""
Functions for working with pipes in asyncio.
"""

from asyncio import StreamReader, StreamWriter, StreamReaderProtocol, get_running_loop
import os
from typing import IO, Union


def pipe():
    read_fileno, write_fileno = os.pipe()
    read_fd = os.fdopen(read_fileno, 'rb')
    write_fd = os.fdopen(write_fileno, 'wb')
    return read_fd, write_fd


async def pipe_stream():
    read_fd, write_fd = pipe()
    reader = await _create_pipe_stream_reader(read_fd)
    writer = await _create_pipe_stream_writer(write_fd)
    return reader, writer


async def transfer(input_: Union[IO, StreamReader], output: IO) -> None:
    """
    Transfer bytes from an input file-like object or asyncio.StreamReader to an output file-like object.
    :param input_: the input file-like object or stream reader.
    :param output: the output file-like object.
    """
    if os.name == 'nt':
        await _piped_nt(input_, output)
    else:
        await _piped_other(input_, output)


async def _piped_nt(input_: Union[IO, StreamReader], output: IO) -> None:
    read_fd, write_fd = pipe()
    get_running_loop().run_in_executor(None, _do_write, input_, write_fd, 1024)
    _do_reading(read_fd, output)


async def _piped_other(input_: Union[IO, StreamReader], output: IO) -> None:
    reader, writer = await pipe_stream()
    get_running_loop().create_task(_do_write_async(input_, writer, 1024))
    await _do_reading_async(reader, output)


def _do_reading(reader: IO, output: IO) -> None:
    while chunk := reader.read(2 ** 16):
        output.write(chunk)


async def _do_reading_async(reader: StreamReader, output: IO) -> None:
    while not reader.at_eof():
        chunk = await reader.read(2 ** 16)
        output.write(chunk)


async def _create_pipe_stream_reader(read_fd: IO) -> StreamReader:
    loop = get_running_loop()
    reader = StreamReader()
    read_protocol = StreamReaderProtocol(reader)
    read_transport, _ = await loop.connect_read_pipe(lambda: read_protocol, read_fd)
    return reader


async def _create_pipe_stream_writer(write_fd: IO) -> StreamWriter:
    loop = get_running_loop()
    write_protocol = StreamReaderProtocol(StreamReader())
    write_transport, _ = await loop.connect_write_pipe(lambda: write_protocol, write_fd)
    return StreamWriter(write_transport, write_protocol, None, loop)


async def _do_write_async(fd: Union[IO, StreamReader], writer: StreamWriter, n: int = None):
    """
    Writes the contents of a file-like object fd to a stream writer, and closes the writer.

    :param fd: the file-like object supporting read().
    :param writer: the stream writer.
    :param n: read up to size bytes from the object.
    """
    try:
        if isinstance(fd, StreamReader):
            while not fd.at_eof():
                writer.write(fd.read(n))
                await writer.drain()
        else:
            while chunk := fd.read(n):
                writer.write(chunk)
                await writer.drain()
        writer.close()
        await writer.wait_closed()
        writer = None
    finally:
        if writer is not None:
            try:
                writer.close()
                await writer.wait_closed()
            except OSError:
                pass


def _do_write(fd: Union[IO, StreamReader], writer: IO, n: int = None):
    """
    Writes the contents of a file-like object fd to another file-like object, and closes the latter.

    :param fd: the file-like object supporting read().
    :param writer: the stream writer.
    :param n: read up to size bytes from the object.
    """
    try:
        while chunk := fd.read(n):
            writer.write(chunk)
        writer.close()
    finally:
        if not writer.closed:
            try:
                writer.close()
            except OSError:
                pass
