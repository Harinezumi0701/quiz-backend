import os
from dotenv import load_dotenv  
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # load file .env

DATABASE_URL = os.getenv("DATABASE_URL")

# Tắt echo trong production, bật trong development
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
engine = create_engine(DATABASE_URL, echo=DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()