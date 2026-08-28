import uuid
import random
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import RevenueEvent, Customer, MerchantPolicy, RecoveryAttempt, RecoveryOutcome, AuditLog
from app.services.revenue_opportunity import RevenueOpportunityEngine
from app.services.ai_decision import AIDecisionEngine
from app.services.guardrail import GuardrailEngine

class RecoveryWorkflowController:
    """
    Bounded Recovery Workflow Controller for Razorpay Merchants.
    
    Orchestrates the complete bounded recovery loop:
    Opportunity Analysis -> AI Recommendation -> Guardrail Validation -> 
    Simulated Action Execution -> Outcome Generation -> Audit Logging -> Stopping Rule Evaluation.
    """

    @staticmethod
    def execute_recovery_step(
        event_id: str,
        db: Session,
        api_key: Optional[str] = None,
        force_outcome: Optional[str] = None,  # Useful for deterministic testing: 'RECOVERED' or 'FAILED'
        offered_discount_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes a single bounded recovery step for a given revenue event.
        Guarantees strict single-action execution, guardrail firewalling, terminal state prevention, and immutable audit trails.
        """
        # 1. Fetch required DB entities
        event = db.query(RevenueEvent).filter(RevenueEvent.id == event_id).first()
        if not event:
            raise ValueError(f"Revenue event '{event_id}' not found.")

        # Terminal state check: A recovered event cannot be recovered again!
        if event.status == "RECOVERED":
            audit_terminal = AuditLog(
                id=f"AUD-TRM-{uuid.uuid4().hex[:8]}",
                revenue_event_id=event_id,
                action="NO_ACTION",
                reason="Recovery prevented: Revenue event is already in terminal state 'RECOVERED'.",
                guardrail_result="TERMINAL_STATE_BLOCKED",
                timestamp=datetime.utcnow()
            )
            db.add(audit_terminal)
            db.commit()

            return {
                "event_id": event_id,
                "recommendation": {
                    "event_id": event_id,
                    "recommended_action": "NO_ACTION",
                    "reason": "Event already recovered.",
                    "confidence": 1.0,
                    "alternative_action": "NO_ACTION",
                    "recommendation_source": "SYSTEM_TERMINAL_CHECK"
                },
                "guardrail": {
                    "allowed": False,
                    "reason": "Revenue event is already RECOVERED and cannot undergo further recovery attempts."
                },
                "execution": None,
                "outcome": None,
                "workflow": {
                    "status": "STOPPED",
                    "stop_reason": "EVENT_ALREADY_RECOVERED",
                    "details": "This event has already been successfully recovered and cannot be processed again."
                }
            }

        customer = db.query(Customer).filter(Customer.id == event.customer_id).first()
        policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == event.merchant_id).first()

        # Count existing recovery attempts and reminders for this event
        prev_attempts_count = db.query(RecoveryAttempt).filter(RecoveryAttempt.revenue_event_id == event_id).count()
        prev_reminders_count = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.revenue_event_id == event_id,
            RecoveryAttempt.action_type == "SEND_REMINDER"
        ).count()

        # 2. Phase 3: Run Revenue Opportunity Engine
        opportunity = RevenueOpportunityEngine.analyze_event(event, customer)

        # 3. Phase 4: Get AI Recommendation
        recommendation = AIDecisionEngine.recommend_next_action(opportunity, api_key=api_key)
        action_recommended = recommendation["recommended_action"]

        # Log AI recommendation event to Audit Trail
        audit_ai = AuditLog(
            id=f"AUD-AI-{uuid.uuid4().hex[:8]}",
            revenue_event_id=event_id,
            action=action_recommended,
            reason=f"AI Recommendation ({recommendation['recommendation_source']}): {recommendation['reason']}",
            guardrail_result="AI_RECOMMENDATION_GENERATED",
            timestamp=datetime.utcnow()
        )
        db.add(audit_ai)

        # 4. Phase 5: Run Guardrail Engine Check
        guardrail_result = GuardrailEngine.validate_action(
            opportunity=opportunity,
            recommendation=recommendation,
            merchant_policy=policy,
            customer=customer,
            previous_attempts_count=prev_attempts_count,
            previous_reminders_count=prev_reminders_count,
            offered_discount_pct=offered_discount_pct
        )

        # 5. Handle Guardrail BLOCKED case
        if not guardrail_result["allowed"]:
            audit_blocked = AuditLog(
                id=f"AUD-BLK-{uuid.uuid4().hex[:8]}",
                revenue_event_id=event_id,
                action=action_recommended,
                reason=f"Workflow Blocked by Policy Firewall: {guardrail_result['reason']}",
                guardrail_result="BLOCKED",
                timestamp=datetime.utcnow()
            )
            db.add(audit_blocked)
            db.commit()

            return {
                "event_id": event_id,
                "recommendation": recommendation,
                "guardrail": guardrail_result,
                "execution": None,
                "outcome": None,
                "workflow": {
                    "status": "STOPPED",
                    "stop_reason": "GUARDRAIL_BLOCKED",
                    "details": guardrail_result["reason"]
                }
            }

        # 6. Guardrail ALLOWED: Log Guardrail Approval to Audit Trail
        audit_pass = AuditLog(
            id=f"AUD-PAS-{uuid.uuid4().hex[:8]}",
            revenue_event_id=event_id,
            action=action_recommended,
            reason="Guardrail Validation Passed. Action approved for simulated execution.",
            guardrail_result="PASSED",
            timestamp=datetime.utcnow()
        )
        db.add(audit_pass)

        # 7. Execute SIMULATED Action
        execution_result = RecoveryWorkflowController._simulate_action_execution(action_recommended)

        audit_exec = AuditLog(
            id=f"AUD-EXE-{uuid.uuid4().hex[:8]}",
            revenue_event_id=event_id,
            action=action_recommended,
            reason=f"Executed Simulated Action: {execution_result['message']}",
            guardrail_result="EXECUTION_SIMULATED",
            timestamp=datetime.utcnow()
        )
        db.add(audit_exec)

        # Create RecoveryAttempt record in DB
        attempt_num = prev_attempts_count + 1
        attempt_id = f"ATT-SIM-{uuid.uuid4().hex[:8]}"
        attempt = RecoveryAttempt(
            id=attempt_id,
            revenue_event_id=event_id,
            action_type=action_recommended,
            attempt_number=attempt_num,
            status="PENDING",
            attempted_at=datetime.utcnow()
        )
        db.add(attempt)

        # 8. Generate Simulated Outcome
        rec_prob = opportunity.get("recoverability_probability", 0.5)
        revenue_at_risk = Decimal(str(opportunity.get("revenue_at_risk", 0.0)))

        if force_outcome:
            outcome_status = force_outcome.upper()
        else:
            outcome_status = "RECOVERED" if random.random() < rec_prob else "FAILED"

        if outcome_status == "RECOVERED":
            recovered_amount = revenue_at_risk
            attempt.status = "SUCCESS"
            event.status = "RECOVERED"
            stop_reason = "RECOVERY_SUCCESSFUL"
            workflow_status = "STOPPED"
        else:
            recovered_amount = Decimal("0.00")
            attempt.status = "FAILED"
            max_attempts = int(getattr(policy, "max_recovery_attempts", 3))
            
            if attempt_num >= max_attempts:
                event.status = "FAILED"
                stop_reason = "MAXIMUM_ATTEMPTS_REACHED"
                workflow_status = "STOPPED"
            else:
                event.status = "IN_RECOVERY"
                stop_reason = "ATTEMPT_FAILED_PENDING_NEXT_STEP"
                workflow_status = "IN_RECOVERY"

        # Create RecoveryOutcome record in DB
        outcome_id = f"OUT-SIM-{uuid.uuid4().hex[:8]}"
        outcome = RecoveryOutcome(
            id=outcome_id,
            recovery_attempt_id=attempt_id,
            outcome=outcome_status,
            recovered_amount=recovered_amount,
            outcome_timestamp=datetime.utcnow()
        )
        db.add(outcome)

        # Log Outcome to Audit Trail
        audit_out = AuditLog(
            id=f"AUD-OUT-{uuid.uuid4().hex[:8]}",
            revenue_event_id=event_id,
            action=action_recommended,
            reason=f"Recovery Outcome: {outcome_status}. Recovered Amount: ₹{recovered_amount:,.2f}.",
            guardrail_result=f"OUTCOME_{outcome_status}",
            timestamp=datetime.utcnow()
        )
        db.add(audit_out)

        db.commit()

        return {
            "event_id": event_id,
            "recommendation": recommendation,
            "guardrail": guardrail_result,
            "execution": execution_result,
            "outcome": {
                "attempt_id": attempt_id,
                "outcome_id": outcome_id,
                "status": outcome_status,
                "recovered_amount": float(recovered_amount)
            },
            "workflow": {
                "status": workflow_status,
                "stop_reason": stop_reason,
                "current_attempt": attempt_num,
                "max_attempts": int(getattr(policy, "max_recovery_attempts", 3))
            }
        }

    @staticmethod
    def _simulate_action_execution(action: str) -> Dict[str, Any]:
        """Returns clean simulated action payload clearly labeled as SIMULATED."""
        simulations = {
            "RETRY_PAYMENT": "SIMULATED payment auto-debit retry executed via Razorpay API adapter.",
            "SEND_PAYMENT_LINK": "SIMULATED payment link generated and dispatched to customer email/SMS.",
            "SEND_REMINDER": "SIMULATED automated payment reminder dispatched.",
            "OFFER_APPROVED_INCENTIVE": "SIMULATED approved discount coupon applied to customer checkout link.",
            "ESCALATE_TO_HUMAN": "SIMULATED priority ticket dispatched to merchant account manager.",
            "NO_ACTION": "SIMULATED evaluation completed: No recovery action taken."
        }

        msg = simulations.get(action, f"SIMULATED execution of action '{action}'.")
        return {
            "status": "SIMULATED",
            "action": action,
            "message": msg,
            "timestamp": datetime.utcnow().isoformat()
        }
