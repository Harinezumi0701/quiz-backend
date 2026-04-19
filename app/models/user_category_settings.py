from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserCategorySettings(Base):
    __tablename__ = "user_category_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=text("uuidv7()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    questions_per_day = Column(Integer, nullable=False, default=20)
    time_limit = Column(Integer, nullable=False, default=60)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_user_category_settings"),
    )

    user = relationship("User", back_populates="category_settings")
    category = relationship("Category", back_populates="user_settings")
