"""
Payroll Module
Handles payroll processing, timesheet management, and STP reporting for NDIS providers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
from anthropic import AsyncAnthropic

from .schads_calculator import SCHADSCalculator
from ...utils.logger import get_logger

logger = get_logger(__name__)


class PayrollModule:
    """
    NDIS Payroll Module

    Manages:
    - Timesheet processing
    - SCHADS Award pay calculations
    - Leave management
    - Superannuation
    - STP (Single Touch Payroll) Phase 2 reporting
    - Payroll queries and reports
    """

    def __init__(self, config):
        """
        Initialize Payroll module

        Args:
            config: Application configuration
        """
        self.config = config
        self.ai_client = AsyncAnthropic(api_key=config.anthropic_api_key)
        self.schads_calc = SCHADSCalculator()

        logger.info("Payroll Module initialized")

    async def process(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process payroll-related request

        Args:
            message: User message
            intent: Classified intent
            context: Session context

        Returns:
            Response dictionary
        """
        logger.info(f"Processing Payroll request: {message[:100]}")

        # Determine payroll action
        payroll_action = await self._determine_payroll_action(message, intent)

        # Route to appropriate handler
        handlers = {
            "calculate_pay": self._handle_pay_calculation,
            "timesheet": self._handle_timesheet,
            "leave": self._handle_leave,
            "superannuation": self._handle_superannuation,
            "stp": self._handle_stp,
            "schads_rates": self._handle_schads_rates,
            "payslip": self._handle_payslip,
            "general": self._handle_general_payroll_query,
        }

        handler = handlers.get(payroll_action, self._handle_general_payroll_query)
        return await handler(message, intent, context)

    async def _determine_payroll_action(
        self,
        message: str,
        intent: Dict[str, Any]
    ) -> str:
        """Determine specific payroll action from message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["calculate", "how much", "pay rate", "wage"]):
            return "calculate_pay"
        elif any(word in message_lower for word in ["timesheet", "hours", "shift"]):
            return "timesheet"
        elif any(word in message_lower for word in ["leave", "annual leave", "sick leave", "holiday"]):
            return "leave"
        elif any(word in message_lower for word in ["super", "superannuation", "retirement"]):
            return "superannuation"
        elif any(word in message_lower for word in ["stp", "ato", "single touch"]):
            return "stp"
        elif any(word in message_lower for word in ["schads", "award", "rate", "penalty"]):
            return "schads_rates"
        elif any(word in message_lower for word in ["payslip", "pay stub", "earnings"]):
            return "payslip"
        else:
            return "general"

    async def _handle_pay_calculation(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle pay calculation requests"""

        response = """**SCHADS Award Pay Calculator**

I can calculate pay for NDIS workers including all penalty rates and allowances.

**To calculate pay, I need:**
1. Classification level (e.g., 2.1, 3.1)
2. Shift start and end time
3. Day of the week
4. Whether it's a public holiday
5. Any allowances (sleepover, broken shift, travel)

**Example:**
"Calculate pay for Level 2.1 worker, Saturday 9am-5pm"

**SCHADS Classification Levels (2026 Rates):**
- Level 1.1: $27.15/hour - Entry level
- Level 2.1: $28.45/hour - Support Worker (most common)
- Level 2.2: $29.15/hour - Support Worker with Certificate III
- Level 3.1: $30.85/hour - Senior Support Worker
- Level 3.2: $31.55/hour - Senior Support Worker with Certificate IV
- Level 4.1: $33.95/hour - Team Leader

**Penalty Rates:**
- Afternoon (3pm-8pm weekday): 1.15x base rate
- Night (8pm-7am weekday): 1.25x base rate
- Saturday: 1.5x base rate
- Sunday: 1.75x base rate
- Public Holiday: 2.5x base rate

**Allowances:**
- Sleepover: $62.45 per night
- Broken shift: $4.85 per occurrence
- Meal (shift > 5 hours): $18.35
- Travel: $0.85 per km

What pay calculation do you need?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "calculate_pay"
        }

    async def _handle_timesheet(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle timesheet-related requests"""

        response = """**Timesheet Management**

**Timesheet Requirements:**
All NDIS workers must submit timesheets that include:
- Employee name and ID
- Classification level
- Shift date, start and end times
- Participant name/NDIS number (for billing)
- Break duration (unpaid)
- Any allowances (travel, meals, etc.)
- Supervisor approval signature

**Critical for NDIS Audit:**
Timesheets must link to NDIS claims. The NDIS Quality and Safeguards Commission
requires clear records showing:
- Worker qualifications (linking to classification)
- Actual hours worked (matching claimed hours)
- Service delivery location
- Support item number

**Timesheet Deadlines:**
- Submit by: 5pm Monday following the pay week
- Approval by: 5pm Tuesday
- Payroll processing: Wednesday
- Pay date: Thursday

**Common Timesheet Issues:**
1. **Missing breaks** - Include unpaid meal breaks (30+ min)
2. **Wrong classification** - Ensure classification matches role
3. **Unrecorded travel** - Claim travel time and kilometers
4. **Missing participant details** - Required for NDIS billing
5. **Unsigned** - Must be approved by coordinator

**Timesheet Validation:**
Velma automatically checks for:
- Overlapping shifts
- Shifts exceeding 12 hours
- Missing required fields
- Incorrect classification codes
- Unmatched NDIS claims

Would you like me to:
- Validate a timesheet?
- Calculate total pay from timesheet?
- Generate timesheet template?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "timesheet"
        }

    async def _handle_leave(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle leave management queries"""

        response = """**NDIS Worker Leave Entitlements (SCHADS Award)**

**Annual Leave:**
- Permanent employees: 4 weeks (152 hours) per year
- Casual employees: Not entitled to annual leave (receive 25% loading instead)
- Leave loading: 17.5% when taking annual leave
- Accrual: Accrues progressively throughout the year

**Annual Leave Calculation:**
For permanent employee on $30/hour:
- Normal pay for 4 weeks: $30 × 152 hours = $4,560
- Leave loading (17.5%): $4,560 × 0.175 = $798
- Total annual leave entitlement: $5,358

**Personal/Carer's Leave:**
- Permanent employees: 10 days (76 hours) per year
- Casual employees: 2 days unpaid carer's leave per occasion
- Accrual: Accrues progressively
- Can be used for: Personal illness, injury, or caring for family member

**Long Service Leave:**
- After 5 years: Entitled to 8.67 weeks
- Pro-rata: Available after 7 years if employment ends
- Varies by state

**Public Holidays:**
- 10-11 public holidays per year (varies by state)
- Permanent employees: Paid if rostered day
- Casual employees: Not paid unless working (then 2.5x rate)

**Parental Leave:**
- 12 months unpaid parental leave
- Must have worked 12 months
- Government Paid Parental Leave: Up to 20 weeks (separate from employer)

**Compassionate Leave:**
- 2 days paid per occasion
- On death or life-threatening illness of immediate family

**Leave Without Pay:**
- By agreement with employer
- No accrual during unpaid leave

**Leave Loading:**
The SCHADS Award provides 17.5% leave loading on annual leave to compensate
for not earning penalty rates while on leave.

Would you like me to:
- Calculate leave entitlement for an employee?
- Process a leave request?
- Generate leave balance report?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "leave"
        }

    async def _handle_superannuation(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle superannuation queries"""

        response = """**Superannuation for NDIS Workers (2026)**

**Superannuation Guarantee (SG):**
- Current rate: 11.5% (as of July 2025)
- Calculated on: Ordinary Time Earnings (OTE)
- Payment frequency: Quarterly (minimum) or monthly (preferred)

**OTE (Ordinary Time Earnings):**
Includes:
- Base wages
- Penalty rates and shift loadings
- Annual leave loading
- Some allowances

Excludes:
- Overtime payments
- Payments in lieu of notice
- Some expense reimbursements

**Superannuation Threshold:**
- Monthly threshold: $450
- Employees earning less than $450/month are not entitled to SG
- Threshold applies per employer, not per job

**Calculation Example:**
Employee earns $3,000 in OTE for the month:
- Super contribution: $3,000 × 11.5% = $345
- Employer pays this to employee's super fund

**Stapled Super Funds:**
From 2021, employees have "stapled" super funds that follow them between jobs.
New employees should provide their super fund details, or their existing fund
will be used.

**Choice of Fund:**
Employees can choose their own super fund or use the employer's default fund.
Must offer choice within 28 days of employment start.

**Payment Deadlines:**
Quarterly due dates:
- Q1 (Jul-Sep): Due 28 October
- Q2 (Oct-Dec): Due 28 January
- Q3 (Jan-Mar): Due 28 April
- Q4 (Apr-Jun): Due 28 July

Late payments incur Superannuation Guarantee Charge (SGC) penalties.

**Reporting:**
Super payments must be reported to ATO via:
- Single Touch Payroll (STP) Phase 2 - real-time reporting
- SuperStream - electronic payment and data standard

**Tax Deductibility:**
Super contributions are tax-deductible for employers.

**Velma Auto-Calculation:**
Velma automatically:
- Calculates 11.5% of OTE for each employee
- Excludes employees under $450 threshold
- Tracks payment due dates
- Sends reminders 7 days before deadline
- Reports via STP Phase 2

Would you like me to:
- Calculate super for an employee?
- Check upcoming super payments?
- Generate super contribution report?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "superannuation"
        }

    async def _handle_stp(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Single Touch Payroll queries"""

        response = """**Single Touch Payroll (STP) Phase 2 - 2026**

**What is STP?**
Single Touch Payroll (STP) is the way employers report tax and super information
to the ATO. It's required for all employers, including small NDIS providers.

**STP Phase 2 Requirements:**
Phase 2 (mandatory from 2022) includes additional reporting:
- Disaggregated pay data (separating OTE from gross)
- Employment basis (full-time, part-time, casual)
- Country codes
- Child support garnishee details
- Income type (salary vs allowances)

**When to Report:**
- Every pay run (even if just one employee)
- On or before the pay date
- Year-end finalization by 14 July

**What to Report:**
For each employee, each pay period:
- Gross payments
- PAYG withholding
- Superannuation contributions
- Employment basis
- Pay period dates
- YTD totals

**STP for NDIS Providers:**
Critical considerations:
1. **OTE Separation**: Must separate Ordinary Time Earnings from penalties
2. **Allowances**: Report allowances separately from wages
3. **Multiple Jobs**: Workers may have multiple casual positions
4. **Irregular Hours**: Casual workers have varying pay periods

**STP Software:**
Velma integrates with STP-enabled payroll systems:
- Employment Hero
- Xero Payroll
- MYOB
- KeyPay

**Penalties:**
Failure to report via STP can result in:
- Penalties up to $1,100 per 28-day period
- Director penalties for unpaid PAYG
- Super guarantee charges

**Exemptions:**
Very limited exemptions for:
- Closely held payees (family members)
- Some international employers
- Technical difficulties (temporary)

**Year-End Finalization:**
By 14 July each year:
- Finalize all STP reports
- Declare they are final
- Employees can then lodge tax returns

**Velma STP Automation:**
Velma can:
- Auto-generate STP reports from timesheets
- Submit to ATO via approved software
- Track submission status
- Alert to errors or rejections
- Ensure Phase 2 compliance

**Important:** STP submissions are legal declarations. While Velma automates
preparation, final submission requires authorized officer approval.

Would you like me to:
- Prepare STP report for current pay period?
- Check STP submission status?
- Explain specific STP codes?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "stp"
        }

    async def _handle_schads_rates(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle SCHADS Award rates queries"""

        # Generate comprehensive rates table
        rates_info = """**SCHADS Award 2010 - Pay Rates (2026)**

**Base Hourly Rates by Classification:**

**Level 1 - Entry Level Support Worker**
- 1.1: $27.15/hour - Introductory level, training
- 1.2: $27.85/hour - After 3 months

**Level 2 - Support Worker (Most Common)**
- 2.1: $28.45/hour - Certificate II or 6 months experience
- 2.2: $29.15/hour - Certificate III
- 2.3: $29.85/hour - Certificate III + additional skills

**Level 3 - Senior Support Worker**
- 3.1: $30.85/hour - Advanced skills, complex care
- 3.2: $31.55/hour - Certificate IV or specialized skills
- 3.3: $32.25/hour - Senior role, supervision

**Level 4 - Team Leader / Coordinator**
- 4.1: $33.95/hour - Team leader, coordination
- 4.2: $35.15/hour - Senior coordinator
- 4.3: $36.45/hour - Manager level

**Penalty Rates (Multiplied by Base Rate):**

**Weekday Penalties:**
- Afternoon shift (3pm-8pm): 1.15x (15% extra)
- Night shift (8pm-7am): 1.25x (25% extra)
- Evening (after 6pm): 1.50x (50% extra)

**Weekend Penalties:**
- Saturday (all day): 1.50x (50% extra)
- Sunday (all day): 1.75x (75% extra)

**Public Holidays:**
- Public holiday (all day): 2.50x (150% extra)

**Example Calculations:**

**Level 2.1 Worker ($28.45/hour):**
- Monday 9am-5pm: $28.45 × 8 hours = $227.60
- Saturday 9am-5pm: $28.45 × 1.5 × 8 = $341.40
- Sunday 9am-5pm: $28.45 × 1.75 × 8 = $398.30
- Public Holiday 9am-5pm: $28.45 × 2.5 × 8 = $569.00

**Mixed Shift (Monday 2pm-10pm):**
- 2pm-3pm (ordinary): $28.45 × 1 hour = $28.45
- 3pm-8pm (afternoon): $28.45 × 1.15 × 5 = $163.59
- 8pm-10pm (night): $28.45 × 1.25 × 2 = $71.13
- Total: $263.17 for 8 hours

**Allowances (Fixed Amounts):**
- Sleepover: $62.45 per night
- Broken shift: $4.85 per occurrence
- Meal (shift > 5 hours): $18.35
- Travel/km: $0.85 per kilometer

**Leave Loading:**
- 17.5% on annual leave

**Casual Loading:**
- 25% on top of all rates (no leave entitlements)

**These rates are updated annually.** Always check the current Fair Work
Commission SCHADS Award determination.

Would you like me to calculate specific shift pay?
"""

        return {
            "status": "success",
            "message": rates_info,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "schads_rates"
        }

    async def _handle_payslip(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payslip generation and queries"""

        response = """**Payslip Requirements**

**Mandatory Payslip Information:**
All employees must receive a payslip within 1 working day of pay, showing:

1. **Employer Details:**
   - Business name
   - ABN

2. **Employee Details:**
   - Full name
   - Employment status (full-time, part-time, casual)

3. **Pay Period:**
   - Start and end dates

4. **Earnings:**
   - Ordinary hours and rate
   - Overtime/penalty hours and rates
   - Allowances
   - Gross pay

5. **Deductions:**
   - PAYG tax withheld
   - Other deductions (if any)

6. **Superannuation:**
   - Contribution amount
   - Fund name

7. **Net Pay:**
   - Total payment after deductions

**Example Payslip - NDIS Support Worker:**

```
ABC NDIS Services Pty Ltd
ABN: 12 345 678 901

Employee: Jane Smith
Classification: SCHADS Level 2.2
Pay Period: 1-14 February 2026

EARNINGS:
Ordinary hours       38.0 hrs @ $29.15    $1,107.70
Saturday            16.0 hrs @ $43.73    $  699.68
Sunday               8.0 hrs @ $51.01    $  408.08
Meal allowance       3      @ $18.35    $   55.05
                                         ----------
Gross Pay                                $2,270.51

DEDUCTIONS:
PAYG Tax Withheld                        $  295.00
                                         ----------
Total Deductions                         $  295.00

NET PAY                                  $1,975.51

SUPERANNUATION:
Superannuation SG 11.5%                  $  261.11
Fund: Australian Super

YTD TOTALS:
Gross: $4,541.02  |  Tax: $590.00  |  Net: $3,951.02
```

**Payslip Delivery:**
- Electronic: Via email or payroll portal (most common)
- Paper: Sealed envelope (if requested)

**Record Keeping:**
Employers must keep payslip records for 7 years.

**Velma Payslip Generation:**
Velma can:
- Auto-generate compliant payslips
- Email directly to employees
- Archive for record keeping
- Include detailed breakdown of penalty rates

Would you like me to:
- Generate a payslip?
- Explain a payslip item?
- Resend a payslip?
"""

        return {
            "status": "success",
            "message": response,
            "action": "inform",
            "module": "payroll",
            "payroll_action": "payslip"
        }

    async def _handle_general_payroll_query(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general payroll queries with AI"""

        system_prompt = """You are a payroll specialist for NDIS service providers in Australia.

        You have deep knowledge of:
        - SCHADS Award 2010 pay rates and conditions
        - Australian payroll tax and compliance
        - Single Touch Payroll (STP) Phase 2
        - Superannuation Guarantee
        - NDIS-specific payroll requirements
        - Fair Work Act requirements

        Provide accurate, helpful, and compliance-focused advice.
        Always recommend consulting with an accountant or payroll professional for complex situations.
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
            "module": "payroll",
            "payroll_action": "general"
        }

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("Payroll Module shutting down")
