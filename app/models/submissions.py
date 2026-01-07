from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Submission(Base):
    """Model for user submissions - each submission is an answer to a question"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    submission_history_id = Column(Integer, ForeignKey("submission_history.id"), nullable=True)  # Track which submission history this belongs to
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="submissions")
    question = relationship("Question")
    selected_option = relationship("AnswerOption", foreign_keys=[selected_option_id])
    submission_history = relationship("SubmissionHistory", back_populates="submissions")

