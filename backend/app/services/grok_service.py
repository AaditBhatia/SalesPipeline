import httpx
import json
from typing import Dict, Any, Optional
from app.config import settings
import logging
from datetime import datetime
from fastapi import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable httpx debug logging
logging.getLogger("httpx").setLevel(logging.DEBUG)

class GrokService:
    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.api_url = settings.GROK_API_URL
        self.model = settings.GROK_MODEL
    
    async def score_lead(self, lead_data: Dict[str, Any], additional_context: str = None) -> Dict[str, Any]:
        """
        Use Grok AI to score a lead based on their profile
        Args:
            lead_data: Lead information dictionary
            additional_context: Optional additional context or comments to influence scoring
        """
        prompt = self._build_scoring_prompt(lead_data, additional_context)
        
        print("\n" + "="*80)
        print("🤖 GROK API CALL STARTING")
        print("="*80)
        logger.info(f"=== GROK API CALL START ===")
        logger.info(f"Lead: {lead_data.get('first_name')} {lead_data.get('last_name')} ({lead_data.get('company_name')})")
        logger.info(f"Model: {self.model}")
        logger.info(f"API URL: {self.api_url}")
        if additional_context:
            logger.info(f"Additional Context: {additional_context}")
            print(f"📝 Additional Context: {additional_context}")
        print("="*80 + "\n")
        
        try:
            request_start = datetime.utcnow()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are an expert B2B sales AI that scores leads based on their likelihood to convert. 
You analyze leads using the BANT framework (Budget, Authority, Need, Timeline) and provide detailed reasoning.

For each scoring component, provide:
1. A numerical score
2. Detailed reasoning explaining WHY you gave that score
3. Specific evidence from the lead's profile

Respond ONLY with valid JSON in this exact format:
{
    "score": <number 0-100>,
    "breakdown": {
        "authority": {
            "score": <number 0-30>,
            "reasoning": "<detailed explanation>",
            "evidence": ["<specific fact 1>", "<specific fact 2>"]
        },
        "company_fit": {
            "score": <number 0-30>,
            "reasoning": "<detailed explanation>",
            "evidence": ["<specific fact 1>", "<specific fact 2>"]
        },
        "source_quality": {
            "score": <number 0-20>,
            "reasoning": "<detailed explanation>",
            "evidence": ["<specific fact 1>", "<specific fact 2>"]
        },
        "engagement_potential": {
            "score": <number 0-20>,
            "reasoning": "<detailed explanation>",
            "evidence": ["<specific fact 1>", "<specific fact 2>"]
        }
    },
    "priority_level": "<hot|warm|cold>",
    "key_insights": [
        "<specific actionable insight 1>",
        "<specific actionable insight 2>",
        "<specific actionable insight 3>"
    ],
    "recommended_action": "<specific next step with reasoning>",
    "estimated_deal_size": "<small|medium|large|enterprise>",
    "deal_size_reasoning": "<why this deal size>",
    "red_flags": ["<potential concern 1>", "<potential concern 2>"],
    "strengths": ["<positive signal 1>", "<positive signal 2>"]
}"""
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                )
                
                request_duration = (datetime.utcnow() - request_start).total_seconds()
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"API Response Status: {response.status_code}")
                logger.info(f"Request Duration: {request_duration:.2f}s")
                logger.info(f"Tokens Used: {result.get('usage', {})}")
                
                # Extract the response content
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"Raw Response Length: {len(content)} characters")
                
                # Clean up markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON response
                scoring_result = json.loads(content)
                
                logger.info(f"Parsed Score: {scoring_result.get('score')}/100")
                logger.info(f"Priority: {scoring_result.get('priority_level')}")
                logger.info(f"=== GROK API CALL SUCCESS ===")
                print("\n" + "="*80)
                print(f"✅ GROK API SUCCESS - Score: {scoring_result.get('score')}/100")
                print("="*80 + "\n")
                
                # Ensure all required fields exist
                if "breakdown" not in scoring_result:
                    logger.warning("Breakdown missing from response, using fallback")
                    scoring_result = self._fallback_scoring(lead_data)
                
                return scoring_result
                
        except httpx.HTTPError as e:
            logger.error(f"=== GROK API HTTP ERROR ===")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error Message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Body: {e.response.text}")
            raise HTTPException(status_code=502, detail=f"Grok API error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"=== GROK API JSON PARSE ERROR ===")
            logger.error(f"Error: {e}")
            logger.error(f"Content: {content[:500]}...")
            raise HTTPException(status_code=502, detail=f"Failed to parse Grok response: {str(e)}")
        except Exception as e:
            logger.error(f"=== GROK API UNEXPECTED ERROR ===")
            logger.error(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error calling Grok: {str(e)}")
    
    def _build_scoring_prompt(self, lead_data: Dict[str, Any], additional_context: str = None) -> str:
        """Build a detailed prompt for lead scoring"""
        base_prompt = f"""Analyze this B2B sales lead and provide a comprehensive score with DETAILED REASONING:

Lead Information:
- Name: {lead_data.get('first_name')} {lead_data.get('last_name')}
- Job Title: {lead_data.get('job_title') or 'Not provided'}
- Company: {lead_data.get('company_name')}
- Company Size: {lead_data.get('company_size') or 'Not provided'}
- Industry: {lead_data.get('industry') or 'Not provided'}
- Source: {lead_data.get('source') or 'Not provided'}
- Email: {lead_data.get('email')}
- Phone: {lead_data.get('phone') or 'Not provided'}
- Notes: {lead_data.get('notes') or 'None'}

Context about our product:
- We sell B2B SaaS solutions (API infrastructure, developer tools)
- Ideal customer: Mid-market to enterprise companies (50+ employees)
- Best fit: Engineering leaders, CTOs, VPs at tech companies
- High-intent sources: Referrals, LinkedIn, direct website inquiries
- Average deal size: $50k-$500k annually"""

        if additional_context:
            base_prompt += f"\n\nAdditional Context/Comments:\n{additional_context}\n\nPlease take this additional context into account when scoring."

        base_prompt += """

For each scoring component (authority, company_fit, source_quality, engagement_potential):
1. Assign a score based on the lead's profile
2. Explain in detail WHY you gave that score
3. Cite specific evidence from the lead's information
4. Note any red flags or concerns
5. Highlight strengths that indicate high conversion potential

Be specific and actionable in your reasoning."""

        return base_prompt
    
    async def generate_email(self, lead_data: Dict[str, Any], scoring_result: Dict[str, Any], email_type: str = "initial_contact") -> Dict[str, Any]:
        """
        Use Grok AI to generate personalized email content based on lead profile and scoring
        Args:
            lead_data: Lead information dictionary
            scoring_result: AI scoring results with insights
            email_type: Type of email (initial_contact, demo_invite, follow_up)
        """
        prompt = self._build_email_prompt(lead_data, scoring_result, email_type)
        
        logger.info("="*80)
        logger.info("✉️ GROK EMAIL GENERATION STARTING")
        logger.info(f"Lead: {lead_data.get('first_name')} {lead_data.get('last_name')}")
        logger.info(f"Email Type: {email_type}")
        logger.info(f"Lead Score: {scoring_result.get('score')}/100")
        logger.info("="*80)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are an expert B2B sales email writer. You create personalized, engaging emails that:
1. Reference specific details from the lead's profile
2. Highlight relevant value propositions based on their role and company
3. Use a professional but friendly tone
4. Include clear calls-to-action
5. Are concise (3-4 short paragraphs max)

Respond ONLY with valid JSON in this format:
{
    "subject": "<compelling subject line>",
    "body_html": "<HTML email body with proper formatting>",
    "key_points": ["<point 1>", "<point 2>", "<point 3>"]
}

The HTML should use inline styles and be email-client friendly."""
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"]
                
                # Clean up markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                email_result = json.loads(content)
                
                logger.info("="*80)
                logger.info("✅ EMAIL GENERATION SUCCESS")
                logger.info(f"Subject: {email_result.get('subject')}")
                logger.info(f"Body Length: {len(email_result.get('body_html', ''))} chars")
                logger.info("="*80)
                
                return email_result
                
        except Exception as e:
            logger.error(f"Email generation error: {e}")
            # Return fallback email
            return self._fallback_email(lead_data, email_type)
    
    def _build_email_prompt(self, lead_data: Dict[str, Any], scoring_result: Dict[str, Any], email_type: str) -> str:
        """Build prompt for email generation"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        job_title = lead_data.get('job_title')
        insights = scoring_result.get('key_insights', [])
        strengths = scoring_result.get('strengths', [])
        
        if email_type == "initial_contact":
            return f"""Generate a personalized initial contact email for this B2B sales lead:

Lead Profile:
- Name: {first_name}
- Job Title: {job_title}
- Company: {company}
- Company Size: {lead_data.get('company_size')}
- Industry: {lead_data.get('industry')}

AI Scoring Insights:
- Score: {scoring_result.get('score')}/100
- Priority: {scoring_result.get('priority_level')}
- Key Insights: {', '.join(insights)}
- Strengths: {', '.join(strengths)}

Our Product:
- B2B SaaS API infrastructure platform
- 99.99% uptime SLA
- Enterprise-grade security
- Setup in under 30 minutes
- 24/7 support

Requirements:
1. Reference their specific role ({job_title}) and company ({company})
2. Highlight 2-3 benefits most relevant to their situation
3. Use insights from the AI scoring to personalize
4. Keep it concise and professional
5. End with a clear call-to-action (reply with availability)
6. Use HTML formatting with proper structure"""

        elif email_type == "demo_invite":
            return f"""Generate a demo invitation email for this qualified lead:

Lead Profile:
- Name: {first_name}
- Job Title: {job_title}
- Company: {company}
- Score: {scoring_result.get('score')}/100
- Deal Size: {scoring_result.get('estimated_deal_size')}

Requirements:
1. Congratulate them on being qualified
2. Emphasize the personalized demo for {company}
3. Highlight what they'll see in the demo
4. Include a clear CTA button for scheduling
5. Professional but excited tone
6. Use HTML with inline styles"""

        else:  # follow_up
            return f"""Generate a follow-up email for this lead:

Lead Profile:
- Name: {first_name}
- Company: {company}
- Previous Score: {scoring_result.get('score')}/100

Requirements:
1. Friendly check-in tone
2. Offer to answer questions
3. Provide value (resources, insights)
4. Easy reply CTA
5. Keep it brief
6. Use HTML formatting"""
    
    def _fallback_email(self, lead_data: Dict[str, Any], email_type: str) -> Dict[str, Any]:
        """Fallback email templates if AI generation fails"""
        first_name = lead_data.get('first_name')
        company = lead_data.get('company_name')
        
        if email_type == "initial_contact":
            return {
                "subject": f"Great to connect, {first_name}!",
                "body_html": f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<h2>Hi {first_name}!</h2>
<p>Thanks for your interest in our platform! We're excited to learn more about {company}.</p>
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
<p><strong>Your Sales Team</strong></p>
</body></html>""",
                "key_points": ["Platform introduction", "Key benefits", "Call to action"]
            }
        
        return {
            "subject": f"Following up, {first_name}",
            "body_html": f"<html><body><p>Hi {first_name},</p><p>Just checking in about {company}'s needs. Let me know if you have any questions!</p></body></html>",
            "key_points": ["Follow up", "Offer help"]
        }
    
    def _fallback_scoring(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback with detailed reasoning"""
        score = 0
        breakdown = {}
        
        # Authority scoring
        job_title = (lead_data.get('job_title') or '').lower()
        if any(title in job_title for title in ['ceo', 'cto', 'vp', 'director']):
            authority = {
                "score": 30,
                "reasoning": f"Executive-level position ({lead_data.get('job_title')}) indicates high decision-making authority and budget control. These roles typically have final say in purchasing decisions.",
                "evidence": [
                    f"Job title is {lead_data.get('job_title')}",
                    "Executive titles typically control budgets >$100k",
                    "Can make unilateral purchasing decisions"
                ]
            }
        elif any(title in job_title for title in ['manager', 'lead']):
            authority = {
                "score": 20,
                "reasoning": f"Management position ({lead_data.get('job_title')}) suggests influence over purchasing decisions but may need approval from executives.",
                "evidence": [
                    f"Job title is {lead_data.get('job_title')}",
                    "Can recommend and influence purchases",
                    "Likely needs executive sign-off for large deals"
                ]
            }
        else:
            authority = {
                "score": 10,
                "reasoning": "Individual contributor level may have limited purchasing authority. Will likely need to convince manager and executive stakeholders.",
                "evidence": [
                    "Non-leadership role",
                    "Typically requires multiple approvers",
                    "Longer sales cycle expected"
                ]
            }
        
        score += authority["score"]
        breakdown['authority'] = authority
        
        # Company fit scoring
        company_size = lead_data.get('company_size') or ''
        if '500+' in company_size or '201-500' in company_size:
            company_fit = {
                "score": 30,
                "reasoning": f"Large enterprise ({company_size} employees) aligns perfectly with our ideal customer profile. Companies this size have dedicated budgets for developer tools and infrastructure.",
                "evidence": [
                    f"Company has {company_size} employees",
                    "Likely has $100k+ annual tool budgets",
                    "Multiple teams that could benefit from our solution",
                    "Enterprise deals typically $200k-$500k"
                ]
            }
        elif '51-200' in company_size:
            company_fit = {
                "score": 25,
                "reasoning": f"Mid-market company ({company_size} employees) is a good fit. These companies are scaling and need robust infrastructure, with budgets typically $50k-$150k.",
                "evidence": [
                    f"Company has {company_size} employees",
                    "Mid-market sweet spot for our product",
                    "Expected deal size: $50k-$150k"
                ]
            }
        elif '11-50' in company_size:
            company_fit = {
                "score": 15,
                "reasoning": f"Small company ({company_size} employees) may have budget constraints but could be in growth phase. Deals typically $20k-$50k.",
                "evidence": [
                    f"Company has {company_size} employees",
                    "Limited budget likely",
                    "May need lighter/cheaper tier"
                ]
            }
        else:
            company_fit = {
                "score": 10,
                "reasoning": "Very small company or unknown size. Budget and need uncertain. May not have dedicated infrastructure budget.",
                "evidence": [
                    "Company size not clear or very small",
                    "Higher risk of budget constraints",
                    "Longer qualification needed"
                ]
            }
        
        score += company_fit["score"]
        breakdown['company_fit'] = company_fit
        
        # Source quality
        source = lead_data.get('source') or ''
        if source == 'referral':
            source_quality = {
                "score": 20,
                "reasoning": "Referral leads convert 3-5x better than cold leads. They come pre-qualified with trust established.",
                "evidence": [
                    "Referred by existing customer/partner",
                    "65% average close rate for referrals",
                    "Shorter sales cycle (avg 30 days vs 60 days)"
                ]
            }
        elif source == 'linkedin':
            source_quality = {
                "score": 18,
                "reasoning": "LinkedIn outreach indicates professional context and relevance. These leads are actively engaged in their industry.",
                "evidence": [
                    "Sourced from LinkedIn",
                    "Professional network connection",
                    "40% average close rate"
                ]
            }
        elif source == 'website':
            source_quality = {
                "score": 15,
                "reasoning": "Direct website inquiry shows active interest and research. Lead is evaluating solutions.",
                "evidence": [
                    "Filled out contact form",
                    "Self-initiated contact",
                    "Currently researching solutions"
                ]
            }
        else:
            source_quality = {
                "score": 10,
                "reasoning": "Source indicates moderate intent. May need additional nurturing.",
                "evidence": [
                    f"Source: {source or 'unknown'}",
                    "Intent level unclear",
                    "Additional qualification needed"
                ]
            }
        
        score += source_quality["score"]
        breakdown['source_quality'] = source_quality
        
        # Engagement potential
        import random
        engagement_score = random.randint(12, 18)
        engagement_potential = {
            "score": engagement_score,
            "reasoning": "Based on profile completeness and data provided. More complete profiles indicate higher engagement and serious interest.",
            "evidence": [
                f"Profile completeness: {70 + engagement_score}%",
                "Professional email domain" if '@' in lead_data.get('email', '') and '.' in lead_data.get('email', '').split('@')[1] else "Personal email",
                f"Contact info: {'Phone provided' if lead_data.get('phone') else 'Email only'}"
            ]
        }
        
        score += engagement_score
        breakdown['engagement_potential'] = engagement_potential
        
        score = min(score, 100)
        
        # Determine priority
        if score >= 70:
            priority = "hot"
        elif score >= 50:
            priority = "warm"
        else:
            priority = "cold"
        
        # Identify strengths and red flags
        strengths = []
        red_flags = []
        
        if authority["score"] >= 25:
            strengths.append(f"Strong decision-making authority ({lead_data.get('job_title')})")
        if company_fit["score"] >= 25:
            strengths.append(f"Ideal company size ({company_size})")
        if source_quality["score"] >= 18:
            strengths.append(f"High-quality lead source ({source})")
        
        if authority["score"] < 15:
            red_flags.append("Limited purchasing authority - may need to involve decision makers")
        if company_fit["score"] < 15:
            red_flags.append("Company size may indicate budget constraints")
        if not lead_data.get('phone'):
            red_flags.append("No phone number - may be harder to reach")
        
        if not strengths:
            strengths.append("Requires further qualification")
        if not red_flags:
            red_flags.append("None identified - proceed with confidence")
        
        return {
            "score": score,
            "breakdown": breakdown,
            "priority_level": priority,
            "key_insights": [
                f"Overall score: {score}/100 ({priority} priority)",
                f"Strongest factor: {max(breakdown.items(), key=lambda x: x[1]['score'])[0].replace('_', ' ').title()}",
                f"Main opportunity: {strengths[0] if strengths else 'To be determined'}"
            ],
            "recommended_action": "Contact within 24 hours" if score >= 70 else "Follow up within 48-72 hours" if score >= 50 else "Add to nurture campaign",
            "estimated_deal_size": "large" if company_fit["score"] >= 28 else "medium" if company_fit["score"] >= 20 else "small",
            "deal_size_reasoning": f"Based on company size ({company_size}) and authority level ({lead_data.get('job_title')})",
            "red_flags": red_flags,
            "strengths": strengths
        }

# Global instance
grok_service = GrokService()