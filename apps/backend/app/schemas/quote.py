from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class QuoteCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    product: str
    quantity: float
    unit_price: float
    city: Optional[str] = None
    notes: Optional[str] = None


class QuoteUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    product: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class QuoteResponse(BaseModel):
    id: int
    quote_number: str
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    product: str
    quantity: float
    unit_price: float
    total_price: float
    city: Optional[str] = None
    notes: Optional[str] = None
    status: str
    pdf_url: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
