/**
 * SCHADS Award Calculator - JavaScript Implementation
 * Complete payroll calculation engine for NDIS workers
 */

class SCHADSCalculator {
    constructor() {
        // SCHADS Award Rates (2026 - Update annually)
        this.BASE_RATES = {
            "1.1": 27.15,
            "1.2": 27.85,
            "2.1": 28.45,
            "2.2": 29.15,
            "2.3": 29.85,
            "3.1": 30.85,
            "3.2": 31.55,
            "3.3": 32.25,
            "4.1": 33.95,
            "4.2": 35.15,
            "4.3": 36.45
        };

        // Penalty Rates (multipliers)
        this.PENALTIES = {
            afternoon: 1.15,      // 3pm-8pm weekday
            night: 1.25,          // 8pm-7am weekday
            evening: 1.50,        // After 6pm weekday
            saturday: 1.50,       // All day Saturday
            sunday: 1.75,         // All day Sunday
            public_holiday: 2.50  // Public holidays
        };

        // Allowances (2026 rates)
        this.ALLOWANCES = {
            sleepover: 62.45,     // Per night
            broken_shift: 4.85,   // Per occurrence
            meal: 18.35,          // Per shift over 5 hours
            km_rate: 0.85         // Per kilometer
        };

        // Leave Loading (17.5%)
        this.LEAVE_LOADING_RATE = 0.175;

        // Superannuation (11.5% for 2026)
        this.SUPERANNUATION_RATE = 0.115;
    }

    /**
     * Calculate shift pay
     */
    calculateShiftPay(options) {
        const {
            classification,
            startTime,
            endTime,
            isPublicHoliday = false,
            isSleepover = false,
            isBrokenShift = false,
            travelKm = 0
        } = options;

        // Get base rate
        const baseRate = this.BASE_RATES[classification];
        if (!baseRate) {
            throw new Error(`Invalid SCHADS classification: ${classification}`);
        }

        // Parse dates
        const start = new Date(startTime);
        const end = new Date(endTime);

        // Calculate duration in hours
        const durationMs = end - start;
        const durationHours = durationMs / (1000 * 60 * 60);

        // Handle sleepover shifts
        if (isSleepover) {
            return this._calculateSleeperShift(baseRate, durationHours);
        }

        // Break shift into periods with different penalties
        const periods = this._breakIntoPeriods(start, end, isPublicHoliday);

        // Calculate pay for each period
        let totalOrdinary = 0;
        let totalPenalty = 0;
        const breakdown = [];

        for (const period of periods) {
            const periodRate = baseRate * period.multiplier;
            const periodPay = period.hours * periodRate;
            const ordinaryPay = period.hours * baseRate;
            const penaltyPay = periodPay - ordinaryPay;

            totalOrdinary += ordinaryPay;
            totalPenalty += penaltyPay;

            breakdown.push({
                period: period.name,
                hours: period.hours,
                rate: periodRate,
                ordinary: ordinaryPay,
                penalty: penaltyPay,
                total: periodPay
            });
        }

        // Calculate allowances
        const allowances = this._calculateAllowances(durationHours, isBrokenShift, travelKm);

        // Total pay
        const allowancesTotal = Object.values(allowances).reduce((sum, a) => sum + a.amount, 0);
        const grossPay = totalOrdinary + totalPenalty + allowancesTotal;

        // Superannuation
        const superannuation = totalOrdinary * this.SUPERANNUATION_RATE;

        return {
            classification,
            baseRate,
            hours: durationHours,
            ordinaryPay: this._round(totalOrdinary),
            penaltyPay: this._round(totalPenalty),
            allowances,
            grossPay: this._round(grossPay),
            superannuation: this._round(superannuation),
            breakdown: breakdown.map(b => ({
                ...b,
                rate: this._round(b.rate),
                ordinary: this._round(b.ordinary),
                penalty: this._round(b.penalty),
                total: this._round(b.total)
            }))
        };
    }

    /**
     * Break shift into periods with different penalty rates
     */
    _breakIntoPeriods(startTime, endTime, isPublicHoliday) {
        const periods = [];

        // Public holiday overrides all other penalties
        if (isPublicHoliday) {
            const duration = (endTime - startTime) / (1000 * 60 * 60);
            return [{
                name: "Public Holiday",
                hours: duration,
                multiplier: this.PENALTIES.public_holiday
            }];
        }

        let currentTime = new Date(startTime);

        while (currentTime < endTime) {
            const { periodEnd, multiplier, name } = this._getPeriodEndAndRate(currentTime, endTime);
            const hours = (periodEnd - currentTime) / (1000 * 60 * 60);

            periods.push({
                name,
                hours,
                multiplier
            });

            currentTime = periodEnd;
        }

        return periods;
    }

    /**
     * Get period end and rate for current time
     */
    _getPeriodEndAndRate(currentTime, endTime) {
        const dayOfWeek = currentTime.getDay(); // 0=Sunday, 6=Saturday
        const hours = currentTime.getHours();
        const minutes = currentTime.getMinutes();
        const currentMinutes = hours * 60 + minutes;

        // Sunday (all day)
        if (dayOfWeek === 0) {
            const nextDay = new Date(currentTime);
            nextDay.setHours(24, 0, 0, 0);
            const periodEnd = endTime < nextDay ? endTime : nextDay;
            return {
                periodEnd,
                multiplier: this.PENALTIES.sunday,
                name: "Sunday"
            };
        }

        // Saturday (all day)
        if (dayOfWeek === 6) {
            const nextDay = new Date(currentTime);
            nextDay.setHours(24, 0, 0, 0);
            const periodEnd = endTime < nextDay ? endTime : nextDay;
            return {
                periodEnd,
                multiplier: this.PENALTIES.saturday,
                name: "Saturday"
            };
        }

        // Weekday penalties
        // Night (8pm-7am)
        if (currentMinutes >= 20 * 60 || currentMinutes < 7 * 60) {
            let nextTransition;
            if (currentMinutes >= 20 * 60) {
                // Until midnight or end
                nextTransition = new Date(currentTime);
                nextTransition.setHours(24, 0, 0, 0);
            } else {
                // Until 7am
                nextTransition = new Date(currentTime);
                nextTransition.setHours(7, 0, 0, 0);
            }
            const periodEnd = endTime < nextTransition ? endTime : nextTransition;
            return {
                periodEnd,
                multiplier: this.PENALTIES.night,
                name: "Night (Weekday)"
            };
        }

        // Afternoon (3pm-8pm)
        if (currentMinutes >= 15 * 60 && currentMinutes < 20 * 60) {
            const eightPm = new Date(currentTime);
            eightPm.setHours(20, 0, 0, 0);
            const periodEnd = endTime < eightPm ? endTime : eightPm;
            return {
                periodEnd,
                multiplier: this.PENALTIES.afternoon,
                name: "Afternoon"
            };
        }

        // Ordinary time (7am-3pm)
        const threePm = new Date(currentTime);
        threePm.setHours(15, 0, 0, 0);
        const periodEnd = endTime < threePm ? endTime : threePm;
        return {
            periodEnd,
            multiplier: 1.0,
            name: "Ordinary Time"
        };
    }

    /**
     * Calculate sleepover shift
     */
    _calculateSleeperShift(baseRate, hours) {
        return {
            shiftType: "sleepover",
            baseRate,
            hours,
            ordinaryPay: 0,
            penaltyPay: 0,
            allowances: {
                sleepover: {
                    amount: this.ALLOWANCES.sleepover,
                    description: "Sleepover allowance"
                }
            },
            grossPay: this.ALLOWANCES.sleepover,
            superannuation: 0,
            breakdown: []
        };
    }

    /**
     * Calculate allowances
     */
    _calculateAllowances(hours, isBrokenShift, travelKm) {
        const allowances = {};

        // Meal allowance (shifts over 5 hours)
        if (hours > 5) {
            allowances.meal = {
                amount: this.ALLOWANCES.meal,
                description: "Meal allowance (shift > 5 hours)"
            };
        }

        // Broken shift allowance
        if (isBrokenShift) {
            allowances.broken_shift = {
                amount: this.ALLOWANCES.broken_shift,
                description: "Broken shift allowance"
            };
        }

        // Travel allowance
        if (travelKm > 0) {
            allowances.travel = {
                amount: travelKm * this.ALLOWANCES.km_rate,
                description: `Travel allowance (${travelKm} km)`
            };
        }

        return allowances;
    }

    /**
     * Calculate leave loading
     */
    calculateLeaveLoading(ordinaryHours, baseRate) {
        // 4 weeks annual leave = 152 hours (38 hours * 4)
        const annualLeaveHours = 152;
        const annualLeavePay = annualLeaveHours * baseRate;
        const leaveLoading = annualLeavePay * this.LEAVE_LOADING_RATE;
        return this._round(leaveLoading);
    }

    /**
     * Calculate superannuation
     */
    calculateSuperannuation(ordinaryTimeEarnings) {
        const super_amount = ordinaryTimeEarnings * this.SUPERANNUATION_RATE;
        return this._round(super_amount);
    }

    /**
     * Round to 2 decimal places
     */
    _round(value) {
        return Math.round(value * 100) / 100;
    }

    /**
     * Get all classification levels with rates
     */
    getAllRates() {
        return Object.entries(this.BASE_RATES).map(([level, rate]) => ({
            level,
            rate,
            description: this._getClassificationDescription(level)
        }));
    }

    /**
     * Get classification description
     */
    _getClassificationDescription(level) {
        const descriptions = {
            "1.1": "Entry level, training",
            "1.2": "After 3 months",
            "2.1": "Certificate II or 6 months experience (Most Common)",
            "2.2": "Certificate III",
            "2.3": "Certificate III + additional skills",
            "3.1": "Advanced skills, complex care",
            "3.2": "Certificate IV or specialized skills",
            "3.3": "Senior role, supervision",
            "4.1": "Team leader, coordination",
            "4.2": "Senior coordinator",
            "4.3": "Manager level"
        };
        return descriptions[level] || "";
    }
}

// Export for use in other scripts
window.SCHADSCalculator = SCHADSCalculator;
