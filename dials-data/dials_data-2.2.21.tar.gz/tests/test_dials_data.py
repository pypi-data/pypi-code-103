import pathlib
from unittest import mock

import py
import pytest

import dials_data
import dials_data.datasets
import dials_data.download


def test_all_datasets_can_be_parsed():
    assert dials_data.datasets.definition


def test_repository_location():
    rl = dials_data.datasets.repository_location()
    assert rl.check(dir=1)


def test_fetching_undefined_datasets_does_not_crash():
    df = dials_data.download.DataFetcher(read_only=True)
    assert df("aardvark") is False


def test_requests_for_future_datasets_can_be_intercepted():
    df = dials_data.download.DataFetcher(read_only=True)
    df.result_filter = mock.Mock()
    df.result_filter.return_value = False
    assert df("aardvark") is False
    df.result_filter.assert_called_once_with(result=False)


@mock.patch("dials_data.datasets.repository_location")
@mock.patch("dials_data.download.fetch_dataset")
def test_datafetcher_constructs_py_path(fetcher, root):
    root.return_value = py.path.local("/tmp/root")
    fetcher.return_value = True

    df = dials_data.download.DataFetcher(read_only=True)
    with pytest.warns(DeprecationWarning):
        ds = df("dataset")
    assert ds == py.path.local("/tmp/root/dataset")
    assert isinstance(ds, py.path.local)
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )

    ds = df("dataset", pathlib=False)
    assert ds == py.path.local("/tmp/root/dataset")
    assert isinstance(ds, py.path.local)
    fetcher.assert_called_once()


@mock.patch("dials_data.datasets.repository_location")
@mock.patch("dials_data.download.fetch_dataset")
def test_datafetcher_constructs_path(fetcher, root):
    test_path = py.path.local("/tmp/root")
    root.return_value = test_path
    fetcher.return_value = True

    df = dials_data.download.DataFetcher(read_only=True)
    ds = df("dataset", pathlib=True)
    assert ds == pathlib.Path(test_path) / "dataset"

    assert isinstance(ds, pathlib.Path)
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )

    ds = df("dataset")
    assert ds == pathlib.Path(test_path) / "dataset"
    assert not isinstance(
        ds, pathlib.Path
    )  # default is currently to return py.path.local()
    fetcher.assert_called_once_with(
        "dataset", pre_scan=True, read_only=False, download_lockdir=mock.ANY
    )
