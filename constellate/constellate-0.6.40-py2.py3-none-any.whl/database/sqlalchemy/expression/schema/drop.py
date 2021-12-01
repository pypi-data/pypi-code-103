from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropSchema as SQADropSchema


class DropSchema(SQADropSchema):
    def __init__(self, name, quote=None, if_exists: bool = False, cascade: bool = False, **kw):
        if quote is not None:
            kw.update({"quote": quote})
        super().__init__(name, **kw)
        self._option_if_exists = if_exists
        self._option_cascade = cascade


@compiles(DropSchema)
def _visit_drop_schema(element, compiler, **kw):
    raise NotImplementedError()


@compiles(DropSchema, "postgresql")
def _visit_drop_schema(element, compiler, **kw):
    pre_options = " ".join(
        filter(lambda x: x is not None, ["IF EXISTS" if element._option_if_exists else None])
    )

    post_options = " ".join(
        filter(
            lambda x: x is not None,
            [f"cascade {element._option_cascade}" if element._option_cascade else None],
        )
    )

    return f"DROP SCHEMA {pre_options} {element.element} {post_options}"
