"""
SCHADS Award Calculator
Calculates pay rates, penalties, and allowances according to the
Social, Community, Home Care and Disability Services Industry Award 2010
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
import math

from ...utils.logger import get_logger

logger = get_logger(__name__)


class SCHADSCalculator:
    """
    SCHADS Award Pay Calculator

    Calculates wages according to SCHADS Award 2010 including:
    - Base rates by classification level
    - Penalty rates (afternoon, night, weekend, public holiday)
    - Allowances (sleepover, broken shift, meal, travel)
    - Leave loading
    - Superannuation
    """

    # SCHADS Award Rates (2026 - Update annually)
    BASE_RATES = {
        "1.1": Decimal("27.15"),
        "1.2": Decimal("27.85"),
        "2.1": Decimal("28.45"),
        "2.2": Decimal("29.15"),
        "2.3": Decimal("29.85"),
        "3.1": Decimal("30.85"),
        "3.2": Decimal("31.55"),
        "3.3": Decimal("32.25"),
        "4.1": Decimal("33.95"),
        "4.2": Decimal("35.15"),
        "4.3": Decimal("36.45"),
    }

    # Penalty Rates (multipliers)
    PENALTIES = {
        "afternoon": Decimal("1.15"),      # 3pm-8pm weekday
        "night": Decimal("1.25"),          # 8pm-7am weekday
        "evening": Decimal("1.50"),        # After 6pm weekday
        "saturday": Decimal("1.50"),       # All day Saturday
        "sunday": Decimal("1.75"),         # All day Sunday
        "public_holiday": Decimal("2.50"), # Public holidays
    }

    # Allowances (2026 rates - Update annually)
    ALLOWANCES = {
        "sleepover": Decimal("62.45"),     # Per night
        "broken_shift": Decimal("4.85"),   # Per occurrence
        "meal": Decimal("18.35"),          # Per shift over 5 hours
        "km_rate": Decimal("0.85"),        # Per kilometer
    }

    # Leave Loading (17.5% of 4 weeks annual leave)
    LEAVE_LOADING_RATE = Decimal("0.175")

    # Superannuation (2026 - 11.5%)
    SUPERANNUATION_RATE = Decimal("0.115")
    SUPERANNUATION_THRESHOLD = Decimal("450")  # Monthly threshold

    def __init__(self):
        """Initialize SCHADS calculator"""
        logger.info("SCHADS Calculator initialized")

    def calculate_shift_pay(
        self,
        classification: str,
        start_time: datetime,
        end_time: datetime,
        is_public_holiday: bool = False,
        is_sleepover: bool = False,
        is_broken_shift: bool = False,
        travel_km: float = 0,
        custom_rate: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Calculate pay for a single shift

        Args:
            classification: SCHADS classification level (e.g., "2.1", "3.1")
            start_time: Shift start datetime
            end_time: Shift end datetime
            is_public_holiday: True if public holiday
            is_sleepover: True if sleepover shift
            is_broken_shift: True if broken shift
            travel_km: Travel kilometers
            custom_rate: Custom hourly rate (overrides classification)

        Returns:
            Dictionary with detailed pay breakdown
        """
        # Get base rate
        if custom_rate:
            base_rate = custom_rate
        else:
            base_rate = self.BASE_RATES.get(classification)
            if not base_rate:
                raise ValueError(f"Invalid SCHADS classification: {classification}")

        # Calculate shift duration in hours
        duration = (end_time - start_time).total_seconds() / 3600
        duration = Decimal(str(duration))

        # Handle sleepover shifts differently
        if is_sleepover:
            return self._calculate_sleepover_shift(
                base_rate, start_time, end_time
            )

        # Break down shift into time periods with different penalty rates
        periods = self._break_into_periods(start_time, end_time, is_public_holiday)

        # Calculate pay for each period
        total_ordinary = Decimal("0")
        total_penalty = Decimal("0")
        breakdown = []

        for period in periods:
            period_hours = period["hours"]
            period_rate = base_rate * period["multiplier"]
            period_pay = period_hours * period_rate

            ordinary_pay = period_hours * base_rate
            penalty_pay = period_pay - ordinary_pay

            total_ordinary += ordinary_pay
            total_penalty += penalty_pay

            breakdown.append({
                "period": period["name"],
                "hours": float(period_hours),
                "rate": float(period_rate),
                "ordinary": float(ordinary_pay),
                "penalty": float(penalty_pay),
                "total": float(period_pay)
            })

        # Calculate allowances
        allowances = self._calculate_allowances(
            duration, is_broken_shift, travel_km
        )

        # Total pay
        total_pay = total_ordinary + total_penalty + sum(
            Decimal(str(a["amount"])) for a in allowances.values()
        )

        return {
            "classification": classification,
            "base_rate": float(base_rate),
            "hours": float(duration),
            "ordinary_pay": float(total_ordinary),
            "penalty_pay": float(total_penalty),
            "allowances": allowances,
            "gross_pay": float(total_pay),
            "breakdown": breakdown
        }

    def _break_into_periods(
        self,
        start_time: datetime,
        end_time: datetime,
        is_public_holiday: bool
    ) -> List[Dict[str, Any]]:
        """
        Break shift into periods with different penalty rates

        Args:
            start_time: Shift start
            end_time: Shift end
            is_public_holiday: True if public holiday

        Returns:
            List of periods with hours and multipliers
        """
        periods = []

        # Public holiday overrides all other penalties
        if is_public_holiday:
            duration = (end_time - start_time).total_seconds() / 3600
            return [{
                "name": "Public Holiday",
                "hours": Decimal(str(duration)),
                "multiplier": self.PENALTIES["public_holiday"]
            }]

        current_time = start_time

        while current_time < end_time:
            # Determine what penalty applies to current time
            period_end, multiplier, name = self._get_period_end_and_rate(
                current_time, end_time
            )

            # Calculate hours in this period
            period_hours = (period_end - current_time).total_seconds() / 3600

            periods.append({
                "name": name,
                "hours": Decimal(str(period_hours)),
                "multiplier": multiplier
            })

            current_time = period_end

        return periods

    def _get_period_end_and_rate(
        self,
        current_time: datetime,
        end_time: datetime
    ) -> tuple:
        """
        Get the end of current penalty period and rate

        Args:
            current_time: Current time in shift
            end_time: Shift end time

        Returns:
            Tuple of (period_end_time, multiplier, period_name)
        """
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        current_hour = current_time.time()

        # Sunday (all day)
        if day_of_week == 6:
            next_day = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            period_end = min(end_time, next_day)
            return period_end, self.PENALTIES["sunday"], "Sunday"

        # Saturday (all day)
        elif day_of_week == 5:
            next_day = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            period_end = min(end_time, next_day)
            return period_end, self.PENALTIES["saturday"], "Saturday"

        # Weekday penalties
        else:
            # Night (8pm-7am)
            if current_hour >= time(20, 0) or current_hour < time(7, 0):
                if current_hour >= time(20, 0):
                    # Until midnight or 7am next day
                    next_morning = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
                    next_morning = next_morning.replace(hour=7, minute=0)
                else:
                    # Until 7am
                    next_morning = current_time.replace(hour=7, minute=0, second=0)

                period_end = min(end_time, next_morning)
                return period_end, self.PENALTIES["night"], "Night (Weekday)"

            # Afternoon (3pm-8pm)
            elif time(15, 0) <= current_hour < time(20, 0):
                eight_pm = current_time.replace(hour=20, minute=0, second=0)
                period_end = min(end_time, eight_pm)
                return period_end, self.PENALTIES["afternoon"], "Afternoon"

            # Ordinary time (7am-3pm)
            else:
                three_pm = current_time.replace(hour=15, minute=0, second=0)
                period_end = min(end_time, three_pm)
                return period_end, Decimal("1.0"), "Ordinary Time"

    def _calculate_sleepover_shift(
        self,
        base_rate: Decimal,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Calculate pay for sleepover shift

        Args:
            base_rate: Base hourly rate
            start_time: Shift start
            end_time: Shift end

        Returns:
            Pay calculation
        """
        sleepover_allowance = self.ALLOWANCES["sleepover"]
        duration = (end_time - start_time).total_seconds() / 3600

        return {
            "shift_type": "sleepover",
            "base_rate": float(base_rate),
            "hours": float(duration),
            "ordinary_pay": 0,
            "penalty_pay": 0,
            "allowances": {
                "sleepover": {
                    "amount": float(sleepover_allowance),
                    "description": "Sleepover allowance"
                }
            },
            "gross_pay": float(sleepover_allowance),
            "breakdown": []
        }

    def _calculate_allowances(
        self,
        hours: Decimal,
        is_broken_shift: bool,
        travel_km: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate applicable allowances

        Args:
            hours: Shift hours
            is_broken_shift: True if broken shift
            travel_km: Travel kilometers

        Returns:
            Dictionary of allowances
        """
        allowances = {}

        # Meal allowance (shifts over 5 hours)
        if hours > 5:
            allowances["meal"] = {
                "amount": float(self.ALLOWANCES["meal"]),
                "description": "Meal allowance (shift > 5 hours)"
            }

        # Broken shift allowance
        if is_broken_shift:
            allowances["broken_shift"] = {
                "amount": float(self.ALLOWANCES["broken_shift"]),
                "description": "Broken shift allowance"
            }

        # Travel allowance
        if travel_km > 0:
            travel_amount = Decimal(str(travel_km)) * self.ALLOWANCES["km_rate"]
            allowances["travel"] = {
                "amount": float(travel_amount),
                "description": f"Travel allowance ({travel_km} km)"
            }

        return allowances

    def calculate_leave_loading(
        self,
        ordinary_hours: Decimal,
        base_rate: Decimal
    ) -> Decimal:
        """
        Calculate leave loading (17.5% on 4 weeks annual leave)

        Args:
            ordinary_hours: Total ordinary hours worked in year
            base_rate: Base hourly rate

        Returns:
            Leave loading amount
        """
        # 4 weeks of annual leave = 152 hours (38 hours * 4)
        annual_leave_hours = Decimal("152")
        annual_leave_pay = annual_leave_hours * base_rate
        leave_loading = annual_leave_pay * self.LEAVE_LOADING_RATE

        return leave_loading.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_superannuation(
        self,
        ordinary_time_earnings: Decimal
    ) -> Decimal:
        """
        Calculate superannuation contribution

        Args:
            ordinary_time_earnings: OTE for the period

        Returns:
            Superannuation amount
        """
        # SG is calculated on Ordinary Time Earnings (OTE)
        # Does not include overtime penalties
        super_amount = ordinary_time_earnings * self.SUPERANNUATION_RATE

        return super_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def validate_timesheet(
        self,
        timesheet: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a timesheet for errors and compliance

        Args:
            timesheet: List of shift entries

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        for idx, shift in enumerate(timesheet):
            # Check for required fields
            required_fields = ["classification", "start_time", "end_time"]
            missing_fields = [f for f in required_fields if f not in shift]

            if missing_fields:
                errors.append({
                    "shift_index": idx,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue

            # Check classification is valid
            if shift["classification"] not in self.BASE_RATES:
                errors.append({
                    "shift_index": idx,
                    "error": f"Invalid classification: {shift['classification']}"
                })

            # Check times are valid
            try:
                start = datetime.fromisoformat(shift["start_time"])
                end = datetime.fromisoformat(shift["end_time"])

                # Check end is after start
                if end <= start:
                    errors.append({
                        "shift_index": idx,
                        "error": "End time must be after start time"
                    })

                # Warn about very long shifts (over 12 hours)
                duration = (end - start).total_seconds() / 3600
                if duration > 12:
                    warnings.append({
                        "shift_index": idx,
                        "warning": f"Shift duration is {duration:.1f} hours (over 12 hours)"
                    })

            except ValueError as e:
                errors.append({
                    "shift_index": idx,
                    "error": f"Invalid datetime format: {str(e)}"
                })

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
