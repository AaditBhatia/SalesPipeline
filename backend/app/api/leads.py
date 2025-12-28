from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.services.lead_service import lead_service, LeadService
from app.services.grok_service import grok_service
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leads", tags=["leads"])

async def get_lead_service():
    return lead_service

@router.post("/", response_model=LeadResponse, status_code=201)
def create_lead(
    lead_data: LeadCreate,
    service: LeadService = Depends(get_lead_service)
):
    """Create a new lead"""
    return service.create_lead(lead_data)

@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    service: LeadService = Depends(get_lead_service)
):
    """List all leads"""
    return service.list_leads(skip=skip, limit=limit, status=status)

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """Get lead by ID"""
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    service: LeadService = Depends(get_lead_service)
):
    """Update lead"""
    lead = service.update_lead(lead_id, lead_data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.delete("/{lead_id}")
def delete_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """Delete lead"""
    deleted = service.delete_lead(lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}

@router.post("/{lead_id}/qualify")
def qualify_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """
    AI-powered lead qualification
    """
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Mock qualification logic
    qualification_data = {
        "status": "qualified" if lead.score > 50 else "contacted",
    }
    
    updated_lead = service.update_lead(lead_id, LeadUpdate(**qualification_data))
    
    return {
        "message": "Lead qualified successfully",
        "lead": updated_lead,
        "qualification": {
            "budget": "medium",
            "authority": "influencer",
            "need": "high",
            "timeline": "1-3_months"
        }
    }

@router.post("/{lead_id}/score")
async def score_lead_endpoint(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """
    AI-powered lead scoring using Grok
    """
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get AI scoring from Grok
    scoring_result = await grok_service.score_lead(lead.model_dump())
    
    # Update lead with new score
    updated_lead = service.update_lead(lead_id, LeadUpdate(score=scoring_result["score"]))
    
    # Log the AI scoring activity
    service._log_activity(
        lead_id,
        "ai_scoring",
        f"Grok AI scored lead: {scoring_result['score']}/100 - {scoring_result['priority_level']} priority",
        {
            "score": scoring_result["score"],
            "breakdown": scoring_result["breakdown"],
            "priority": scoring_result["priority_level"],
            "insights": scoring_result.get("key_insights", []),
            "recommended_action": scoring_result.get("recommended_action", ""),
            "deal_size": scoring_result.get("estimated_deal_size", ""),
            "deal_size_reasoning": scoring_result.get("deal_size_reasoning", ""),
            "strengths": scoring_result.get("strengths", []),
            "red_flags": scoring_result.get("red_flags", [])
        }
    )
    
    # Send initial contact email after scoring
    email_sent = False
    try:
        logger.info("="*80)
        logger.info("📧 STARTING EMAIL AUTOMATION AFTER SCORING")
        logger.info(f"Lead: {updated_lead.first_name} {updated_lead.last_name}")
        logger.info(f"Score: {scoring_result['score']}/100")
        logger.info("="*80)
        
        email_result = email_service.send_initial_contact(updated_lead.model_dump())
        if email_result.get("success"):
            email_sent = True
            # Update lead status to contacted since email was sent
            updated_lead = service.update_lead(lead_id, LeadUpdate(status="contacted"))
            
            service._log_activity(
                lead_id,
                "email_sent",
                f"Initial contact email sent to {updated_lead.email}",
                {"email_id": email_result.get("email_id"), "type": "initial_contact"}
            )
            
            logger.info("="*80)
            logger.info("✅ EMAIL AUTOMATION COMPLETED")
            logger.info(f"Status updated: new → contacted")
            logger.info("="*80)
    except Exception as e:
        logger.error("="*80)
        logger.error("❌ EMAIL AUTOMATION FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("="*80)
        # Don't fail the scoring if email fails
        service._log_activity(
            lead_id,
            "email_failed",
            f"Failed to send initial contact email: {str(e)}",
            {"error": str(e)}
        )
    
    return {
        "message": "Lead scored successfully with AI",
        "lead": updated_lead,
        "ai_analysis": scoring_result,
        "email_sent": email_sent
    }

@router.post("/{lead_id}/rescore")
async def rescore_lead_endpoint(
    lead_id: str,
    request: dict,
    service: LeadService = Depends(get_lead_service)
):
    """
    Rescore a lead with additional context/comments
    """
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    additional_context = request.get("comment", "")
    
    if not additional_context:
        raise HTTPException(status_code=400, detail="Comment is required for rescoring")
    
    # Get AI scoring with additional context
    scoring_result = await grok_service.score_lead(lead.model_dump(), additional_context)
    
    # Update lead with new score
    updated_lead = service.update_lead(lead_id, LeadUpdate(score=scoring_result["score"]))
    
    # Log the AI scoring activity with comment
    service._log_activity(
        lead_id,
        "ai_scoring",
        f"Grok AI rescored lead with additional context: {scoring_result['score']}/100 - {scoring_result['priority_level']} priority",
        {
            "score": scoring_result["score"],
            "breakdown": scoring_result["breakdown"],
            "priority": scoring_result["priority_level"],
            "insights": scoring_result.get("key_insights", []),
            "recommended_action": scoring_result.get("recommended_action", ""),
            "deal_size": scoring_result.get("estimated_deal_size", ""),
            "deal_size_reasoning": scoring_result.get("deal_size_reasoning", ""),
            "strengths": scoring_result.get("strengths", []),
            "red_flags": scoring_result.get("red_flags", []),
            "user_comment": additional_context
        }
    )
    
    return {
        "message": "Lead rescored successfully with additional context",
        "lead": updated_lead,
        "ai_analysis": scoring_result,
        "comment": additional_context
    }

@router.post("/{lead_id}/auto-workflow")
async def auto_workflow(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """
    Automated workflow: AI Score → Qualify → Contact → Demo
    """
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    workflow_log = []
    base_time = datetime.utcnow()
    
    # Step 1: AI-powered scoring
    workflow_log.append("🤖 Running AI analysis...")
    scoring_result = await grok_service.score_lead(lead.model_dump())
    
    score = scoring_result["score"]
    lead = service.update_lead(lead_id, LeadUpdate(score=score))
    workflow_log.append(f"✓ AI scored lead: {score}/100 ({scoring_result['priority_level']} priority)")
    
    # Log AI scoring
    service._log_activity(
        lead_id,
        "ai_scoring",
        f"Grok AI analyzed lead profile: {score}/100 - {scoring_result['priority_level']} priority. {scoring_result['recommended_action']}",
        {
            "score": score,
            "breakdown": scoring_result["breakdown"],
            "priority": scoring_result["priority_level"],
            "insights": scoring_result.get("key_insights", []),
            "deal_size": scoring_result.get("estimated_deal_size", ""),
            "deal_size_reasoning": scoring_result.get("deal_size_reasoning", ""),
            "strengths": scoring_result.get("strengths", []),
            "red_flags": scoring_result.get("red_flags", []),
            "recommended_action": scoring_result.get("recommended_action", "")
        },
        custom_time=base_time
    )
    
    # Step 2: Contact (5 minutes later)
    contacted_time = base_time + timedelta(minutes=5)
    lead = service.update_lead(lead_id, LeadUpdate(status="contacted"))
    workflow_log.append("✓ Marked as contacted")
    
    contact_messages = [
        f"Sales rep sent personalized email to {lead.first_name} based on AI insights",
        f"Personalized outreach sent highlighting {scoring_result.get('key_insights', ['our solution'])[0] if scoring_result.get('key_insights') else 'our solution'}",
        f"Initial contact made with {lead.first_name} - mentioned their {lead.job_title} role at {lead.company_name}"
    ]
    
    service._log_activity(
        lead_id,
        "contact_attempt",
        random.choice(contact_messages),
        {"method": "email", "ai_guided": True},
        custom_time=contacted_time
    )
    
    # Step 3: Qualify (2 hours later)
    qualified_time = base_time + timedelta(hours=2)
    lead = service.update_lead(lead_id, LeadUpdate(status="qualified"))
    workflow_log.append("✓ Lead qualified")
    
    service._log_activity(
        lead_id,
        "ai_qualification",
        f"Lead qualified with {score}/100 score. AI predicts {scoring_result['estimated_deal_size']} deal size. Key insight: {scoring_result.get('key_insights', ['Good fit'])[0] if scoring_result.get('key_insights') else 'Good fit'}",
        {
            "score": score,
            "ai_insights": scoring_result.get('key_insights', []),
            "deal_size": scoring_result['estimated_deal_size']
        },
        custom_time=qualified_time
    )
    
    # Step 4: Demo (1 day later)
    demo_time = base_time + timedelta(days=1)
    lead = service.update_lead(lead_id, LeadUpdate(status="demo"))
    workflow_log.append("✓ Demo scheduled")
    
    service._log_activity(
        lead_id,
        "demo_scheduled",
        f"Demo scheduled for {lead.company_name}. Preparing customized presentation for {scoring_result['estimated_deal_size']} deal",
        {
            "demo_date": (demo_time + timedelta(days=2)).isoformat(),
            "estimated_deal_size": scoring_result['estimated_deal_size'],
            "key_talking_points": scoring_result.get('key_insights', [])
        },
        custom_time=demo_time
    )
    
    service._log_activity(
        lead_id,
        "workflow_completed",
        f"✅ AI-powered workflow completed. {lead.company_name} moved to demo stage with {score}/100 score",
        {
            "final_status": "demo",
            "final_score": score,
            "ai_priority": scoring_result['priority_level'],
            "total_time": "~1 day"
        },
        custom_time=demo_time
    )
    
    return {
        "message": "AI-powered workflow completed!",
        "lead": lead,
        "workflow_log": workflow_log,
        "ai_analysis": {
            "score": score,
            "priority": scoring_result['priority_level'],
            "insights": scoring_result.get('key_insights', []),
            "recommended_action": scoring_result['recommended_action']
        }
    }

@router.post("/{lead_id}/send-contact-email")
async def send_contact_email(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """Send initial contact email"""
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Send email
    result = email_service.send_initial_contact(lead.model_dump())
    
    if result['success']:
        # Log activity
        service._log_activity(
            lead_id,
            "email_sent",
            f"Initial contact email sent to {lead.first_name}",
            {"email_id": result.get('email_id')}
        )
        
        # Update status
        service.update_lead(lead_id, LeadUpdate(status="contacted"))
    
    return {
        "message": "Email sent successfully" if result['success'] else "Failed to send email",
        "result": result
    }

@router.post("/{lead_id}/send-demo-email")
async def send_demo_email(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """Send demo invitation with Calendly link"""
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Send demo invite
    result = email_service.send_demo_invite(lead.model_dump())
    
    if result['success']:
        # Log activity
        service._log_activity(
            lead_id,
            "demo_invite_sent",
            f"Demo invitation sent to {lead.first_name} with scheduling link",
            {"email_id": result.get('email_id')}
        )
        
        # Update status
        service.update_lead(lead_id, LeadUpdate(status="demo"))
    
    return {
        "message": "Demo invite sent successfully" if result['success'] else "Failed to send invite",
        "result": result
    }

@router.post("/{lead_id}/send-followup-email")
async def send_followup_email(
    lead_id: str,
    service: LeadService = Depends(get_lead_service)
):
    """Send follow-up email"""
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Send follow-up
    result = email_service.send_follow_up(lead.model_dump())
    
    if result['success']:
        # Log activity
        service._log_activity(
            lead_id,
            "followup_sent",
            f"Follow-up email sent to {lead.first_name}",
            {"email_id": result.get('email_id')}
        )
    
    return {
        "message": "Follow-up sent successfully" if result['success'] else "Failed to send follow-up",
        "result": result
    }