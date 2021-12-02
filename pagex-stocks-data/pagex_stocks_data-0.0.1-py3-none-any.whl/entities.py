from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from pagexdata.database import Base
from pagexdata.database import db_session
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class RedditHits(Base):
    __tablename__ = 'reddit_hits'

    date = Column(DateTime, primary_key=True)
    ticker_symbol = Column(String, primary_key=True)
    subreddit = Column(String, primary_key=True)
    hits = Column(Integer)
    positive_hits = Column(Boolean)
    rank = Column(Integer, nullable=True)
    previous_rank = Column(Integer, nullable=True)
    change_rank = Column(Integer, nullable=True)
    change_hits_one_day = Column(Integer, nullable=True)
    change_hits_two_days = Column(Integer, nullable=True)
    change_hits_three_days = Column(Integer, nullable=True)
    change_hits_one_week = Column(Integer, nullable=True)
    change_hits_two_weeks = Column(Integer, nullable=True)
    change_hits_four_weeks = Column(Integer, nullable=True)
    hits_volatility_one_week = Column(Float, nullable=True)
    hits_volatility_two_weeks = Column(Float, nullable=True)


class RedditHitsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RedditHits
        sqla_session = db_session
        load_instance = False


class StockData(Base):
    __tablename__ = 'stockdata'

    date = Column(DateTime, primary_key=True)
    ticker_symbol = Column(String, primary_key=True)
    price = Column(Float)
    volume = Column(Integer)


class StockDataSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = StockData
        sqla_session = db_session
        load_instance = False

