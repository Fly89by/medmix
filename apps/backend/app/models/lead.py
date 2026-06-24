from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company_name = Column(String(255), nullable=False, index=True)
    industry = Column(String(255))
    city = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    source = Column(String(100))
    status = Column(String(50), default="NEW", index=True)
    score = Column(Integer, default=0)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    notes = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
