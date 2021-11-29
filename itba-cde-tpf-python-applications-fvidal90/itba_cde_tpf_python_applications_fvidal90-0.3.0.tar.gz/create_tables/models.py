"""Dummy data model definition."""

from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockValue(Base):
    """Stock value data model."""

    __tablename__ = "stock_value"
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    __table_args__ = (UniqueConstraint('symbol', 'date'),)

    def __repr__(self):
        return f"<StockValue(symbol='{self.symbol}', ...)>"
