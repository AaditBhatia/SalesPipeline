# Email Automation & Demo Scheduling

This document describes the email automation and demo scheduling features added to the Sales Pipeline application.

## Features

### 1. **SMTP Email Integration**
- Switched from Resend to SMTP for broader compatibility
- No domain verification required
- Works with Gmail, Outlook, Yahoo, SendGrid, and other SMTP providers
- Async email sending for better performance

### 2. **Background Task Scheduler**
- APScheduler integration for delayed and scheduled emails
- Schedule emails for specific times or with delays
- Persistent background jobs that survive server restarts

### 3. **Email Sequences (Drip Campaigns)**
Three pre-configured email sequences:

- **Standard**: Initial contact → 2 days → Follow-up → 3 days → Demo invite
- **Aggressive**: Initial contact → 1 day → Follow-up → 1 day → Demo invite
- **Nurture**: Initial contact → 3 days → Follow-up → 7 days → Follow-up → 7 days → Demo invite

### 4. **Demo Scheduling**
- Calendly integration for demo scheduling
- Automated demo invitation emails
- Configurable scheduling links per campaign

## Setup

### 1. Gmail Configuration

For Gmail, you need to create an **App Password** (not your regular password):

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"
5. Copy the 16-character password

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```env
# Your Gmail address
SMTP_USER=aadit.bhatia93@gmail.com
SMTP_PASSWORD=your_16_char_app_password_here
FROM_EMAIL=aadit.bhatia93@gmail.com
FROM_NAME=Sales AI Team
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Start the Server

```bash
cd backend
uvicorn app.main:app --reload
```

## API Endpoints

### Schedule a Single Email

```http
POST /api/leads/{lead_id}/schedule-email
Content-Type: application/json

{
  "email_type": "initial_contact",
  "delay_minutes": 60
}
```

Or schedule for a specific time:

```json
{
  "email_type": "demo_invite",
  "scheduled_time": "2025-01-15T10:00:00Z"
}
```

**Email Types:**
- `initial_contact` - First outreach email
- `demo_invite` - Demo scheduling invitation
- `follow_up` - Follow-up/nurture email

### Schedule an Email Sequence

```http
POST /api/leads/{lead_id}/schedule-sequence
Content-Type: application/json

{
  "sequence_name": "standard"
}
```

**Sequence Options:**
- `standard` - Balanced approach (5 days total)
- `aggressive` - Fast follow-up (2 days total)
- `nurture` - Slow, relationship-building (17 days total)

### Get Scheduled Emails

```http
GET /api/leads/scheduled-emails
```

Filter by lead:
```http
GET /api/leads/{lead_id}/scheduled-emails
```

### Cancel a Scheduled Email

```http
DELETE /api/leads/scheduled-emails/{job_id}
```

## Example Usage

### 1. Create a lead and schedule an email sequence

```bash
# Create a lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "company_name": "Acme Corp",
    "company_size": "51-200",
    "source": "website"
  }'

# Response will include lead_id
# Use that to schedule a sequence

curl -X POST http://localhost:8000/api/leads/{lead_id}/schedule-sequence \
  -H "Content-Type: application/json" \
  -d '{
    "sequence_name": "standard"
  }'
```

### 2. Schedule a single email for tomorrow

```bash
curl -X POST http://localhost:8000/api/leads/{lead_id}/schedule-email \
  -H "Content-Type: application/json" \
  -d '{
    "email_type": "follow_up",
    "delay_minutes": 1440
  }'
```

### 3. Check scheduled emails

```bash
curl http://localhost:8000/api/leads/scheduled-emails
```

### 4. Cancel a scheduled email

```bash
curl -X DELETE http://localhost:8000/api/leads/scheduled-emails/{job_id}
```

## Email Templates

All emails are sent as HTML with professional formatting. Templates are defined in `/backend/app/services/email_service.py`.

### Customizing Templates

Edit the `html_content` in each email method:

```python
# backend/app/services/email_service.py

def send_initial_contact(self, lead_data: dict) -> dict:
    subject = f"Great to connect, {first_name}!"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <!-- Your custom template here -->
    </body>
    </html>
    """
```

## Calendly Integration

Update the Calendly link in `email_service.py`:

```python
def send_demo_invite(self, lead_data: dict,
                     calendly_link: str = "https://calendly.com/your-username/demo"):
    # ...
```

Or pass a custom link per call:

```python
email_service.send_demo_invite(lead, calendly_link="https://calendly.com/custom-link")
```

## Monitoring

### Check Scheduler Status

The scheduler runs in the background automatically when the FastAPI app starts. Check logs for:

```
📅 Scheduler service initialized
📧 Scheduled initial_contact email for lead abc-123 at 2025-01-15 10:00:00+00:00
✅ Scheduled initial contact email sent to user@example.com
```

### Activity Logs

All scheduled emails are logged in the lead's activity timeline:

```json
{
  "type": "email_sequence_scheduled",
  "description": "Scheduled 'standard' email sequence",
  "metadata": {
    "sequence_name": "standard",
    "total_emails": 3,
    "jobs": [...]
  }
}
```

## Troubleshooting

### Gmail SMTP Errors

**Error: "Username and Password not accepted"**
- Make sure you're using an App Password, not your regular password
- Enable 2-Step Verification first
- Create a new App Password specifically for this app

**Error: "Connection refused"**
- Check SMTP_PORT is 587 (not 465)
- Verify SMTP_HOST is smtp.gmail.com

### Scheduler Issues

**Scheduled emails not sending**
- Check that the FastAPI server is running
- The scheduler runs in-process, so server restarts will clear pending jobs
- Check logs for error messages

**Timezone issues**
- All times are in UTC
- Convert local times to UTC when scheduling

## Other SMTP Providers

### Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your_email@outlook.com
SMTP_PASSWORD=your_outlook_password
```

### SendGrid

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

### Yahoo Mail

```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your_email@yahoo.com
SMTP_PASSWORD=your_yahoo_app_password
```

## Architecture

```
┌─────────────────┐
│  API Endpoint   │  POST /api/leads/{id}/schedule-sequence
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scheduler Svc   │  Creates APScheduler jobs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  APScheduler    │  Waits until scheduled time
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Email Service  │  Sends via SMTP
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SMTP Server   │  Gmail/Outlook/etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Recipient     │
└─────────────────┘
```

## Future Enhancements

Potential improvements:
- Persistent job storage (Redis/PostgreSQL)
- Email templates in database
- A/B testing for email content
- Email analytics (open rates, click rates)
- Calendar API integration (Google Calendar, Outlook)
- SMS notifications
- Webhook events for email sent/opened
- Email preference center
- Unsubscribe management

## Support

For issues or questions:
- Check the logs in the terminal
- Review the `.env` file configuration
- Verify SMTP credentials with a test email client
- Check Gmail app password permissions
