# app/models/roles.py
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    default = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    users = relationship("User", back_populates="role_obj")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(String(200), nullable=False, index=True)  # Format: namespace::action or *::*
    name = Column(String(200), nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role", back_populates="permissions")
