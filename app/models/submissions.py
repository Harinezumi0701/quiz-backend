

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Submission(Base):
    """Model for user submissions - each submission is an answer to a question"""
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id"), nullable=False)
    submission_history_id = Column(UUID(as_uuid=True), ForeignKey("submission_history.id"), nullable=True)  # Track which submission history this belongs to
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="submissions")
    question = relationship("Question")
    answer = relationship("AnswerOption", foreign_keys=[answer_id])
    submission_history = relationship("SubmissionHistory", back_populates="submissions")

