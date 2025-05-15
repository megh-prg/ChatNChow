# BE/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BE.base import Base

SQLALCHEMY_DATABASE_URL = "postgresql://delivery_user:securepassword@localhost/food_delivery"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()