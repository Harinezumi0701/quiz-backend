from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    category = Column(String(100))
    question_set = Column(String(100), nullable=True)  # For organizing into dumps/sets (e.g., "Dump 1", "Set A")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    # A question can have multiple answer options
    options = relationship("AnswerOption", back_populates="question")
