import httpx
from app.config import settings
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ZapierService:
    def __init__(self):
        self.webhook_url = settings.ZAPIER_WEBHOOK_URL
    
    async def send_event(self, event_type: str, data: Dict):
        """
        Send event to Zapier webhook
        
        Args:
            event_type: Type of event (new_lead, lead_scored, demo_scheduled, etc.)
            data: Event data to send
        """
        if not self.webhook_url:
            logger.warning("Zapier webhook URL not configured")
            return False
        
        payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                
                if response.status_code == 200:
                    logger.info(f"✅ Zapier event sent: {event_type}")
                    return True
                else:
                    logger.error(f"❌ Zapier webhook failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Zapier webhook error: {e}")
            return False
    
    async def new_lead_created(self, lead: Dict):
        """Trigger when a new lead is created"""
        await self.send_event("new_lead", {
            "lead_id": lead.get("id"),
            "name": f"{lead.get('first_name')} {lead.get('last_name')}",
            "first_name": lead.get("first_name"),
            "last_name": lead.get("last_name"),
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "company": lead.get("company_name"),
            "job_title": lead.get("job_title"),
            "company_size": lead.get("company_size"),
            "industry": lead.get("industry"),
            "source": lead.get("source"),
            "status": lead.get("status"),
            "score": lead.get("score", 0)
        })
    
    async def lead_scored(self, lead: Dict, score_data: Dict):
        """Trigger when a lead is scored by AI"""
        await self.send_event("lead_scored", {
            "lead_id": lead.get("id"),
            "name": f"{lead.get('first_name')} {lead.get('last_name')}",
            "email": lead.get("email"),
            "company": lead.get("company_name"),
            "score": score_data.get("score"),
            "priority": score_data.get("priority_level"),
            "deal_size": score_data.get("estimated_deal_size"),
            "insights": score_data.get("key_insights", []),
            "recommended_action": score_data.get("recommended_action")
        })
    
    async def hot_lead_detected(self, lead: Dict, score: int):
        """Trigger when a lead scores 70+"""
        await self.send_event("hot_lead", {
            "lead_id": lead.get("id"),
            "name": f"{lead.get('first_name')} {lead.get('last_name')}",
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "company": lead.get("company_name"),
            "job_title": lead.get("job_title"),
            "score": score,
            "alert": f"🔥 HIGH PRIORITY: {lead.get('first_name')} {lead.get('last_name')} from {lead.get('company_name')} scored {score}/100!"
        })
    
    async def demo_scheduled(self, lead: Dict):
        """Trigger when a demo is scheduled"""
        await self.send_event("demo_scheduled", {
            "lead_id": lead.get("id"),
            "name": f"{lead.get('first_name')} {lead.get('last_name')}",
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "company": lead.get("company_name"),
            "job_title": lead.get("job_title"),
            "score": lead.get("score")
        })
    
    async def lead_qualified(self, lead: Dict):
        """Trigger when a lead is qualified"""
        await self.send_event("lead_qualified", {
            "lead_id": lead.get("id"),
            "name": f"{lead.get('first_name')} {lead.get('last_name')}",
            "email": lead.get("email"),
            "company": lead.get("company_name"),
            "score": lead.get("score")
        })

# Global instance
zapier_service = ZapierService()