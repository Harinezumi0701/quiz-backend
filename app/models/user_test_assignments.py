# app/models/user_test_assignments.py
from sqlalchemy import Column, TIMESTAMP, ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserTestAssignment(Base):
    __tablename__ = "user_test_assignments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("uuidv7()"),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    # Unique constraint for user_id + test_id
    __table_args__ = (
        UniqueConstraint("user_id", "test_id", name="uq_user_test_assignment"),
    )

    # Relationships
    user = relationship("User", back_populates="test_assignments")
    test = relationship("Test", back_populates="user_assignments")
