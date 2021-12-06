#!/usr/bin/env python3
# Copyright 2004-present Facebook. All Rights Reserved.

import asyncio
import json
import os
import threading
from pathlib import Path
from typing import Dict, Sequence, Union

import h5py
import pytest

from ...graphs.config import Config
from ...graphs.graph import Graph
from ...graphs.group import Connections, Group
from ...graphs.method import AsyncPublisher, background, main, publisher, subscriber
from ...graphs.module import Module
from ...graphs.node import Node
from ...graphs.topic import Topic
from ...messages.message import Message
from ...util.random import random_string
from ...util.testing import get_test_filename, local_test
from ..exceptions import NormalTermination
from ..local_runner import LocalRunner
from ..parallel_runner import ParallelRunner


NUM_MESSAGES = 30
SAMPLE_RATE = 10

LOCAL_OUTPUT_FILENAME = get_test_filename("json")
DISTRIBUTED_OUTPUT_FILENAME = get_test_filename("json")
PARALLEL_ONE_PROCESS_FILENAME = get_test_filename("json")


class MyMessage1(Message):
    int_field: int


class MyMessage2(Message):
    str_field: str


class MySource(Node):
    A = Topic(MyMessage1)

    def __init__(self) -> None:
        super(MySource, self).__init__()

    @publisher(A)
    async def source(self) -> AsyncPublisher:
        for i in range(NUM_MESSAGES):
            yield self.A, MyMessage1(int_field=i)
            await asyncio.sleep(1 / SAMPLE_RATE)


class MyTransform(Node):
    B = Topic(MyMessage1)
    C = Topic(MyMessage2)

    @subscriber(B)
    @publisher(C)
    async def transform(self, message: MyMessage1) -> AsyncPublisher:
        yield self.C, MyMessage2(str_field=str(message.int_field))


class MySinkConfig(Config):
    output_filename: str


class MySink(Node):
    D = Topic(MyMessage2)
    config: MySinkConfig

    def setup(self) -> None:
        self.messages_seen: int = 0

    @subscriber(D)
    def sink(self, message: MyMessage2) -> None:
        with open(self.config.output_filename, "a") as output_file:
            output_file.write(json.dumps(message.asdict()) + "\n")
        self.messages_seen += 1
        if self.messages_seen == NUM_MESSAGES:
            raise NormalTermination()


class MyLocalGraph(Graph):
    config: MySinkConfig

    SOURCE: MySource
    TRANSFORM: MyTransform
    SINK: MySink

    def setup(self) -> None:
        self.SINK.configure(self.config)

    def connections(self) -> Connections:
        return ((self.SOURCE.A, self.TRANSFORM.B), (self.TRANSFORM.C, self.SINK.D))

    def logging(self) -> Dict[str, Topic]:
        return {"source_a": self.SOURCE.A, "transform_c": self.TRANSFORM.C}


@local_test
def test_local_run() -> None:
    runner = LocalRunner(
        module=MyLocalGraph(config=MySinkConfig(output_filename=LOCAL_OUTPUT_FILENAME))
    )
    runner.run()
    remaining_numbers = {str(i) for i in range(NUM_MESSAGES)}
    with open(LOCAL_OUTPUT_FILENAME, "r") as output_file:
        lines = output_file.readlines()
    assert len(lines) == NUM_MESSAGES
    for line in lines:
        message = MyMessage2.fromdict(json.loads(line))
        assert message.str_field in remaining_numbers
        remaining_numbers.remove(message.str_field)

    assert len(remaining_numbers) == 0
    os.remove(LOCAL_OUTPUT_FILENAME)


class PubGroup(Group):
    SOURCE: MySource
    TRANSFORM: MyTransform

    def connections(self) -> Connections:
        return ((self.SOURCE.A, self.TRANSFORM.B),)


class SubGroup(Group):
    SINK: MySink
    config: MySinkConfig

    def setup(self) -> None:
        self.SINK.configure(self.config)


class MyDistributedConfig(Config):
    output_filename: str


class MyDistributedGraph(Graph):
    PUB: PubGroup
    SUB: SubGroup

    config: MyDistributedConfig

    def setup(self) -> None:
        self.SUB.configure(MySinkConfig(output_filename=self.config.output_filename))

    def connections(self) -> Connections:
        return ((self.PUB.TRANSFORM.C, self.SUB.SINK.D),)

    def process_modules(self) -> Sequence[Module]:
        return (self.PUB, self.SUB)

    def logging(self) -> Dict[str, Topic]:
        return {"source_a": self.PUB.SOURCE.A, "transform_c": self.PUB.TRANSFORM.C}


class MyBackgroundMainConfig(Config):
    background_filename: str
    main_filename: str
    string: str


class MyBackgroundMainNode(Node):
    config: MyBackgroundMainConfig

    def setup(self) -> None:
        self.barrier = threading.Barrier(2)

    @background
    async def my_background(self) -> None:
        with open(self.config.background_filename, "w") as f:
            f.write(self.config.string)
        self.barrier.wait()

    @main
    def my_main(self) -> None:
        with open(self.config.main_filename, "w") as f:
            f.write(self.config.string)
        self.barrier.wait()
        raise NormalTermination()


@local_test
def test_background_method() -> None:
    """
    Tests that methods decorated with `@background` and `@main` are executed correctly.
    """
    test_background_filename = get_test_filename()
    test_main_filename = get_test_filename()
    test_string = random_string(100)

    node = MyBackgroundMainNode()
    node.configure(
        MyBackgroundMainConfig(
            background_filename=test_background_filename,
            main_filename=test_main_filename,
            string=test_string,
        )
    )
    runner = LocalRunner(module=node)
    runner.run()
    with open(test_background_filename, "r") as f:
        background_written_string = f.read()
    assert test_string == background_written_string
    with open(test_main_filename, "r") as f:
        main_written_string = f.read()
    assert test_string == main_written_string
