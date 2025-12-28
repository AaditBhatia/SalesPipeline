from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import pytz

from app.services.email_service import email_service
from app.services.lead_service import lead_service

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling background tasks like delayed emails"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        self.scheduler.start()
        logger.info("📅 Scheduler service initialized")

    def schedule_email(
        self,
        lead_id: str,
        email_type: str,
        delay_minutes: int = 0,
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Schedule an email to be sent at a specific time

        Args:
            lead_id: ID of the lead to send email to
            email_type: Type of email (initial_contact, demo_invite, follow_up)
            delay_minutes: Minutes to delay from now (ignored if scheduled_time is provided)
            scheduled_time: Specific datetime to send email (UTC)

        Returns:
            dict with job_id and scheduled_time
        """
        # Get lead data
        lead = lead_service.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        # Calculate send time
        if scheduled_time:
            send_time = scheduled_time
        else:
            send_time = datetime.now(pytz.UTC) + timedelta(minutes=delay_minutes)

        # Create job based on email type
        if email_type == "initial_contact":
            job = self.scheduler.add_job(
                func=self._send_initial_contact,
                trigger=DateTrigger(run_date=send_time),
                args=[lead_id],
                id=f"email_{lead_id}_{email_type}_{send_time.timestamp()}",
                replace_existing=False
            )
        elif email_type == "demo_invite":
            job = self.scheduler.add_job(
                func=self._send_demo_invite,
                trigger=DateTrigger(run_date=send_time),
                args=[lead_id],
                id=f"email_{lead_id}_{email_type}_{send_time.timestamp()}",
                replace_existing=False
            )
        elif email_type == "follow_up":
            job = self.scheduler.add_job(
                func=self._send_follow_up,
                trigger=DateTrigger(run_date=send_time),
                args=[lead_id],
                id=f"email_{lead_id}_{email_type}_{send_time.timestamp()}",
                replace_existing=False
            )
        else:
            raise ValueError(f"Invalid email type: {email_type}")

        logger.info(f"📧 Scheduled {email_type} email for lead {lead_id} at {send_time}")

        return {
            "success": True,
            "job_id": job.id,
            "scheduled_time": send_time.isoformat(),
            "email_type": email_type,
            "lead_id": lead_id
        }

    def schedule_email_sequence(
        self,
        lead_id: str,
        sequence_name: str = "standard"
    ) -> Dict[str, Any]:
        """
        Schedule a sequence of emails for a lead

        Sequences:
        - standard: Initial contact -> 2 days -> Follow-up -> 3 days -> Demo invite
        - aggressive: Initial contact -> 1 day -> Follow-up -> 1 day -> Demo invite
        - nurture: Initial contact -> 3 days -> Follow-up -> 7 days -> Follow-up -> 7 days -> Demo invite
        """
        sequences = {
            "standard": [
                ("initial_contact", 0),      # Immediate
                ("follow_up", 2880),          # 2 days (2880 minutes)
                ("demo_invite", 7200)         # 5 days total (7200 minutes)
            ],
            "aggressive": [
                ("initial_contact", 0),       # Immediate
                ("follow_up", 1440),          # 1 day (1440 minutes)
                ("demo_invite", 2880)         # 2 days total (2880 minutes)
            ],
            "nurture": [
                ("initial_contact", 0),       # Immediate
                ("follow_up", 4320),          # 3 days (4320 minutes)
                ("follow_up", 14400),         # 10 days total (14400 minutes)
                ("demo_invite", 24480)        # 17 days total (24480 minutes)
            ]
        }

        if sequence_name not in sequences:
            raise ValueError(f"Invalid sequence: {sequence_name}. Available: {list(sequences.keys())}")

        sequence = sequences[sequence_name]
        scheduled_jobs = []

        for email_type, delay_minutes in sequence:
            result = self.schedule_email(lead_id, email_type, delay_minutes)
            scheduled_jobs.append(result)

        logger.info(f"📧 Scheduled '{sequence_name}' email sequence for lead {lead_id}")

        # Log activity
        lead_service.add_activity(
            lead_id,
            "email_sequence_scheduled",
            {
                "sequence_name": sequence_name,
                "total_emails": len(scheduled_jobs),
                "jobs": scheduled_jobs
            }
        )

        return {
            "success": True,
            "sequence_name": sequence_name,
            "lead_id": lead_id,
            "scheduled_jobs": scheduled_jobs
        }

    def cancel_scheduled_email(self, job_id: str) -> Dict[str, Any]:
        """Cancel a scheduled email job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"🚫 Cancelled scheduled email job: {job_id}")
            return {"success": True, "job_id": job_id}
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_scheduled_jobs(self, lead_id: Optional[str] = None) -> list:
        """Get all scheduled jobs, optionally filtered by lead_id"""
        jobs = self.scheduler.get_jobs()

        result = []
        for job in jobs:
            job_data = {
                "job_id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "func_name": job.func.__name__
            }

            # Filter by lead_id if provided
            if lead_id:
                if f"_{lead_id}_" in job.id:
                    result.append(job_data)
            else:
                result.append(job_data)

        return result

    # Internal methods for sending emails
    def _send_initial_contact(self, lead_id: str):
        """Send initial contact email (called by scheduler)"""
        try:
            lead = lead_service.get_lead(lead_id)
            if not lead:
                logger.error(f"Lead {lead_id} not found for scheduled email")
                return

            result = email_service.send_initial_contact(lead)

            if result["success"]:
                # Update lead status
                lead_service.update_lead(lead_id, {"status": "contacted"})

                # Log activity
                lead_service.add_activity(
                    lead_id,
                    "email_sent",
                    {
                        "email_type": "initial_contact",
                        "email_id": result.get("email_id"),
                        "scheduled": True
                    }
                )
                logger.info(f"✅ Scheduled initial contact email sent to {lead['email']}")
            else:
                lead_service.add_activity(
                    lead_id,
                    "email_failed",
                    {
                        "email_type": "initial_contact",
                        "error": result.get("error"),
                        "scheduled": True
                    }
                )
                logger.error(f"❌ Scheduled initial contact email failed for {lead['email']}")
        except Exception as e:
            logger.error(f"Error in scheduled initial contact email: {e}")

    def _send_demo_invite(self, lead_id: str):
        """Send demo invite email (called by scheduler)"""
        try:
            lead = lead_service.get_lead(lead_id)
            if not lead:
                logger.error(f"Lead {lead_id} not found for scheduled email")
                return

            result = email_service.send_demo_invite(lead)

            if result["success"]:
                # Update lead status
                lead_service.update_lead(lead_id, {"status": "demo"})

                # Log activity
                lead_service.add_activity(
                    lead_id,
                    "demo_invite_sent",
                    {
                        "email_id": result.get("email_id"),
                        "scheduled": True
                    }
                )
                logger.info(f"✅ Scheduled demo invite sent to {lead['email']}")
            else:
                lead_service.add_activity(
                    lead_id,
                    "email_failed",
                    {
                        "email_type": "demo_invite",
                        "error": result.get("error"),
                        "scheduled": True
                    }
                )
        except Exception as e:
            logger.error(f"Error in scheduled demo invite: {e}")

    def _send_follow_up(self, lead_id: str):
        """Send follow-up email (called by scheduler)"""
        try:
            lead = lead_service.get_lead(lead_id)
            if not lead:
                logger.error(f"Lead {lead_id} not found for scheduled email")
                return

            result = email_service.send_follow_up(lead)

            if result["success"]:
                # Log activity
                lead_service.add_activity(
                    lead_id,
                    "email_sent",
                    {
                        "email_type": "follow_up",
                        "email_id": result.get("email_id"),
                        "scheduled": True
                    }
                )
                logger.info(f"✅ Scheduled follow-up sent to {lead['email']}")
            else:
                lead_service.add_activity(
                    lead_id,
                    "email_failed",
                    {
                        "email_type": "follow_up",
                        "error": result.get("error"),
                        "scheduled": True
                    }
                )
        except Exception as e:
            logger.error(f"Error in scheduled follow-up: {e}")

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("📅 Scheduler service shut down")


# Global instance
scheduler_service = SchedulerService()
