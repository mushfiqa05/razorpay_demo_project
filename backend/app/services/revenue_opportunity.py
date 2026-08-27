from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Dict, Any, Optional

class RevenueOpportunityEngine:
    """
    Transparent, Rule-Based Revenue Opportunity Engine for Razorpay Merchants.
    
    Performs 100% deterministic analysis for every revenue event:
    1. Revenue at Risk (Decimal)
    2. Likely Root Cause
    3. Recoverability Probability (0.0 to 1.0)
    4. Expected Recoverable Value (Revenue at Risk * Recoverability)
    5. Urgency Score (0.0 to 1.0)
    6. Customer Value Factor (0.0 to 1.0)
    7. Priority Score (0.0 to 1.0)
    8. Suggested Action Category
    """

    @staticmethod
    def analyze_event(event, customer=None) -> Dict[str, Any]:
        """
        Analyzes a single revenue event and returns structured opportunity metrics.
        Accepts a RevenueEvent ORM model (or dict) and associated Customer ORM model.
        """
        # Extract basic properties safely
        event_id = str(getattr(event, "id", "EVT-UNKNOWN"))
        event_type = str(getattr(event, "event_type", "UNKNOWN"))
        
        # 1. Revenue at Risk (Decimal representation of monetary amount)
        raw_amount = getattr(event, "amount", 0)
        revenue_at_risk = Decimal(str(raw_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if revenue_at_risk < Decimal("0.00"):
            revenue_at_risk = Decimal("0.00")

        currency = str(getattr(event, "currency", "INR"))
        days_overdue = int(getattr(event, "days_overdue", 0))
        failure_reason = getattr(event, "failure_reason", None)
        payment_method = getattr(event, "payment_method", None)
        status = str(getattr(event, "status", "OPEN"))

        # Calculate event age in days
        event_timestamp = getattr(event, "event_timestamp", datetime.utcnow())
        if isinstance(event_timestamp, datetime):
            days_ago = max(0, (datetime.utcnow() - event_timestamp).days)
        else:
            days_ago = 0

        # Customer performance metrics
        if customer:
            customer_value_str = str(getattr(customer, "customer_value", "STANDARD"))
            prev_total = int(getattr(customer, "previous_payment_count", 0))
            prev_success = int(getattr(customer, "previous_success_count", 0))
            prev_attempts = int(getattr(customer, "previous_recovery_attempts", 0))
            is_opted_out = bool(getattr(customer, "is_opted_out", False))
        else:
            customer_value_str = "STANDARD"
            prev_total = 0
            prev_success = 0
            prev_attempts = 0
            is_opted_out = False

        # 2. Diagnose Likely Root Cause
        likely_root_cause = RevenueOpportunityEngine._determine_root_cause(
            event_type=event_type,
            failure_reason=failure_reason,
            days_overdue=days_overdue,
            revenue_at_risk=revenue_at_risk
        )

        # 3. Calculate Recoverability Probability (0.0 to 1.0)
        recoverability = RevenueOpportunityEngine._calculate_recoverability(
            event_type=event_type,
            prev_total=prev_total,
            prev_success=prev_success,
            prev_attempts=prev_attempts,
            days_overdue=days_overdue,
            days_ago=days_ago,
            is_opted_out=is_opted_out
        )

        # 4. Calculate Expected Recoverable Value (Decimal)
        recoverability_decimal = Decimal(str(recoverability))
        expected_recoverable_value = (revenue_at_risk * recoverability_decimal).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # 5. Calculate Urgency Score (0.0 to 1.0)
        urgency = RevenueOpportunityEngine._calculate_urgency(
            event_type=event_type,
            days_ago=days_ago,
            days_overdue=days_overdue
        )

        # 6. Calculate Customer Value Factor (0.0 to 1.0)
        customer_value_factor = RevenueOpportunityEngine._calculate_customer_value_factor(
            customer_value_str=customer_value_str,
            prev_success=prev_success
        )

        # 7. Calculate Priority Score (0.0 to 1.0)
        priority_score = RevenueOpportunityEngine._calculate_priority_score(
            expected_recoverable_value=expected_recoverable_value,
            recoverability=recoverability,
            urgency=urgency,
            customer_value_factor=customer_value_factor
        )

        # 8. Determine Suggested Action Category
        suggested_action = RevenueOpportunityEngine._determine_suggested_action(
            event_type=event_type,
            recoverability=recoverability,
            prev_attempts=prev_attempts,
            failure_reason=failure_reason,
            days_overdue=days_overdue,
            revenue_at_risk=revenue_at_risk,
            is_opted_out=is_opted_out
        )

        return {
            "event_id": event_id,
            "merchant_id": str(getattr(event, "merchant_id", "MERCH-1001")),
            "customer_id": str(getattr(event, "customer_id", "CUST-1001")),
            "event_type": event_type,
            "amount": float(revenue_at_risk),
            "currency": currency,
            "status": status,
            "revenue_at_risk": float(revenue_at_risk),
            "likely_root_cause": likely_root_cause,
            "recoverability_probability": round(recoverability, 4),
            "expected_recoverable_value": float(expected_recoverable_value),
            "urgency_score": round(urgency, 4),
            "customer_value_factor": round(customer_value_factor, 4),
            "priority_score": round(priority_score, 4),
            "suggested_action": suggested_action,
            "days_overdue": days_overdue,
            "days_ago": days_ago
        }

    @staticmethod
    def _determine_root_cause(
        event_type: str, 
        failure_reason: Optional[str], 
        days_overdue: int, 
        revenue_at_risk: Decimal
    ) -> str:
        """Determines likely root cause based on event type and failure signals."""
        reason_upper = (failure_reason or "").upper()

        if event_type == "PAYMENT_FAILURE":
            if "BANK" in reason_upper or "DECLINE" in reason_upper or "TIMEOUT" in reason_upper:
                return "BANK_DECLINE"
            elif "FUNDS" in reason_upper:
                return "INSUFFICIENT_FUNDS"
            elif "EXPIRED" in reason_upper or "CARD" in reason_upper:
                return "EXPIRED_CARD"
            elif "AUTH" in reason_upper or "OTP" in reason_upper:
                return "AUTHENTICATION_FAILURE"
            elif reason_upper != "":
                return reason_upper
            return "UNKNOWN"

        elif event_type == "CHECKOUT_ABANDONMENT":
            if revenue_at_risk >= Decimal("10000.00"):
                return "HIGH_VALUE_ABANDONMENT"
            elif "REPEATED" in reason_upper or "VISIT" in reason_upper:
                return "REPEATED_CHECKOUT_ABANDONMENT"
            elif "INACTIVITY" in reason_upper:
                return "LONG_INACTIVITY"
            elif reason_upper != "":
                return reason_upper
            return "UNKNOWN"

        elif event_type == "SUBSCRIPTION_FAILURE":
            if "EXPIRED" in reason_upper or "CARD" in reason_upper:
                return "EXPIRED_PAYMENT_METHOD"
            elif "FUNDS" in reason_upper or "DECLINE" in reason_upper:
                return "INSUFFICIENT_FUNDS"
            elif "AUTO_DEBIT" in reason_upper:
                return "AUTO_DEBIT_DECLINE"
            elif reason_upper != "":
                return reason_upper
            return "UNKNOWN"

        elif event_type == "OVERDUE_INVOICE":
            if days_overdue > 30 and revenue_at_risk >= Decimal("50000.00"):
                return "HIGH_VALUE_LONG_OVERDUE"
            elif days_overdue > 30:
                return "LONG_OVERDUE"
            elif days_overdue > 0:
                return "SHORT_OVERDUE"
            elif "REPEATED" in reason_upper:
                return "REPEATED_OVERDUE"
            elif reason_upper != "":
                return reason_upper
            return "UNKNOWN"

        return "UNKNOWN"

    @staticmethod
    def _calculate_recoverability(
        event_type: str,
        prev_total: int,
        prev_success: int,
        prev_attempts: int,
        days_overdue: int,
        days_ago: int,
        is_opted_out: bool
    ) -> float:
        """
        Calculates transparent recoverability score (0.0 to 1.0).
        Formula: Base (0.50) + Customer History + Recovery History + Event Factors - Penalties
        """
        if is_opted_out:
            return 0.05  # Near zero recoverability if customer opted out of contact

        score = 0.50  # Base neutral score

        # 1. Customer Payment History Factor (+0.25 max, -0.20 min)
        if prev_total > 0:
            success_rate = prev_success / prev_total
            if success_rate >= 0.85:
                score += 0.25
            elif success_rate >= 0.65:
                score += 0.15
            elif success_rate >= 0.45:
                score += 0.05
            else:
                score -= 0.15
        else:
            score += 0.00  # New customer neutral

        # 2. Previous Recovery Attempts Factor (+0.10 max, -0.20 min)
        if prev_attempts == 0:
            score += 0.10  # Fresh opportunity, no spam fatigue
        elif prev_attempts == 1:
            score -= 0.05
        else:
            score -= 0.20  # Multiple previous failed attempts indicate fatigue/unwillingness

        # 3. Event Freshness / Age Factor
        if days_ago <= 2:
            score += 0.05
        elif days_ago > 14:
            score -= 0.10

        # 4. Overdue Penalty for Invoices (-0.01 per 5 days overdue, max -0.25)
        if days_overdue > 0:
            overdue_penalty = min(0.25, (days_overdue / 100.0))
            score -= overdue_penalty

        # Clamp score between 0.0 and 1.0
        return float(max(0.0, min(1.0, score)))

    @staticmethod
    def _calculate_urgency(event_type: str, days_ago: int, days_overdue: int) -> float:
        """
        Calculates urgency score (0.0 to 1.0).
        Fresh failures or long overdue invoices carry higher urgency.
        """
        if event_type == "OVERDUE_INVOICE":
            # Urgency scales up with days overdue (30 days overdue = 0.80 urgency)
            urgency = min(1.0, 0.40 + (days_overdue / 50.0))
        elif event_type == "CHECKOUT_ABANDONMENT":
            # Cart abandonment requires rapid intervention (decay over 7 days)
            urgency = max(0.1, 1.0 - (days_ago / 7.0))
        else:
            # Payment/Subscription failures decay gradually over 14 days
            urgency = max(0.2, 0.90 - (days_ago / 14.0))

        return float(max(0.0, min(1.0, urgency)))

    @staticmethod
    def _calculate_customer_value_factor(customer_value_str: str, prev_success: int) -> float:
        """Returns customer value factor (0.0 to 1.0) based on tier and past payments."""
        if customer_value_str == "HIGH_VALUE" or prev_success >= 10:
            return 1.0
        elif customer_value_str == "STANDARD" or prev_success >= 3:
            return 0.60
        else:
            return 0.35

    @staticmethod
    def _calculate_priority_score(
        expected_recoverable_value: Decimal,
        recoverability: float,
        urgency: float,
        customer_value_factor: float
    ) -> float:
        """
        Calculates priority score (0.0 to 1.0) using transparent weighted formula:
        Priority = 0.50 * Normalized_Expected_Value + 0.20 * Recoverability + 0.20 * Urgency + 0.10 * Customer_Value
        """
        # Normalize expected recoverable value (scaled relative to ₹50,000 benchmark)
        exp_val_float = float(expected_recoverable_value)
        normalized_exp_val = min(1.0, exp_val_float / 50000.0)

        priority = (
            (normalized_exp_val * 0.50) +
            (recoverability * 0.20) +
            (urgency * 0.20) +
            (customer_value_factor * 0.10)
        )

        return float(max(0.0, min(1.0, priority)))

    @staticmethod
    def _determine_suggested_action(
        event_type: str,
        recoverability: float,
        prev_attempts: int,
        failure_reason: Optional[str],
        days_overdue: int,
        revenue_at_risk: Decimal,
        is_opted_out: bool
    ) -> str:
        """Determines preliminary suggested action category using rule-based heuristics."""
        if is_opted_out or recoverability < 0.15:
            return "NO_ACTION"

        reason_upper = (failure_reason or "").upper()

        if event_type == "PAYMENT_FAILURE":
            if recoverability >= 0.70 and prev_attempts == 0:
                return "RETRY_PAYMENT"
            elif prev_attempts >= 1 or "CARD" in reason_upper:
                return "SEND_PAYMENT_LINK"
            else:
                return "SEND_REMINDER"

        elif event_type == "CHECKOUT_ABANDONMENT":
            if revenue_at_risk >= Decimal("10000.00") and recoverability >= 0.60:
                return "OFFER_APPROVED_INCENTIVE"
            else:
                return "SEND_REMINDER"

        elif event_type == "SUBSCRIPTION_FAILURE":
            if "EXPIRED" in reason_upper or "CARD" in reason_upper:
                return "SEND_PAYMENT_LINK"
            else:
                return "RETRY_PAYMENT"

        elif event_type == "OVERDUE_INVOICE":
            if days_overdue >= 45 or revenue_at_risk >= Decimal("50000.00"):
                return "ESCALATE_TO_HUMAN"
            else:
                return "SEND_REMINDER"

        return "SEND_PAYMENT_LINK"
