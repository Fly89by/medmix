from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: str = "active"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ContactCreate(BaseModel):
    company_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    company_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    company_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    company_id: int
    project_name: str
    city: Optional[str] = None
    budget: Optional[float] = None
    status: str = "active"


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    city: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    company_id: int
    project_name: str
    city: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    company_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ActivityResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
