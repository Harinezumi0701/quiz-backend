import os
from dotenv import load_dotenv  
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()  # Load .env file

DATABASE_URL = os.getenv("DATABASE_URL")

# Disable echo in production, enable in development
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
engine = create_engine(DATABASE_URL, echo=DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()