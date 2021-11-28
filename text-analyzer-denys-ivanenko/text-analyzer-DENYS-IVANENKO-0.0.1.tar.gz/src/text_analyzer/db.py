from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///../../text_analyzer_db.sqlite", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
