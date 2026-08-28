import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Strict set of permitted actions in the Razorpay Revenue Recovery Control Tower
ALLOWED_ACTIONS = {
    "RETRY_PAYMENT",
    "SEND_PAYMENT_LINK",
    "SEND_REMINDER",
    "OFFER_APPROVED_INCENTIVE",
    "ESCALATE_TO_HUMAN",
    "NO_ACTION"
}

SYSTEM_PROMPT = """You are a revenue recovery decision assistant for a Razorpay merchant.
Your job is to recommend the most appropriate next action for a revenue recovery opportunity.

You may choose ONLY from these allowed actions:
- RETRY_PAYMENT
- SEND_PAYMENT_LINK
- SEND_REMINDER
- OFFER_APPROVED_INCENTIVE
- ESCALATE_TO_HUMAN
- NO_ACTION

CRITICAL SAFETY CONSTRAINTS:
1. Do NOT invent actions outside the allowed action list.
2. Do NOT calculate financial amounts or modify values.
3. Do NOT invent customer facts or assume unstated details.
4. Return ONLY valid JSON in the exact structure specified below.

Required JSON Structure:
{
  "recommended_action": "<ONE_ALLOWED_ACTION>",
  "reason": "<Clear human-readable justification based on customer history, event type, and failure reason>",
  "confidence": <float between 0.0 and 1.0>,
  "alternative_action": "<ANOTHER_ALLOWED_ACTION>"
}"""


class AIDecisionEngine:
    """
    AI Decision Engine for Razorpay Merchants.
    
    Provides contextual recommendations for next-best recovery actions using LLMs 
    when available, with strict JSON validation and deterministic fallback guarantees.
    """

    @staticmethod
    def recommend_next_action(
        opportunity: Dict[str, Any], 
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Takes structured opportunity payload from Phase 3 and returns next-best action recommendation.
        Guarantees structured return payload with valid recommended_action and reasoning.
        """
        # Validate opportunity input
        if not opportunity or "event_id" not in opportunity:
            return AIDecisionEngine._get_fallback_recommendation(opportunity, reason_prefix="Invalid opportunity payload.")

        # Extract context fields safely for AI reasoning
        event_id = opportunity.get("event_id", "UNKNOWN")
        event_type = opportunity.get("event_type", "UNKNOWN")
        amount = opportunity.get("revenue_at_risk", 0.0)
        root_cause = opportunity.get("likely_root_cause", "UNKNOWN")
        recoverability = opportunity.get("recoverability_probability", 0.5)
        urgency = opportunity.get("urgency_score", 0.5)
        customer_val = opportunity.get("customer_value_factor", 0.5)
        priority = opportunity.get("priority_score", 0.5)
        days_overdue = opportunity.get("days_overdue", 0)
        days_ago = opportunity.get("days_ago", 0)

        # Build clean AI user prompt payload
        ai_input_data = {
            "event_id": event_id,
            "event_type": event_type,
            "revenue_at_risk_inr": amount,
            "likely_root_cause": root_cause,
            "recoverability_probability": recoverability,
            "urgency_score": urgency,
            "customer_value_factor": customer_val,
            "priority_score": priority,
            "days_overdue": days_overdue,
            "days_ago": days_ago
        }

        # Attempt LLM call if valid API key is present (mocked or external LLM service)
        if api_key and api_key != "demo-key-ai-explainer" and not api_key.startswith("mock"):
            try:
                # LLM API call invocation template (OpenAI/Gemini API compatible)
                response_data = AIDecisionEngine._call_external_llm(ai_input_data, api_key)
                
                # Parse and validate LLM output
                recommended_action = response_data.get("recommended_action")
                if recommended_action in ALLOWED_ACTIONS:
                    return {
                        "event_id": event_id,
                        "recommended_action": recommended_action,
                        "reason": str(response_data.get("reason", "Recommended based on opportunity analysis.")),
                        "confidence": float(response_data.get("confidence", 0.85)),
                        "alternative_action": str(response_data.get("alternative_action", "SEND_PAYMENT_LINK")),
                        "recommendation_source": "AI_LLM_ENGINE"
                    }
                else:
                    logger.warning(f"LLM returned unpermitted action '{recommended_action}'. Falling back to deterministic rule.")
            except Exception as err:
                logger.warning(f"LLM API call failed or timed out: {err}. Triggering deterministic fallback.")

        # Deterministic Fallback Engine
        return AIDecisionEngine._get_fallback_recommendation(opportunity)

    @staticmethod
    def _call_external_llm(ai_input_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """
        Placeholder for external LLM API client (OpenAI / Gemini).
        In production, calls LLM endpoint with SYSTEM_PROMPT.
        """
        # Simulated exception for invalid keys to test fallback cleanly
        raise NotImplementedError("Live LLM integration disabled in local test mode; using fallback engine.")

    @staticmethod
    def _get_fallback_recommendation(
        opportunity: Dict[str, Any], 
        reason_prefix: str = ""
    ) -> Dict[str, Any]:
        """
        100% Deterministic Fallback Recommendation Engine.
        Provides robust, explainable action recommendations when LLM is unavailable or unpermitted.
        """
        event_id = opportunity.get("event_id", "EVT-UNKNOWN") if opportunity else "EVT-UNKNOWN"
        event_type = opportunity.get("event_type", "UNKNOWN") if opportunity else "UNKNOWN"
        recoverability = opportunity.get("recoverability_probability", 0.5) if opportunity else 0.5
        root_cause = opportunity.get("likely_root_cause", "UNKNOWN") if opportunity else "UNKNOWN"
        revenue_at_risk = opportunity.get("revenue_at_risk", 0.0) if opportunity else 0.0
        days_overdue = opportunity.get("days_overdue", 0) if opportunity else 0

        # Rule 1: Extremely low recoverability -> NO_ACTION
        if recoverability < 0.15:
            action = "NO_ACTION"
            reason = f"Recoverability score is critically low ({int(recoverability*100)}%). Pursuing recovery has low expected ROI."
            alt_action = "ESCALATE_TO_HUMAN"
            conf = 0.90

        # Rule 2: PAYMENT_FAILURE workflows
        elif event_type == "PAYMENT_FAILURE":
            if recoverability >= 0.70 and root_cause == "BANK_DECLINE":
                action = "RETRY_PAYMENT"
                reason = f"Payment failure caused by transient bank decline with high customer recoverability ({int(recoverability*100)}%). Retrying payment is optimal."
                alt_action = "SEND_PAYMENT_LINK"
                conf = 0.88
            else:
                action = "SEND_PAYMENT_LINK"
                reason = f"Payment failure with root cause '{root_cause}'. Sending a direct Razorpay payment link enables customer to complete checkout with alternative payment method."
                alt_action = "SEND_REMINDER"
                conf = 0.82

        # Rule 3: CHECKOUT_ABANDONMENT workflows
        elif event_type == "CHECKOUT_ABANDONMENT":
            if revenue_at_risk >= 10000.0 and recoverability >= 0.60:
                action = "OFFER_APPROVED_INCENTIVE"
                reason = f"High-value abandoned cart (₹{revenue_at_risk:,.2f}). Offering an approved merchant discount incentive maximizes recovery probability."
                alt_action = "SEND_REMINDER"
                conf = 0.85
            else:
                action = "SEND_REMINDER"
                reason = f"Cart abandoned recently. Sending a gentle checkout reminder encourages customer completion."
                alt_action = "SEND_PAYMENT_LINK"
                conf = 0.80

        # Rule 4: SUBSCRIPTION_FAILURE workflows
        elif event_type == "SUBSCRIPTION_FAILURE":
            if "EXPIRED" in root_cause or root_cause == "EXPIRED_PAYMENT_METHOD":
                action = "SEND_PAYMENT_LINK"
                reason = "Subscription auto-debit failed due to expired payment method. Sending payment link allows customer to update card details."
                alt_action = "SEND_REMINDER"
                conf = 0.87
            else:
                action = "RETRY_PAYMENT"
                reason = f"Subscription failure due to '{root_cause}'. Scheduling a secondary auto-debit retry."
                alt_action = "SEND_PAYMENT_LINK"
                conf = 0.78

        # Rule 5: OVERDUE_INVOICE workflows
        elif event_type == "OVERDUE_INVOICE":
            if days_overdue >= 30 or revenue_at_risk >= 50000.0:
                action = "ESCALATE_TO_HUMAN"
                reason = f"Invoice is {days_overdue} days overdue with high value (₹{revenue_at_risk:,.2f}). Escalating to merchant account manager for personal outreach."
                alt_action = "SEND_REMINDER"
                conf = 0.90
            else:
                action = "SEND_REMINDER"
                reason = f"Invoice is {days_overdue} days overdue. Sending automated payment reminder with attached invoice link."
                alt_action = "ESCALATE_TO_HUMAN"
                conf = 0.84

        # Fallback default
        else:
            action = "SEND_PAYMENT_LINK"
            reason = "Standard recovery recommendation to provide customer with instant payment link."
            alt_action = "SEND_REMINDER"
            conf = 0.75

        if reason_prefix:
            reason = f"{reason_prefix} {reason}"

        return {
            "event_id": event_id,
            "recommended_action": action,
            "reason": reason,
            "confidence": conf,
            "alternative_action": alt_action,
            "recommendation_source": "DETERMINISTIC_FALLBACK_ENGINE"
        }
