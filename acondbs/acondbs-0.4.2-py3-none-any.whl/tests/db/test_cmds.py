from pathlib import Path

import pytest
import unittest.mock as mock

from ..constants import SAMPLE_DIR


##__________________________________________________________________||
@pytest.fixture()
def mock_define_tables(monkeypatch):
    ret = mock.Mock()
    monkeypatch.setattr("acondbs.db.cmds.define_tables", ret)
    return ret


def test_init_db_command(runner, mock_define_tables):
    """test command init-db"""
    result = runner.invoke(args=["init-db"])
    assert [mock.call()] == mock_define_tables.call_args_list
    assert "Initialized" in result.output


##__________________________________________________________________||
def test_dump_db_command(runner):
    """test command dump-db"""
    result = runner.invoke(args=["dump-db"])
    assert 0 == result.exit_code
    assert 1800 < len(result.output)


##__________________________________________________________________||
@pytest.fixture()
def mock_import_tables_from_csv_files(monkeypatch):
    ret = mock.Mock()
    monkeypatch.setattr("acondbs.db.cmds.import_tables_from_csv_files", ret)
    return ret


def test_import_csv_command(runner, mock_import_tables_from_csv_files):
    """test command import-csv"""

    csvdir = str(Path(SAMPLE_DIR, "csv"))
    # needs to give an existing path to `import-csv` as `click.Path()`
    # checks the check the existence.

    result = runner.invoke(args=["import-csv", csvdir])
    assert 0 == result.exit_code
    assert [
        mock.call(csvdir)
    ] == mock_import_tables_from_csv_files.call_args_list


##__________________________________________________________________||
@pytest.fixture()
def mock_export_db_to_csv_files(monkeypatch):
    ret = mock.Mock()
    monkeypatch.setattr("acondbs.db.cmds.export_db_to_csv_files", ret)
    return ret


def test_export_csv_command(
    runner, tmpdir_factory, mock_export_db_to_csv_files
):
    """test command export-csv"""

    tmpdir = str(tmpdir_factory.mktemp("csv_out"))
    csvdir = str(Path(tmpdir, "csv"))

    result = runner.invoke(args=["export-csv", csvdir])
    assert 0 == result.exit_code
    assert [mock.call(csvdir)] == mock_export_db_to_csv_files.call_args_list


##__________________________________________________________________||
