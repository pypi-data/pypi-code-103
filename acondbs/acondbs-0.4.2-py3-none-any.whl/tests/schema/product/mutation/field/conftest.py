import pytest

from acondbs import ops


##__________________________________________________________________||
@pytest.fixture
def app(app_users):
    y = app_users
    with y.app_context():
        ops.create_field(
            field_id=1,
            name="contact",
            type_=ops.FieldType.UnicodeText,
        )
        ops.create_field(
            field_id=2,
            name="produced_by",
            type_=ops.FieldType.UnicodeText,
        )
        ops.create_field(
            field_id=3,
            name="date_produced",
            type_=ops.FieldType.Date,
        )
        ops.commit()
    yield y


##__________________________________________________________________||
