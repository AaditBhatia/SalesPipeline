from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    score: Optional[int] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: str
    status: str
    score: int
    activities: List[dict] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True