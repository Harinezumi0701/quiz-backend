from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AnswerOption(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)
    explanation = Column(Text, nullable=True)
    question = relationship("Question", back_populates="options")

