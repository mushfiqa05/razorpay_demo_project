from decimal import Decimal
from typing import Dict, Any, Optional

ALLOWED_ACTIONS = {
    "RETRY_PAYMENT",
    "SEND_PAYMENT_LINK",
    "SEND_REMINDER",
    "OFFER_APPROVED_INCENTIVE",
    "ESCALATE_TO_HUMAN",
    "NO_ACTION"
}

class GuardrailEngine:
    """
    100% Deterministic Merchant Policy Guardrail Engine.
    
    Acts as an unbreachable firewall between AI recommendations and workflow execution.
    Evaluates 7 strict policy checks:
    1. Action Allowed Check
    2. Max Recovery Attempts Check
    3. Max Reminders Check
    4. Recovery Window Expiry Check
    5. Minimum Expected Recovery Threshold Check
    6. Customer Opt-Out Check
    7. Incentive Discount Limit Check
    """

    @staticmethod
    def validate_action(
        opportunity: Dict[str, Any],
        recommendation: Dict[str, Any],
        merchant_policy: Optional[Any],
        customer: Optional[Any],
        previous_attempts_count: int = 0,
        previous_reminders_count: int = 0,
        offered_discount_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Validates an AI recommendation against deterministic merchant policies.
        Returns a structured validation payload with boolean pass/fail status per check.
        """
        action = recommendation.get("recommended_action", "NO_ACTION")
        exp_recovery = Decimal(str(opportunity.get("expected_recoverable_value", 0.0)))
        days_ago = int(opportunity.get("days_ago", 0))

        # Extract policy rules (with safe fallbacks if policy object is missing)
        max_attempts = int(getattr(merchant_policy, "max_recovery_attempts", 3))
        max_reminders = int(getattr(merchant_policy, "max_reminders", 2))
        max_discount = float(getattr(merchant_policy, "max_discount_percentage", 10.0))
        window_days = int(getattr(merchant_policy, "recovery_window_days", 14))
        min_expected = Decimal(str(getattr(merchant_policy, "minimum_expected_recovery", 100.0)))

        is_opted_out = bool(getattr(customer, "is_opted_out", False))

        # Initialize individual check status flags
        checks = {
            "action_allowed": True,
            "attempt_limit": True,
            "reminder_limit": True,
            "recovery_window": True,
            "minimum_expected_recovery": True,
            "customer_opt_out": True,
            "incentive_limit": True
        }

        blocked_reasons = []

        # CHECK 1: Action Whitelist Check
        if action not in ALLOWED_ACTIONS:
            checks["action_allowed"] = False
            blocked_reasons.append(f"Unpermitted action '{action}' is not in allowed action list.")

        # CHECK 2: Maximum Recovery Attempts Check
        if previous_attempts_count >= max_attempts:
            checks["attempt_limit"] = False
            blocked_reasons.append(f"Reached maximum recovery attempts limit ({previous_attempts_count}/{max_attempts}).")

        # CHECK 3: Maximum Reminders Check
        if action == "SEND_REMINDER" and previous_reminders_count >= max_reminders:
            checks["reminder_limit"] = False
            blocked_reasons.append(f"Reached maximum reminders limit ({previous_reminders_count}/{max_reminders}).")

        # CHECK 4: Recovery Window Expiry Check
        if days_ago > window_days:
            checks["recovery_window"] = False
            blocked_reasons.append(f"Opportunity age ({days_ago} days) exceeds merchant recovery window ({window_days} days).")

        # CHECK 5: Minimum Expected Recovery Threshold Check
        if exp_recovery < min_expected:
            checks["minimum_expected_recovery"] = False
            blocked_reasons.append(f"Expected recovery (₹{exp_recovery:,.2f}) is below minimum threshold (₹{min_expected:,.2f}).")

        # CHECK 6: Customer Opt-Out Check
        communication_actions = {"SEND_REMINDER", "SEND_PAYMENT_LINK", "OFFER_APPROVED_INCENTIVE"}
        if is_opted_out and action in communication_actions:
            checks["customer_opt_out"] = False
            blocked_reasons.append("Customer has explicitly opted out of recovery communications.")

        # CHECK 7: Incentive Discount Limit Check
        if action == "OFFER_APPROVED_INCENTIVE" and offered_discount_pct > max_discount:
            checks["incentive_limit"] = False
            blocked_reasons.append(f"Offered discount ({offered_discount_pct}%) exceeds merchant maximum policy ({max_discount}%).")

        # Evaluate overall allowed status
        is_allowed = all(checks.values())

        if is_allowed:
            reason = "All merchant policy guardrail checks passed successfully."
        else:
            reason = f"Guardrail Blocked: {'; '.join(blocked_reasons)}"

        return {
            "allowed": is_allowed,
            "action": action,
            "reason": reason,
            "checks": checks,
            "blocked_reasons": blocked_reasons
        }
