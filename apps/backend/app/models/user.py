from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALES_MANAGER = "sales_manager"
    SALES_AGENT = "sales_agent"
    OPERATIONS = "operations"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.SALES_AGENT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
