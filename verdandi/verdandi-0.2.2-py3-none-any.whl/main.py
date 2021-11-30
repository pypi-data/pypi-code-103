# type: ignore

import argparse
import importlib
import logging
import os
import sys
import types
from typing import Any, List, Optional, Type, Union

from verdandi.cli import print_header
from verdandi.loader import BenchmarkLoader
from verdandi.runner import BenchmarkRunner
from verdandi.utils import make_name_importable


class BenchmarkProgram:
    def __init__(
        self,
        module: Optional[Union[str, types.ModuleType]] = None,
        argv: Optional[List[str]] = None,
        bench_loader: Type[BenchmarkLoader] = BenchmarkLoader,
        bench_runner: Type[BenchmarkRunner] = BenchmarkRunner,
    ) -> None:
        self.setup_logging()

        if isinstance(module, str):
            self.module = importlib.import_module(module)
        else:
            self.module = module

        if argv is None:
            argv = sys.argv

        self.bench_loader = bench_loader
        self.bench_runner = bench_runner

        self.parse_args(argv)

        print_header("Benchmark session started")
        print(f"Root directory: {os.getcwd()}")

        self.do_discovery()
        self.run_benchmarks()

    def setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="(Verdandi) [%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

    def parse_args(self, argv: List[str]) -> None:
        parser = self._get_arg_parser()
        parser.parse_args(argv[1:], self)

    def _get_arg_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument("benches", nargs="*", help="List of bench modules or files")
        parser.add_argument(
            "-ff",
            "--failfast",
            dest="failfast",
            help="Break on first uncaught exception, otherwise exceptions will be captured",
            action="store_true",
        )
        parser.add_argument(
            "-o",
            "--show-stdout",
            dest="show_stdout",
            help="Show captured stdout after benchmarks are completed",
            action="store_true",
        )
        parser.add_argument(
            "-e",
            "--show-stderr",
            dest="show_stderr",
            help="Show captured stderr after benchmarks are completed",
            action="store_true",
        )
        parser.add_argument(
            "-s",
            "--start-directory",
            dest="start_dir",
            help="Directory to start the discovery at (defaults to '.')",
            default=".",
        )
        parser.add_argument(
            "-p",
            "--pattern",
            dest="pattern",
            help="Filename pattern used in discovery (defaults to 'bench*.py')",
            default="bench_*.py",
        )

        return parser

    def do_discovery(self) -> None:
        loader = self.bench_loader()

        if not self.benches:
            self.benches = loader.discover(start_dir=self.start_dir, pattern=self.pattern)
        elif self.benches:
            bench_names = [make_name_importable(name) for name in self.benches]
            self.benches = [loader.load_benches_from_name(name) for name in bench_names]
        else:
            self.benches = loader.load_benches_from_module(self.module)

        print(f"Collected {len(self.benches)} benchmark{'s'[:len(self.benches)^1]}")

    def run_benchmarks(self) -> None:
        runner = self.bench_runner(
            show_stdout=self.show_stdout,
            show_stderr=self.show_stderr,
            failfast=self.failfast,
        )

        print()  # Use whitespace as separator here

        runner.run(self.benches)


def main(*args: Any, **kwargs: Any) -> None:
    """Entry point for usage in scripts"""
    BenchmarkProgram(*args, **kwargs)
