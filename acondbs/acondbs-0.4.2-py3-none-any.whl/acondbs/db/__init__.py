"""SQLAlchemy and DB related

This package contains functions, classes, and other objects that are
related to SQLAlchemy and the DB except ORM model declarations.

"""


from pathlib import Path
from flask_migrate import Migrate

from .sa import sa
from .conn import close_db_connection
from .cmds import init_db_command
from .cmds import dump_db_command
from .cmds import import_csv_command
from .cmds import export_csv_command
from .cmds import backup_db_command

migrate = Migrate()

_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.joinpath("migrations")


##__________________________________________________________________||
def init_app(app):
    """Initialize the Flask application object

    This function is called by `create_app()` of Flask

    Parameters
    ----------
    app : Flask
        The Flask application object, an instance of `Flask`
    """
    sa.init_app(app)
    migrate.init_app(app, sa, directory=_MIGRATIONS_DIR)
    app.cli.add_command(init_db_command)
    app.cli.add_command(dump_db_command)
    app.cli.add_command(import_csv_command)
    app.cli.add_command(export_csv_command)
    app.cli.add_command(backup_db_command)
    app.teardown_appcontext(close_db_connection)


##__________________________________________________________________||
