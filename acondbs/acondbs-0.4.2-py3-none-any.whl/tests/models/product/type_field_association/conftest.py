import pytest

from acondbs.db.sa import sa
from acondbs.models import ProductType, FieldType, Field, TypeFieldAssociation


##__________________________________________________________________||
@pytest.fixture
def app(app_empty):

    y = app_empty

    field1 = Field(name="field1", type_=FieldType.UnicodeText)
    field2 = Field(name="field2", type_=FieldType.Integer)

    assoc1 = TypeFieldAssociation(iid=1, field=field1)
    assoc2 = TypeFieldAssociation(iid=2, field=field2)

    type1 = ProductType(
        name="type1",
        fields=[assoc1, assoc2],
    )

    with y.app_context():
        sa.session.add(field1)
        sa.session.add(field2)
        sa.session.add(type1)
        sa.session.commit()

    yield y


##__________________________________________________________________||
