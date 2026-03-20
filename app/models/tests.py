from uuid import UUID


from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("uuidv7()"),
    )
    name = Column(String(100), nullable=False)
    category_id = Column(
        UUID[UUID](as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=True)
    time_limit = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="tests")
    questions = relationship("Question", back_populates="test_obj")
    user_assignments = relationship("UserTestAssignment", back_populates="test", cascade="all, delete-orphan")
