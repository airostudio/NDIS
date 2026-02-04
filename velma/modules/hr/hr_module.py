"""
HR Module - NDIS Compliance and Worker Management
Handles all HR functions with NDIS-specific requirements
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from anthropic import AsyncAnthropic

from ...utils.logger import get_logger
from ...utils.validators import (
    validate_worker_screening_check,
    validate_tfn,
    validate_email,
    validate_phone
)

logger = get_logger(__name__)


class HRModule:
    """
    NDIS HR & Compliance Module

    Manages:
    - Worker screening and credentialing
    - Onboarding and offboarding
    - Compliance tracking (WWCC, First Aid, etc.)
    - Incident reporting
    - Performance management
    """

    def __init__(self, config):
        """
        Initialize HR module

        Args:
            config: Application configuration
        """
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)

        # Compliance requirements for NDIS workers
        self.required_compliance_items = [
            {
                "name": "NDIS Worker Screening Check",
                "code": "NDIS_WSC",
                "expiry_warning_days": 30,
                "mandatory": True
            },
            {
                "name": "Working with Children Check",
                "code": "WWCC",
                "expiry_warning_days": 30,
                "mandatory": True
            },
            {
                "name": "First Aid Certificate",
                "code": "FIRST_AID",
                "expiry_warning_days": 60,
                "mandatory": True
            },
            {
                "name": "CPR Certificate",
                "code": "CPR",
                "expiry_warning_days": 60,
                "mandatory": True
            },
            {
                "name": "Police Check",
                "code": "POLICE_CHECK",
                "expiry_warning_days": 90,
                "mandatory": True
            },
            {
                "name": "NDIS Worker Orientation Module",
                "code": "NDIS_ORIENTATION",
                "expiry_warning_days": None,  # Doesn't expire
                "mandatory": True
            },
        ]

        logger.info("HR Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process HR-related request

        Args:
            message: User message
            intent: Classified intent
            context: Session context

        Returns:
            Response dictionary
        """
        logger.info(f"Processing HR request: {message[:100]}")

        # Extract HR-specific intent
        hr_action = await self._determine_hr_action(message, intent)

        # Route to appropriate handler
        handlers = {
            "worker_screening": self._handle_worker_screening,
            "compliance_check": self._handle_compliance_check,
            "onboarding": self._handle_onboarding,
            "incident_report": self._handle_incident_report,
            "performance": self._handle_performance,
            "document_request": self._handle_document_request,
            "expiry_check": self._check_expiring_credentials,
            "general": self._handle_general_hr_query,
        }

        handler = handlers.get(hr_action, self._handle_general_hr_query)
        return await handler(message, intent, context)

    async def _determine_hr_action(
        self,
        message: str,
        intent: Dict[str, Any]
    ) -> str:
        """
        Determine specific HR action from message

        Args:
            message: User message
            intent: Intent data

        Returns:
            HR action type
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["screening", "yellow card", "wsc"]):
            return "worker_screening"
        elif any(word in message_lower for word in ["compliance", "expiring", "expiry", "wwcc", "first aid"]):
            return "compliance_check"
        elif any(word in message_lower for word in ["onboard", "new hire", "new employee", "new worker"]):
            return "onboarding"
        elif any(word in message_lower for word in ["incident", "accident", "injury", "report"]):
            return "incident_report"
        elif any(word in message_lower for word in ["performance", "review", "appraisal"]):
            return "performance"
        elif any(word in message_lower for word in ["document", "form", "paperwork", "certificate"]):
            return "document_request"
        elif any(word in message_lower for word in ["expir", "renew", "due"]):
            return "expiry_check"
        else:
            return "general"

    async def _handle_worker_screening(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle NDIS Worker Screening Check queries"""

        system_prompt = """You are an HR specialist for an NDIS company.
        Help with NDIS Worker Screening Check (Yellow Card) queries.

        Key information:
        - NDIS Worker Screening Check is mandatory for all NDIS workers
        - Valid for 5 years from issue date
        - Different from WWC Check (both may be required)
        - Must be applied for in the state where work is performed
        - Costs vary by state (~$80-$120)
        - Takes 2-8 weeks to process

        Provide accurate, helpful information and next steps.
        """

        response = await self.ai_client.messages.create(
            model=self.config.ai_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        return {
            "status": "success",
            "message": response.content[0].text,
            "action": "inform",
            "module": "hr",
            "hr_action": "worker_screening"
        }

    async def _handle_compliance_check(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance status for workers"""

        # In production, this would query the database
        # For now, provide information about compliance requirements

        response = f"""**NDIS Worker Compliance Requirements**

All NDIS workers must maintain current:

1. **NDIS Worker Screening Check (Yellow Card)**
   - Valid for 5 years
   - Warning at 30 days before expiry

2. **Working with Children Check (WWCC)**
   - Valid for 5 years (varies by state)
   - Warning at 30 days before expiry

3. **First Aid Certificate**
   - Valid for 3 years
   - Warning at 60 days before expiry

4. **CPR Certificate**
   - Valid for 12 months
   - Warning at 60 days before expiry

5. **Police Check**
   - Valid for 3 years
   - Warning at 90 days before expiry

6. **NDIS Worker Orientation Module**
   - One-time completion required
   - Available free online via NDIS Commission website

**Automatic Reminders:**
Velma automatically sends reminders when credentials are approaching expiry.

Would you like me to:
- Check specific employee compliance status?
- Generate a compliance report for all staff?
- Set up automatic renewal reminders?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "hr",
            "hr_action": "compliance_check"
        }

    async def _handle_onboarding(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle new employee onboarding"""

        onboarding_checklist = """**NDIS Employee Onboarding Checklist**

**Pre-Employment (Week -2 to -1):**
- [ ] Job offer letter sent and accepted
- [ ] NDIS Worker Screening Check verified
- [ ] Working with Children Check verified
- [ ] Police Check completed (within 3 years)
- [ ] First Aid & CPR certificates verified
- [ ] Employment contract signed
- [ ] Tax File Number Declaration completed
- [ ] Superannuation choice form completed
- [ ] Banking details collected

**NDIS Worker Orientation (Week -1):**
- [ ] NDIS Worker Orientation Module completed online
- [ ] Certificate of completion obtained
- [ ] NDIS Code of Conduct reviewed and signed
- [ ] Privacy and confidentiality agreement signed

**First Day (Day 1):**
- [ ] Welcome meeting scheduled
- [ ] IT systems access set up
- [ ] Company policies handbook provided
- [ ] Emergency procedures explained
- [ ] Workplace tour completed

**First Week (Week 1):**
- [ ] SCHADS Award classification confirmed
- [ ] Pay rate and penalty rates explained
- [ ] Roster and availability confirmed
- [ ] Initial training sessions scheduled
- [ ] Meet key team members
- [ ] Shadow experienced worker

**First Month (Weeks 2-4):**
- [ ] Competency assessments completed
- [ ] Client matching process explained
- [ ] First participant shift supervised
- [ ] Incident reporting process trained
- [ ] Progress check-in meeting
- [ ] Documentation requirements clarified

**Ongoing:**
- [ ] 90-day probation review scheduled
- [ ] Annual performance review planned
- [ ] Continuous professional development tracked

Would you like me to:
- Create an onboarding plan for a specific employee?
- Send automated reminders for checklist items?
- Generate required onboarding documents?
"""

        return {
            "status": "success",
            "message": onboarding_checklist,
            "action": "inform",
            "module": "hr",
            "hr_action": "onboarding",
            "next_steps": ["create_plan", "send_reminders", "generate_docs"]
        }

    async def _handle_incident_report(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incident reporting"""

        # Check urgency
        is_emergency = any(word in message.lower() for word in ["emergency", "urgent", "immediate", "serious"])

        if is_emergency:
            response = """**URGENT INCIDENT DETECTED**

For immediate medical emergencies, call 000.

I've escalated this incident to your HR Manager and the incident response team.

Please provide the following information:
1. Date and time of incident
2. Location
3. People involved (staff and/or participants)
4. Nature of incident
5. Injuries or damage
6. Immediate actions taken
7. Witnesses

This information will be used to complete the mandatory NDIS incident report.

**NDIS Reportable Incidents:**
The following must be reported to the NDIS Commission within 24 hours:
- Death of a participant
- Serious injury or illness
- Abuse or neglect
- Unlawful sexual or physical contact
- Unauthorized use of restrictive practices

An incident manager will contact you within 15 minutes.
"""
        else:
            response = """**NDIS Incident Reporting**

I can help you document and report this incident.

**Incident Categories:**
1. **Reportable to NDIS Commission (within 24 hours):**
   - Death or serious injury
   - Abuse or neglect
   - Unauthorized restrictive practices
   - Unlawful contact

2. **Internal Incidents:**
   - Minor injuries
   - Near misses
   - Property damage
   - Policy violations
   - Client complaints

Please provide:
- Date and time
- Location
- People involved
- Description of what happened
- Any injuries or damage
- Actions taken

I'll help complete the appropriate incident form and notify relevant parties.
"""

        # Log incident initiation
        logger.warning(f"Incident report initiated: {message[:100]}")

        return {
            "status": "success" if not is_emergency else "urgent",
            "message": response,
            "action": "escalate" if is_emergency else "collect_info",
            "module": "hr",
            "hr_action": "incident_report",
            "is_emergency": is_emergency
        }

    async def _handle_performance(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle performance management queries"""

        response = """**NDIS Worker Performance Management**

**Performance Review Schedule:**
- Probation Review: 90 days after start
- Annual Performance Review: Yearly
- Informal Check-ins: Quarterly

**Key Performance Areas for NDIS Workers:**
1. **Participant Care & Support**
   - Quality of care delivery
   - Person-centered approach
   - Goal achievement support

2. **Compliance & Documentation**
   - Accurate shift notes
   - Timely reporting
   - Adherence to care plans

3. **Professional Conduct**
   - NDIS Code of Conduct compliance
   - Respectful communication
   - Reliability and punctuality

4. **Safety & Risk Management**
   - WHS compliance
   - Incident prevention
   - Proper use of equipment

5. **Teamwork & Communication**
   - Collaboration with team
   - Handover quality
   - Responsiveness

**Performance Improvement:**
If performance issues arise, we follow:
1. Informal discussion and coaching
2. Formal performance improvement plan (PIP)
3. Regular progress reviews
4. Outcome assessment

Would you like me to:
- Schedule a performance review?
- Generate performance review templates?
- Create a performance improvement plan?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "hr",
            "hr_action": "performance"
        }

    async def _handle_document_request(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle requests for HR documents"""

        response = """**Available HR Documents**

**Employment Documents:**
- Letter of Offer template
- Employment Contract (Casual/Permanent)
- Position Description templates
- Tax File Number Declaration
- Superannuation Choice Form

**NDIS Compliance:**
- NDIS Code of Conduct acknowledgment
- NDIS Worker Orientation completion form
- Worker Screening Check verification form
- Privacy and Confidentiality agreement

**Policies & Procedures:**
- Staff Handbook
- WHS Policy
- Incident Reporting Procedure
- Code of Conduct Policy
- Privacy Policy
- Complaints Handling Procedure

**Forms:**
- Leave application form
- Timesheet template
- Expense reimbursement form
- Incident report form
- Performance review form

Which document do you need? I can generate it or send you the template.
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "hr",
            "hr_action": "document_request"
        }

    async def _check_expiring_credentials(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for expiring worker credentials"""

        # In production, would query database
        # For demonstration, show what would be checked

        response = """**Credential Expiry Monitoring**

Velma automatically monitors the following credentials and sends reminders:

**30 Days Before Expiry:**
- NDIS Worker Screening Checks
- Working with Children Checks

**60 Days Before Expiry:**
- First Aid Certificates
- CPR Certificates

**90 Days Before Expiry:**
- Police Checks (3-year validity)

**Automatic Actions:**
1. Email reminder to employee
2. Notification to HR manager
3. Calendar reminder created
4. Follow-up if not renewed 7 days before expiry
5. Rostering alert if expired (cannot work)

**Current Status:**
To check specific employee credentials or generate an expiry report for all staff,
please provide:
- Employee name/ID, or
- "All staff" for full report

I can also set up custom reminder schedules if needed.
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "hr",
            "hr_action": "expiry_check"
        }

    async def _handle_general_hr_query(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general HR queries with AI"""

        system_prompt = """You are an HR specialist for an NDIS service provider in Australia.

        Provide accurate information about:
        - NDIS-specific employment requirements
        - SCHADS Award conditions
        - Worker screening and compliance
        - Onboarding and offboarding
        - Performance management
        - Incident reporting
        - WHS compliance
        - Australian employment law

        Be professional, accurate, and helpful. If unsure, recommend consulting with HR manager or legal advisor.
        """

        response = await self.ai_client.messages.create(
            model=self.config.ai_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )

        return {
            "status": "success",
            "message": response.content[0].text,
            "action": "inform",
            "module": "hr",
            "hr_action": "general"
        }

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("HR Module shutting down")
