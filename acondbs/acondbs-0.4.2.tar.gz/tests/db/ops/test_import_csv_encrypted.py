from pathlib import Path
import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables, import_tables_from_csv_files


from acondbs.models import GitHubToken

from ...constants import SAMPLE_DIR


##__________________________________________________________________||
@pytest.fixture
def app():
    config_path = Path(SAMPLE_DIR, "config.py")
    database_uri = "sqlite:///:memory:"
    app = create_app(
        config_path=config_path, SQLALCHEMY_DATABASE_URI=database_uri
    )
    with app.app_context():
        define_tables()
    yield app


##__________________________________________________________________||
def test_encrypted_field(app):
    csvdir = Path(SAMPLE_DIR, "csv")
    with app.app_context():
        import_tables_from_csv_files(csvdir)
        assert "token123" == GitHubToken.query.one().token


def test_how_to_encrypt_and_decrypt(app):
    unencrypted = "token123"
    encrypted = "aKjGknYDHY39Z2xAaN7+sQ=="

    with app.app_context():
        secret_key = app.config["SECRET_KEY"]  # 'secret_key_test_123'

    from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

    engine = AesEngine()
    engine._update_key(secret_key)
    engine._set_padding_mechanism(None)

    assert engine.encrypt(unencrypted) == encrypted
    assert engine.decrypt(encrypted) == unencrypted


##__________________________________________________________________||
