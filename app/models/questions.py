from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    question_set_id = Column(UUID(as_uuid=True), ForeignKey("question_sets.id"), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    category_obj = relationship("Category", back_populates="questions")
    question_set_obj = relationship("QuestionSet", back_populates="questions")
    options = relationship("AnswerOption", back_populates="question")

    @property
    def category(self):
        """Backward compatibility: return category name as string"""
        return self.category_obj.name if self.category_obj else None

    @property
    def question_set(self):
        """Backward compatibility: return question set name as string"""
        return self.question_set_obj.name if self.question_set_obj else None
