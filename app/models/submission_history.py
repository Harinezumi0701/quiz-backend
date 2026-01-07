from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class SubmissionHistory(Base):
    """Model to track submission history - each record represents one submit action"""
    __tablename__ = "submission_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, server_default=func.now(), nullable=False)
    submission_count = Column(Integer, default=1, nullable=False)  # Number of submissions in this history record
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="submission_history")
    submissions = relationship("Submission", back_populates="submission_history")

