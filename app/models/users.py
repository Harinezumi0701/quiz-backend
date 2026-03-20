from sqlalchemy import Column, String, TIMESTAMP, Date, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    user_id = Column(String(125), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    birthday = Column(Date, nullable=True)
    address = Column(String(500), nullable=True)
    job_title = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)
    join_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)
    
    role_obj = relationship("Role", back_populates="users")
    submissions = relationship("Submission", back_populates="user")
    submission_history = relationship("SubmissionHistory", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    test_assignments = relationship("UserTestAssignment", back_populates="user", cascade="all, delete-orphan")
    category_access = relationship("UserCategoryAccess", back_populates="user", cascade="all, delete-orphan")
