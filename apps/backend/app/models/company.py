from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(255))
    city = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
