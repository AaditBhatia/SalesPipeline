from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import random

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse

class LeadService:
    def __init__(self):
        self.leads: Dict[str, dict] = {}
    
    def _log_activity(self, lead_id: str, activity_type: str, details: str, metadata: dict = None, custom_time: datetime = None):
        """Log an activity for a lead with custom timestamp"""
        if lead_id in self.leads:
            activity = {
                "id": str(uuid.uuid4()),
                "type": activity_type,
                "details": details,
                "metadata": metadata or {},
                "timestamp": (custom_time or datetime.utcnow()).isoformat()
            }
            
            if "activities" not in self.leads[lead_id]:
                self.leads[lead_id]["activities"] = []
            
            self.leads[lead_id]["activities"].append(activity)
    
    def create_lead(self, lead_data: LeadCreate) -> LeadResponse:
        """Create a new lead"""
        lead_id = str(uuid.uuid4())
        creation_time = datetime.utcnow()
        
        lead_dict = lead_data.model_dump()
        lead_dict.update({
            "id": lead_id,
            "status": "new",
            "score": 0,
            "activities": [],
            "created_at": creation_time,
            "updated_at": creation_time
        })
        
        self.leads[lead_id] = lead_dict
        
        # Log creation with detailed message
        source_messages = {
            "website": "submitted a contact form on the website",
            "linkedin": "reached out via LinkedIn",
            "referral": "was referred by an existing customer",
            "cold_outreach": "was contacted through cold outreach",
            "event": "met at a conference/event"
        }
        
        source_detail = source_messages.get(lead_data.source, "expressed interest in our product")
        
        self._log_activity(
            lead_id, 
            "lead_created", 
            f"{lead_data.first_name} {lead_data.last_name} from {lead_data.company_name} {source_detail}",
            {
                "source": lead_data.source,
                "company": lead_data.company_name,
                "job_title": lead_data.job_title
            },
            custom_time=creation_time
        )
        
        return LeadResponse(**lead_dict)
    
    def get_lead(self, lead_id: str) -> Optional[LeadResponse]:
        """Get lead by ID"""
        lead = self.leads.get(lead_id)
        if lead:
            return LeadResponse(**lead)
        return None
    
    def list_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[LeadResponse]:
        """List leads with optional filtering"""
        leads_list = list(self.leads.values())
        
        if status:
            leads_list = [lead for lead in leads_list if lead.get("status") == status]
        
        leads_list.sort(key=lambda x: x["created_at"], reverse=True)
        leads_list = leads_list[skip:skip + limit]
        
        return [LeadResponse(**lead) for lead in leads_list]
    
    def update_lead(self, lead_id: str, lead_data: LeadUpdate) -> Optional[LeadResponse]:
        """Update lead"""
        if lead_id not in self.leads:
            return None
        
        lead = self.leads[lead_id]
        update_data = {k: v for k, v in lead_data.model_dump().items() if v is not None}
        update_time = datetime.utcnow()
        
        # Log status changes with descriptive messages
        if "status" in update_data and update_data["status"] != lead.get("status"):
            old_status = lead.get("status")
            new_status = update_data["status"]
            
            status_messages = {
                ("new", "contacted"): f"Initial outreach completed. Sales rep made first contact with {lead.get('first_name')}",
                ("contacted", "qualified"): f"{lead.get('first_name')} showed strong interest and meets our ideal customer profile",
                ("qualified", "demo"): f"Product demo scheduled with {lead.get('first_name')} and their team",
                ("demo", "closed_won"): f"🎉 Deal closed! {lead.get('company_name')} signed the contract",
                ("demo", "closed_lost"): f"Deal lost. {lead.get('company_name')} decided to go with a competitor"
            }
            
            message = status_messages.get((old_status, new_status), 
                                         f"Lead status updated from {old_status} to {new_status}")
            
            self._log_activity(
                lead_id,
                "status_changed",
                message,
                {"old_status": old_status, "new_status": new_status},
                custom_time=update_time
            )
        
        # Log score changes with descriptive messages
        if "score" in update_data and update_data["score"] != lead.get("score"):
            old_score = lead.get("score", 0)
            new_score = update_data["score"]
            
            score_change = new_score - old_score
            direction = "increased" if score_change > 0 else "decreased"
            
            score_messages = {
                range(0, 30): "Low priority lead - consider nurture campaign",
                range(30, 50): "Medium priority - follow up within 3-5 days",
                range(50, 70): "Good lead quality - reach out within 24-48 hours",
                range(70, 101): "🔥 Hot lead! High conversion potential - contact immediately"
            }
            
            priority_msg = next((msg for r, msg in score_messages.items() if new_score in r), "")
            
            self._log_activity(
                lead_id,
                "score_updated",
                f"Lead score {direction} from {old_score} to {new_score}. {priority_msg}",
                {"old_score": old_score, "new_score": new_score, "change": score_change},
                custom_time=update_time
            )
        
        lead.update(update_data)
        lead["updated_at"] = update_time
        
        return LeadResponse(**lead)
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete lead"""
        if lead_id in self.leads:
            del self.leads[lead_id]
            return True
        return False

# Global instance
lead_service = LeadService()