import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

database_url = os.getenv("DATABASE_URL")

engine = create_engine(database_url, echo=False, future=True)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()