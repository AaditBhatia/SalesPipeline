import resend
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Set Resend API key
resend.api_key = settings.RESEND_API_KEY

class EmailService:
    def __init__(self):
        self.from_email = settings.FROM_EMAIL
        self.company_name = settings.COMPANY_NAME
    
    def send_initial_contact(self, lead_data: dict) -> dict:
        """Send initial contact email"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        email = lead_data.get('email')
        
        logger.info("="*80)
        logger.info("📧 EMAIL SENDING STARTED")
        logger.info(f"To: {email}")
        logger.info(f"Type: Initial Contact")
        logger.info(f"Lead: {first_name} from {company}")
        logger.info("="*80)
        
        try:
            params = {
                "from": self.from_email,
                "to": [email],
                "subject": f"Great to connect, {first_name}!",
                "html": f"""
                <h2>Hi {first_name}!</h2>
                
                <p>Thanks for your interest in {self.company_name}! We're excited to learn more about {company}.</p>
                
                <p>Based on your profile, I think you'd be a great fit for our API infrastructure platform.</p>
                
                <h3>Why teams love us:</h3>
                <ul>
                    <li>99.99% uptime SLA</li>
                    <li>Enterprise-grade security</li>
                    <li>Setup in under 30 minutes</li>
                    <li>24/7 support</li>
                </ul>
                
                <p>Let's chat! Reply to this email with your availability.</p>
                
                <p>Looking forward to connecting!</p>
                
                <p><strong>Your Sales Team</strong><br>
                {self.company_name}</p>
                """
            }
            
            response = resend.Emails.send(params)
            
            logger.info("="*80)
            logger.info("✅ EMAIL SENT SUCCESSFULLY")
            logger.info(f"Email ID: {response.get('id')}")
            logger.info(f"To: {email}")
            logger.info("="*80)
            
            return {"success": True, "email_id": response.get('id')}
            
        except Exception as e:
            logger.error("="*80)
            logger.error("❌ EMAIL SENDING FAILED")
            logger.error(f"Error: {e}")
            logger.error(f"To: {email}")
            logger.error("="*80)
            return {"success": False, "error": str(e)}
    
    def send_demo_invite(self, lead_data: dict, calendly_link: str = "https://calendly.com/your-company/demo") -> dict:
        """Send demo scheduling invite with Calendly link"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        
        try:
            params = {
                "from": self.from_email,
                "to": [lead_data['email']],
                "subject": f"🎯 Ready for your demo, {first_name}?",
                "html": f"""
                <h2>You're Qualified! 🎉</h2>
                
                <p>Hi {first_name},</p>
                
                <p>Great news! Based on our conversation, our platform is a perfect fit for {company}'s needs.</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>What to Expect:</h3>
                    <ul>
                        <li>Personalized walkthrough for {company}</li>
                        <li>Live Q&A with our team</li>
                        <li>Custom pricing for your scale</li>
                        <li>Implementation timeline</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{calendly_link}" 
                       style="background: #2563eb; color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        📅 Schedule Your Demo
                    </a>
                </div>
                
                <p><strong>Duration:</strong> 30-45 minutes<br>
                <strong>Format:</strong> Video call</p>
                
                <p>Questions? Just reply to this email!</p>
                
                <p>Best,<br>
                <strong>Your Sales Team</strong></p>
                """
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Demo invite sent to {lead_data['email']}: {response}")
            
            return {"success": True, "email_id": response.get('id')}
            
        except Exception as e:
            logger.error(f"Failed to send demo invite: {e}")
            return {"success": False, "error": str(e)}
    
    def send_follow_up(self, lead_data: dict) -> dict:
        """Send follow-up email"""
        first_name = lead_data.get('first_name')
        
        try:
            params = {
                "from": self.from_email,
                "to": [lead_data['email']],
                "subject": f"Following up, {first_name}!",
                "html": f"""
                <h2>Hi {first_name}!</h2>
                
                <p>Just checking in! Did you have any questions about our platform?</p>
                
                <p>I'm here to help with:</p>
                <ul>
                    <li>Technical questions</li>
                    <li>Pricing details</li>
                    <li>Integration help</li>
                    <li>Scheduling a demo</li>
                </ul>
                
                <p>Just reply to this email and let me know what would be helpful!</p>
                
                <p>Best,<br>
                <strong>Your Sales Team</strong></p>
                """
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Follow-up sent to {lead_data['email']}: {response}")
            
            return {"success": True, "email_id": response.get('id')}
            
        except Exception as e:
            logger.error(f"Failed to send follow-up: {e}")
            return {"success": False, "error": str(e)}

# Global instance
email_service = EmailService()