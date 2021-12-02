import datetime
import sqlalchemy
import pytest

from acondbs.db.sa import sa
from acondbs.models import ProductType, Product


##__________________________________________________________________||
def test_add(app):
    """A simple test of adding an object with a date field"""

    type1 = ProductType(name="type1")

    # time_posted needs to be initialized with a datetime.date
    time_posted = datetime.datetime(2019, 2, 23, 9, 10, 25)
    product1 = Product(name="product1", time_posted=time_posted, type_=type1)

    with app.app_context():
        sa.session.add(product1)
        sa.session.commit()

    with app.app_context():
        product1 = Product.query.filter_by(name="product1").first()

        # The type of the field "time_posted" of Product is "datetime.date"
        assert isinstance(product1.time_posted, datetime.date)

        assert (
            datetime.datetime(2019, 2, 23, 9, 10, 25) == product1.time_posted
        )


##__________________________________________________________________||
def test_add_raise(app):
    """A simple test of adding an object with a wrong type"""

    type1 = ProductType(name="type1")

    # It is not impossible to instnaiate a date field with a wrong
    # type, e.g, str
    product1 = Product(
        name="product1", time_posted="2019-02-13 10:15:21", type_=type1
    )

    with app.app_context():

        # It is also possible to add
        sa.session.add(product1)

        # However, it is not possible to commit
        with pytest.raises(sqlalchemy.exc.StatementError):
            sa.session.commit()


##__________________________________________________________________||
