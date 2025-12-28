# Add Email Automation and Demo Scheduling Integration

## Summary

This PR adds comprehensive email automation and demo scheduling capabilities to the Sales Pipeline application.

### Key Features

#### 1. SMTP Email Integration
- ✅ Replaced Resend with SMTP for broader compatibility
- ✅ No domain verification required
- ✅ Works with Gmail, Outlook, Yahoo, SendGrid, and other SMTP providers
- ✅ Async email sending for better performance
- ✅ Configured for Gmail: `aadit.bhatia93@gmail.com`

#### 2. Background Task Scheduler
- ✅ APScheduler integration for delayed and scheduled emails
- ✅ Schedule emails for specific times or with delays
- ✅ Job management (create, cancel, list)

#### 3. Email Sequences (Drip Campaigns)
Three pre-configured sequences:
- **Standard**: Initial → 2 days → Follow-up → 3 days → Demo (5 days total)
- **Aggressive**: Initial → 1 day → Follow-up → 1 day → Demo (2 days total)
- **Nurture**: Initial → 3 days → Follow-up → 7 days → Follow-up → 7 days → Demo (17 days)

#### 4. Demo Scheduling
- ✅ Calendly integration for demo scheduling
- ✅ Automated demo invitation emails
- ✅ Configurable scheduling links

## New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/leads/{id}/schedule-email` | POST | Schedule a single email |
| `/api/leads/{id}/schedule-sequence` | POST | Schedule a drip campaign |
| `/api/leads/scheduled-emails` | GET | List all scheduled emails |
| `/api/leads/{id}/scheduled-emails` | GET | Get lead's scheduled emails |
| `/api/leads/scheduled-emails/{job_id}` | DELETE | Cancel scheduled email |

## Files Changed

### New Files
- `backend/app/services/scheduler_service.py` - Email scheduling service
- `backend/.env.example` - Environment configuration template
- `EMAIL_AUTOMATION.md` - Complete setup and usage documentation

### Modified Files
- `backend/requirements.txt` - Added APScheduler, pytz, aiosmtplib
- `backend/app/config/settings.py` - SMTP configuration
- `backend/app/services/email_service.py` - SMTP implementation
- `backend/app/api/leads.py` - New scheduler endpoints

### Removed Files
- `backend/app/Config.py` - Legacy Resend configuration (no longer needed)

## Configuration Required

To use this feature, you need to set up Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create an app password for "Mail"
5. Add to `.env`:
   ```env
   SMTP_PASSWORD=your_16_char_app_password_here
   ```

See `backend/.env.example` and `EMAIL_AUTOMATION.md` for complete setup instructions.

## Testing

To test the email automation:

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Configure .env with Gmail App Password
cp .env.example .env
# Edit .env and add SMTP_PASSWORD

# Start server
uvicorn app.main:app --reload

# Create a lead and schedule an email sequence
curl -X POST http://localhost:8000/api/leads/{lead_id}/schedule-sequence \
  -H "Content-Type: application/json" \
  -d '{"sequence_name": "standard"}'
```

## Breaking Changes

None - this is a new feature addition. Existing functionality remains unchanged.

## Documentation

- ✅ `EMAIL_AUTOMATION.md` - Complete feature documentation
- ✅ `backend/.env.example` - Configuration examples
- ✅ API endpoint documentation in docstrings
- ✅ Email sequence timing documentation

## Future Enhancements

Potential improvements mentioned in documentation:
- Persistent job storage (Redis/PostgreSQL)
- Email templates in database
- A/B testing for email content
- Email analytics (open rates, click rates)
- Calendar API integration (Google Calendar, Outlook)
- SMS notifications
- Webhook events
- Email preference center

---

**Ready for review and testing!** 🚀
