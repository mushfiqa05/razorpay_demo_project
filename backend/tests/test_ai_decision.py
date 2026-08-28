import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models import AuditLog, RevenueEvent
from app.services.ai_decision import AIDecisionEngine, ALLOWED_ACTIONS
from seed import generate_seed_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_ai_test_database():
    """Ensure database has seed data prior to running AI tests."""
    generate_seed_data()

def test_1_high_recoverability_payment_failure_recommends_retry():
    """TEST 1: High recoverability payment failure with no previous attempt -> RETRY_PAYMENT."""
    opp = {
        "event_id": "EVT-TEST-1",
        "event_type": "PAYMENT_FAILURE",
        "revenue_at_risk": 4999.0,
        "likely_root_cause": "BANK_DECLINE",
        "recoverability_probability": 0.85,
        "days_overdue": 0
    }
    rec = AIDecisionEngine.recommend_next_action(opp)
    assert rec["recommended_action"] in ALLOWED_ACTIONS
    assert rec["recommended_action"] == "RETRY_PAYMENT"
    assert rec["confidence"] > 0.70

def test_2_payment_failure_after_retry_recommends_payment_link():
    """TEST 2: Payment failure after previous retry -> SEND_PAYMENT_LINK."""
    opp = {
        "event_id": "EVT-TEST-2",
        "event_type": "PAYMENT_FAILURE",
        "revenue_at_risk": 4999.0,
        "likely_root_cause": "AUTHENTICATION_FAILED",
        "recoverability_probability": 0.60,
        "days_overdue": 0
    }
    rec = AIDecisionEngine.recommend_next_action(opp)
    assert rec["recommended_action"] in ALLOWED_ACTIONS
    assert rec["recommended_action"] == "SEND_PAYMENT_LINK"

def test_3_checkout_abandonment_recommends_reminder_or_incentive():
    """TEST 3: Checkout abandonment -> SEND_REMINDER or OFFER_APPROVED_INCENTIVE."""
    opp_std = {
        "event_id": "EVT-TEST-3A",
        "event_type": "CHECKOUT_ABANDONMENT",
        "revenue_at_risk": 2000.0,
        "likely_root_cause": "LONG_INACTIVITY",
        "recoverability_probability": 0.65,
        "days_overdue": 0
    }
    rec_std = AIDecisionEngine.recommend_next_action(opp_std)
    assert rec_std["recommended_action"] == "SEND_REMINDER"

    opp_high = {
        "event_id": "EVT-TEST-3B",
        "event_type": "CHECKOUT_ABANDONMENT",
        "revenue_at_risk": 15000.0,
        "likely_root_cause": "HIGH_VALUE_ABANDONMENT",
        "recoverability_probability": 0.75,
        "days_overdue": 0
    }
    rec_high = AIDecisionEngine.recommend_next_action(opp_high)
    assert rec_high["recommended_action"] in ["OFFER_APPROVED_INCENTIVE", "SEND_REMINDER"]

def test_4_low_recoverability_recommends_no_action():
    """TEST 4: Low recoverability -> NO_ACTION."""
    opp = {
        "event_id": "EVT-TEST-4",
        "event_type": "PAYMENT_FAILURE",
        "revenue_at_risk": 1000.0,
        "likely_root_cause": "INSUFFICIENT_FUNDS_REPEATED",
        "recoverability_probability": 0.10,
        "days_overdue": 0
    }
    rec = AIDecisionEngine.recommend_next_action(opp)
    assert rec["recommended_action"] == "NO_ACTION"

def test_5_ai_returns_invalid_action_triggers_fallback():
    """TEST 5: AI returns invalid unpermitted action -> triggers fallback logic."""
    opp = {
        "event_id": "EVT-TEST-5",
        "event_type": "PAYMENT_FAILURE",
        "revenue_at_risk": 4999.0,
        "likely_root_cause": "BANK_DECLINE",
        "recoverability_probability": 0.80
    }
    # Mock external LLM returning an illegal unpermitted action 'TRANSFER_MONEY_ILLEGAL'
    with patch.object(AIDecisionEngine, "_call_external_llm", return_value={"recommended_action": "TRANSFER_MONEY_ILLEGAL", "reason": "invalid"}):
        rec = AIDecisionEngine.recommend_next_action(opp, api_key="test-key")
        assert rec["recommended_action"] in ALLOWED_ACTIONS
        assert rec["recommended_action"] != "TRANSFER_MONEY_ILLEGAL"

def test_6_ai_api_unavailable_triggers_fallback():
    """TEST 6: AI API unavailable/exception -> triggers fallback logic."""
    opp = {
        "event_id": "EVT-TEST-6",
        "event_type": "SUBSCRIPTION_FAILURE",
        "revenue_at_risk": 2499.0,
        "likely_root_cause": "EXPIRED_CARD",
        "recoverability_probability": 0.70
    }
    with patch.object(AIDecisionEngine, "_call_external_llm", side_effect=Exception("API Timeout")):
        rec = AIDecisionEngine.recommend_next_action(opp, api_key="test-key")
        assert rec["recommended_action"] in ALLOWED_ACTIONS
        assert rec["recommended_action"] == "SEND_PAYMENT_LINK"

def test_7_ai_returns_malformed_json_triggers_fallback():
    """TEST 7: AI returns malformed JSON -> triggers fallback logic."""
    opp = {
        "event_id": "EVT-TEST-7",
        "event_type": "OVERDUE_INVOICE",
        "revenue_at_risk": 60000.0,
        "likely_root_cause": "LONG_OVERDUE",
        "recoverability_probability": 0.50,
        "days_overdue": 40
    }
    with patch.object(AIDecisionEngine, "_call_external_llm", side_effect=ValueError("Invalid JSON")):
        rec = AIDecisionEngine.recommend_next_action(opp, api_key="test-key")
        assert rec["recommended_action"] in ALLOWED_ACTIONS
        assert rec["recommended_action"] == "ESCALATE_TO_HUMAN"

def test_8_ai_recommendation_api_and_audit_log():
    """TEST 8: POST /api/revenue-opportunities/{event_id}/recommendation stores audit log."""
    response = client.post("/api/revenue-opportunities/EVT-2001/recommendation")
    assert response.status_code == 200
    data = response.json()

    assert data["event_id"] == "EVT-2001"
    assert "opportunity" in data
    assert "recommendation" in data
    assert data["recommendation"]["recommended_action"] in ALLOWED_ACTIONS

    # Verify immutable audit log record created in database
    db: Session = SessionLocal()
    try:
        audit = db.query(AuditLog).filter(
            AuditLog.revenue_event_id == "EVT-2001",
            AuditLog.guardrail_result == "AI_RECOMMENDATION_GENERATED"
        ).first()
        assert audit is not None
        assert audit.action in ALLOWED_ACTIONS
        assert "AI Recommendation" in audit.reason
    finally:
        db.close()
