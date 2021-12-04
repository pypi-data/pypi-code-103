from contextlib import suppress
from typing import Any, Mapping

from pytest import FixtureRequest

__all__ = [

]


with suppress(ImportError):
    from sqlalchemy import MetaData, engine_from_config, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import scoped_session


    def create_sqlalchemy_engine(
        request: FixtureRequest,
        settings: Mapping[str, Any],
        sqlalchemy_session: scoped_session,
        sqlalchemy_metadata: MetaData,
    ) -> Engine:
        """
        Creates sqlalchemy engine from settings and bind it to ORM session.

        :param request: Pytest fixture request.
        :param settings: Test settings.
        :param sqlalchemy_session: Sqlalchemy ORM session.
        :param sqlalchemy_metadata: Sqlalchemy metadata.
        :return: Sqlalchemy engine.
        """
        engine = engine_from_config(settings, 'sqlalchemy.')

        sqlalchemy_session.configure(bind=engine)

        sqlalchemy_metadata.bind = engine
        sqlalchemy_metadata.create_all(engine)

        def teardown():
            sqlalchemy_session.rollback()
            sqlalchemy_metadata.drop_all(engine)
            sqlalchemy_session.remove()

        request.addfinalizer(teardown)
        return engine

    __all__.append(create_sqlalchemy_engine.__name__)


    def truncate_sqlalchemy_tables(sqlalchemy_engine: Engine,
                                   sqlalchemy_metadata: MetaData,
                                   cascade: bool = False) -> None:
        """
        Truncates tables, which defined in sqlalchemy metadata.

        :param sqlalchemy_engine: Sqlalchemy engine.
        :param sqlalchemy_metadata: Sqlalchemy metadata.
        :param cascade: Flag, that indicates should truncate use cascading or
        not.
        :return:
        """
        for table in reversed(sqlalchemy_metadata.sorted_tables):
            sqlalchemy_engine.execute(
                text(
                    f'TRUNCATE {table.name}{" CASCADE" if cascade else ""}'
                ).execution_options(autocommit=True)
            )

    __all__.append(truncate_sqlalchemy_tables.__name__)
