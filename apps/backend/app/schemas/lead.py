from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LeadCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = "manual"
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    company_id: Optional[int] = None
    company_name: str
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = None
    status: str
    score: int
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
