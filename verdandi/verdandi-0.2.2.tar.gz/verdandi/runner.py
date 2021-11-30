import tracemalloc
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from statistics import mean
from time import perf_counter
from typing import Any, Callable, List, Type

from verdandi import cli
from verdandi.benchmark import Benchmark
from verdandi.result import BenchmarkResult, IterationStats, ResultType
from verdandi.utils import flatten


class BenchmarkRunner:
    result_class = BenchmarkResult

    def __init__(self, show_stdout: bool = False, show_stderr: bool = False, failfast: bool = False) -> None:
        self.show_stdout = show_stdout
        self.show_stderr = show_stderr
        self.failfast = failfast

    def run(self, benchmarks: List[Benchmark]) -> None:
        results: List[List[BenchmarkResult]] = []

        for benchmark in flatten(benchmarks):
            result = self.run_class(benchmark)
            results.append(result)

        cli.print_results_as_table(flatten(results))

        if self.show_stdout:
            cli.print_header("Captured stdout")
            for class_result in results:
                for method_result in class_result:
                    cli.print_stdout(method_result)

        if self.show_stderr:
            cli.print_header("Captured stderr")
            for class_result in results:
                for method_result in class_result:
                    cli.print_stderr(method_result)

        cli.print_header("Exceptions")
        for class_result in results:
            for method_result in class_result:
                cli.print_exceptions(method_result)

    def run_class(self, benchmark_class: Type[Benchmark], iterations: int = 10) -> List[BenchmarkResult]:
        benchmark = benchmark_class()
        methods = benchmark.collect_bench_methods()

        results = []

        benchmark.setUpClass()

        for method in methods:
            stats: List[IterationStats] = []
            stdouts: List[str] = []
            stderrs: List[str] = []
            exceptions: List[Exception] = []
            rtype = ResultType.OK

            benchmark.setUp()

            for _ in range(iterations):
                benchmark.setUpIter()

                try:
                    with redirect_stdout(StringIO()) as stdout, redirect_stderr(StringIO()) as stderr:
                        iter_stats = self.measure(method)
                except Exception as e:
                    if self.failfast:
                        raise e

                    exceptions.append(e)
                    rtype = ResultType.ERROR
                    iter_stats = None  # type: ignore

                stdouts.append(stdout.getvalue())
                stderrs.append(stderr.getvalue())
                stats.append(iter_stats)

                benchmark.tearDownIter()

            benchmark.tearDown()

            result = BenchmarkResult(
                name=benchmark.__class__.__name__ + "." + method.__name__,
                rtype=rtype,
                stdout=stdouts,
                stderr=stderrs,
                exceptions=exceptions,
                duration_sec=mean([s.duration_sec for s in stats]) if rtype != ResultType.ERROR else 0,
                memory_diff=int(mean([s.memory_diff for s in stats])) if rtype != ResultType.ERROR else 0,
            )
            results.append(result)

        benchmark.tearDownClass()

        return results

    def measure(self, func: Callable[..., Any]) -> IterationStats:
        def filter_snapshot(snapshot: tracemalloc.Snapshot) -> tracemalloc.Snapshot:
            """Filters out traces not measured by benchmark"""
            return snapshot.filter_traces(
                (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),  # ignore imports
                    tracemalloc.Filter(False, "<unknown>"),  # ignore empty tracebacks
                    tracemalloc.Filter(False, __file__),  # ignore traces of this module
                    tracemalloc.Filter(False, tracemalloc.__file__),  # ignore traces of the tracemalloc module
                )
            )

        tracemalloc.start()

        start_time = perf_counter()
        start_snapshot = tracemalloc.take_snapshot()

        func()

        stop_snapshot = tracemalloc.take_snapshot()
        stop_time = perf_counter()

        tracemalloc.stop()

        start_snapshot = filter_snapshot(start_snapshot)
        stop_snapshot = filter_snapshot(stop_snapshot)

        time_taken = stop_time - start_time

        # StatisticDiff is sorted from biggest to the smallest
        memory_diff = stop_snapshot.compare_to(start_snapshot, "filename")[0].size_diff

        return IterationStats(time_taken, memory_diff)
