from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateSchema as SQACreateSchema


class CreateSchema(SQACreateSchema):
    def __init__(
        self, name, quote=None, if_not_exists: bool = False, authorization: str = None, **kw
    ):
        if quote is not None:
            kw.update({"quote": quote})
        super().__init__(name, **kw)
        self._option_if_not_exists = if_not_exists
        self._option_authorization = authorization


@compiles(CreateSchema)
def _visit_create_schema(element, compiler, **kw):
    raise NotImplementedError()


@compiles(CreateSchema, "postgresql")
def _visit_create_schema(element, compiler, **kw):
    pre_options = " ".join(
        filter(
            lambda x: x is not None, ["IF NOT EXISTS" if element._option_if_not_exists else None]
        )
    )

    post_options = " ".join(
        filter(
            lambda x: x is not None,
            [
                f"AUTHORIZATION {element._option_authorization}"
                if element._option_authorization
                else None
            ],
        )
    )

    return f"CREATE SCHEMA {pre_options} {element.element} {post_options}"
