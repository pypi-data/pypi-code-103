import warnings

import pytest
import unittest.mock as mock

from acondbs.db.backup import backup_db

##__________________________________________________________________||
@pytest.fixture()
def mock_backup_db_to_github(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.db.backup.backup_db_to_github", y)
    yield y

@pytest.fixture()
def mock_backup_db_as_csv_to_github(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.db.backup.backup_db_as_csv_to_github", y)
    yield y

##__________________________________________________________________||
def test_backup_db(mock_backup_db_to_github, mock_backup_db_as_csv_to_github):
    backup_db()
    mock_backup_db_to_github.assert_called_once()
    mock_backup_db_as_csv_to_github.assert_called_once()

def test_exceptions(mock_backup_db_to_github, mock_backup_db_as_csv_to_github):
    mock_backup_db_to_github.side_effect = Exception()
    mock_backup_db_as_csv_to_github.side_effect = Exception()
    with warnings.catch_warnings(record=True) as w:
        backup_db()
    assert len(w) == 2
    mock_backup_db_to_github.assert_called_once()
    mock_backup_db_as_csv_to_github.assert_called_once()

##__________________________________________________________________||
