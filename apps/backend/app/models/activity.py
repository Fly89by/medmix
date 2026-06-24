from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
