"""
Billing Schemas - Invoices, Payments
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.models import InvoiceStatus


# ============================================
# Invoice/Billing Schemas
# ============================================
class InvoiceCreate(BaseModel):
    """Invoice creation request schema"""
    case_id: str
    client_id: str
    amount: str = Field(..., description="Amount in KRW")
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class InvoiceUpdate(BaseModel):
    """Invoice update request schema"""
    amount: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None


class InvoiceOut(BaseModel):
    """Invoice output schema"""
    id: str
    case_id: str
    case_title: Optional[str] = None
    client_id: str
    client_name: Optional[str] = None
    lawyer_id: str
    lawyer_name: Optional[str] = None
    amount: str
    description: Optional[str] = None
    status: InvoiceStatus
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Invoice list response schema"""
    invoices: List[InvoiceOut]
    total: int
    total_pending: str = "0"  # Total pending amount
    total_paid: str = "0"  # Total paid amount


class InvoicePaymentRequest(BaseModel):
    """Invoice payment request schema"""
    payment_method: str = Field(..., description="Payment method (card, bank, etc.)")
    payment_reference: Optional[str] = None
