import pytest
import sqlalchemy

from acondbs.db.conn import get_db_connection


##__________________________________________________________________||
def test_get_close_db_connection(app):
    with app.app_context():
        conn = get_db_connection()
        assert conn is get_db_connection()

    with pytest.raises(sqlalchemy.exc.ResourceClosedError) as e:
        conn.execute("SELECT 1")

    assert "closed" in str(e.value)


##__________________________________________________________________||
