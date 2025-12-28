import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        self.company_name = settings.COMPANY_NAME

    async def _send_email_async(self, to_email: str, subject: str, html_content: str) -> dict:
        """Send email via SMTP asynchronously"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )

            return {"success": True, "email_id": f"smtp_{to_email}_{subject[:20]}"}
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return {"success": False, "error": str(e)}

    def _send_email_sync(self, to_email: str, subject: str, html_content: str) -> dict:
        """Synchronous wrapper for async email sending"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._send_email_async(to_email, subject, html_content))
    
    async def send_initial_contact(self, lead_data: dict, ai_email_content: dict = None) -> dict:
        """Send initial contact email with AI-generated content"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        email = lead_data.get('email')

        logger.info("="*80)
        logger.info("📧 EMAIL SENDING STARTED")
        logger.info(f"To: {email}")
        logger.info(f"Type: Initial Contact")
        logger.info(f"Lead: {first_name} from {company}")
        if ai_email_content:
            logger.info("✨ Using AI-generated content")
        logger.info("="*80)

        # Use AI-generated content if provided, otherwise use template
        if ai_email_content:
            subject = ai_email_content.get('subject', f"Great to connect, {first_name}!")
            html_content = ai_email_content.get('body_html')
        else:
            subject = f"Great to connect, {first_name}!"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
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
            </body>
            </html>
            """

        result = await self._send_email_async(email, subject, html_content)

        if result["success"]:
            logger.info("="*80)
            logger.info("✅ EMAIL SENT SUCCESSFULLY")
            logger.info(f"Email ID: {result.get('email_id')}")
            logger.info(f"To: {email}")
            logger.info("="*80)
        else:
            logger.error("="*80)
            logger.error("❌ EMAIL SENDING FAILED")
            logger.error(f"Error: {result.get('error')}")
            logger.error(f"To: {email}")
            logger.error("="*80)

        return result
    
    async def send_demo_invite(self, lead_data: dict, calendly_link: str = "https://calendly.com/your-company/demo") -> dict:
        """Send demo scheduling invite with Calendly link"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        email = lead_data.get('email')

        subject = f"🎯 Ready for your demo, {first_name}?"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
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
        </body>
        </html>
        """

        result = await self._send_email_async(email, subject, html_content)

        if result["success"]:
            logger.info(f"Demo invite sent to {email}: {result.get('email_id')}")
        else:
            logger.error(f"Failed to send demo invite: {result.get('error')}")

        return result
    
    def send_follow_up(self, lead_data: dict) -> dict:
        """Send follow-up email"""
        first_name = lead_data.get('first_name')
        email = lead_data.get('email')

        subject = f"Following up, {first_name}!"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
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
        </body>
        </html>
        """

        result = self._send_email_sync(email, subject, html_content)

        if result["success"]:
            logger.info(f"Follow-up sent to {email}: {result.get('email_id')}")
        else:
            logger.error(f"Failed to send follow-up: {result.get('error')}")

        return result

# Global instance
email_service = EmailService()