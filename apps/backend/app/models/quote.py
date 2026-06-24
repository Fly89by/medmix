from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50))
    customer_email = Column(String(255))
    product = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    city = Column(String(255))
    notes = Column(Text)
    status = Column(String(50), default="DRAFT", index=True)
    pdf_url = Column(String(500))
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
