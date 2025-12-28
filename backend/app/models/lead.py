from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Lead(BaseModel):
    """Lead model for in-memory storage"""
    id: Optional[str] = Field(alias="_id", default=None)
    
    # Contact Info
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    
    # Company Info
    company_name: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    
    # Lead Management
    source: Optional[str] = None
    status: str = "new"
    score: int = 0
    
    # Notes
    notes: Optional[str] = None
    
    # Activity Log
    activities: List[dict] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "company_name": "Acme Corp",
                "status": "new"
            }
        }