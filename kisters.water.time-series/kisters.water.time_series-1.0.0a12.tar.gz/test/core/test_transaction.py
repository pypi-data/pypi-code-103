import pytest

from kisters.water.time_series.core import TimeSeriesTransaction


class MockedCommitTransaction(TimeSeriesTransaction):
    async def commit_async(self):
        self.commit_async_was_called = True

    def commit(self):
        self.commit_was_called = True


@pytest.mark.asyncio
async def test_async_transaction_context():
    async with MockedCommitTransaction(None) as t:
        pass
    assert t.commit_async_was_called

    with pytest.raises(Exception):
        async with MockedCommitTransaction(None) as t:
            raise Exception
    assert not hasattr(t, "commit_async_was_called")


def test_transaction_context():
    with MockedCommitTransaction(None) as t:
        pass
    assert t.commit_was_called

    with pytest.raises(Exception):
        with MockedCommitTransaction(None) as t:
            raise Exception
    assert not hasattr(t, "commit_was_called")
