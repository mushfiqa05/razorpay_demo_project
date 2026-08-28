import pytest
from datetime import datetime
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models import MerchantPolicy, Customer, RevenueEvent, RecoveryAttempt, AuditLog
from app.services.guardrail import GuardrailEngine
from app.services.recovery_workflow import RecoveryWorkflowController
from seed import generate_seed_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_workflow_test_database():
    """Seed database before running guardrail tests."""
    generate_seed_data()

class MockPolicy:
    def __init__(self, max_attempts=3, max_reminders=2, max_discount=10.0, window_days=14, min_expected=100.0):
        self.max_recovery_attempts = max_attempts
        self.max_reminders = max_reminders
        self.max_discount_percentage = max_discount
        self.recovery_window_days = window_days
        self.minimum_expected_recovery = min_expected

class MockCust:
    def __init__(self, is_opted_out=False):
        self.is_opted_out = is_opted_out

def test_1_valid_action_and_policy_is_allowed():
    """TEST 1: Valid action + valid policy -> ALLOWED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "RETRY_PAYMENT"}
    policy = MockPolicy()
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust)
    assert res["allowed"] is True
    assert res["checks"]["action_allowed"] is True

def test_2_unknown_action_is_blocked():
    """TEST 2: Unknown/unpermitted action -> BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "TRANSFER_MONEY_ILLEGAL"}
    policy = MockPolicy()
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust)
    assert res["allowed"] is False
    assert res["checks"]["action_allowed"] is False

def test_3_max_attempts_reached_is_blocked():
    """TEST 3: Maximum recovery attempts reached -> BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "RETRY_PAYMENT"}
    policy = MockPolicy(max_attempts=3)
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust, previous_attempts_count=3)
    assert res["allowed"] is False
    assert res["checks"]["attempt_limit"] is False

def test_4_max_reminders_reached_is_blocked():
    """TEST 4: Maximum reminders reached -> BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "SEND_REMINDER"}
    policy = MockPolicy(max_reminders=2)
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust, previous_reminders_count=2)
    assert res["allowed"] is False
    assert res["checks"]["reminder_limit"] is False

def test_5_recovery_window_expired_is_blocked():
    """TEST 5: Recovery window expired -> BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 20}  # 20 days > 14 max window
    rec = {"recommended_action": "SEND_PAYMENT_LINK"}
    policy = MockPolicy(window_days=14)
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust)
    assert res["allowed"] is False
    assert res["checks"]["recovery_window"] is False

def test_6_below_minimum_expected_recovery_is_blocked():
    """TEST 6: Expected recovery below minimum threshold -> BLOCKED."""
    opp = {"expected_recoverable_value": 50.0, "days_ago": 2}  # ₹50 < ₹100 minimum threshold
    rec = {"recommended_action": "SEND_PAYMENT_LINK"}
    policy = MockPolicy(min_expected=100.0)
    cust = MockCust()

    res = GuardrailEngine.validate_action(opp, rec, policy, cust)
    assert res["allowed"] is False
    assert res["checks"]["minimum_expected_recovery"] is False

def test_7_customer_opt_out_blocks_communication():
    """TEST 7: Customer opted out -> communication action BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "SEND_REMINDER"}
    policy = MockPolicy()
    cust_opted_out = MockCust(is_opted_out=True)

    res = GuardrailEngine.validate_action(opp, rec, policy, cust_opted_out)
    assert res["allowed"] is False
    assert res["checks"]["customer_opt_out"] is False

def test_8_incentive_exceeds_allowed_discount_is_blocked():
    """TEST 8: Incentive exceeds allowed discount -> BLOCKED."""
    opp = {"expected_recoverable_value": 2000.0, "days_ago": 2}
    rec = {"recommended_action": "OFFER_APPROVED_INCENTIVE"}
    policy = MockPolicy(max_discount=10.0)
    cust = MockCust()

    # Offered 25% discount > 10% max allowed
    res = GuardrailEngine.validate_action(opp, rec, policy, cust, offered_discount_pct=25.0)
    assert res["allowed"] is False
    assert res["checks"]["incentive_limit"] is False

def test_9_valid_retry_simulates_execution():
    """TEST 9: Valid retry -> simulated execution payload."""
    db: Session = SessionLocal()
    try:
        res = RecoveryWorkflowController.execute_recovery_step("EVT-2001", db, force_outcome="RECOVERED")
        assert res["guardrail"]["allowed"] is True
        assert res["execution"]["status"] == "SIMULATED"
        assert "SIMULATED" in res["execution"]["message"]
    finally:
        db.close()

def test_10_successful_recovery_stops_workflow():
    """TEST 10: Successful recovery -> workflow STOPPED (RECOVERY_SUCCESSFUL)."""
    db: Session = SessionLocal()
    try:
        # Create fresh test event
        evt_id = "EVT-TEST-10"
        evt = RevenueEvent(
            id=evt_id,
            merchant_id="MCH-001",
            customer_id="CUST-101",
            event_type="PAYMENT_FAILURE",
            amount=Decimal("5000.00"),
            currency="INR",
            status="OPEN",
            payment_method="CREDIT_CARD",
            failure_reason="INSUFFICIENT_FUNDS",
            event_timestamp=datetime.utcnow()
        )
        db.add(evt)
        db.commit()

        res = RecoveryWorkflowController.execute_recovery_step(evt_id, db, force_outcome="RECOVERED")
        assert res["guardrail"]["allowed"] is True
        assert res["outcome"]["status"] == "RECOVERED"
        assert res["workflow"]["status"] == "STOPPED"
        assert res["workflow"]["stop_reason"] == "RECOVERY_SUCCESSFUL"
    finally:
        db.close()

def test_11_failed_recovery_sets_failed_status():
    """TEST 11: Failed recovery -> outcome FAILED."""
    db: Session = SessionLocal()
    try:
        res = RecoveryWorkflowController.execute_recovery_step("EVT-2004", db, force_outcome="FAILED")
        assert res["outcome"]["status"] == "FAILED"
        assert res["outcome"]["recovered_amount"] == 0.0
    finally:
        db.close()

def test_12_audit_logs_created_chronologically():
    """TEST 12: Audit logs created chronologically during execution."""
    db: Session = SessionLocal()
    try:
        res = RecoveryWorkflowController.execute_recovery_step("EVT-2005", db, force_outcome="RECOVERED")
        logs = db.query(AuditLog).filter(AuditLog.revenue_event_id == "EVT-2005").order_by(AuditLog.timestamp.asc()).all()
        assert len(logs) >= 3
        results = [l.guardrail_result for l in logs]
        assert "PASSED" in results or "AI_RECOMMENDATION_GENERATED" in results
    finally:
        db.close()

def test_13_recovered_amount_never_exceeds_revenue_at_risk():
    """TEST 13: Recovered amount never exceeds revenue at risk."""
    db: Session = SessionLocal()
    try:
        evt = db.query(RevenueEvent).filter(RevenueEvent.id == "EVT-2007").first()
        res = RecoveryWorkflowController.execute_recovery_step("EVT-2007", db, force_outcome="RECOVERED")
        assert res["guardrail"]["allowed"] is True
        assert res["outcome"]["recovered_amount"] <= float(evt.amount)
    finally:
        db.close()

def test_14_workflow_cannot_exceed_max_attempts_endpoint():
    """TEST 14: Execution API blocks when max attempts reached."""
    response = client.post("/api/revenue-opportunities/EVT-2006/execute-recovery")
    assert response.status_code == 200
    data = response.json()
    assert data["guardrail"]["allowed"] is False
    assert data["workflow"]["status"] == "STOPPED"
    assert data["workflow"]["stop_reason"] == "GUARDRAIL_BLOCKED"

# Phase 6.2 Fix Tests

def test_15_audit_logs_endpoint_returns_real_records():
    """TEST 15: GET /api/audit-logs returns real database records."""
    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "revenue_event_id" in data[0]
        assert "guardrail_result" in data[0]

def test_16_recovery_attempts_endpoint_returns_actual_attempts():
    """TEST 16: GET /api/recovery-attempts returns actual execution attempt records."""
    response = client.get("/api/recovery-attempts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "action_type" in data[0]
        assert "attempt_number" in data[0]

def test_17_force_outcome_validation_rejects_invalid_values():
    """TEST 17: Execute recovery rejects invalid force_outcome values (e.g. HACKED) with HTTP 422."""
    res_valid = client.post("/api/revenue-opportunities/EVT-2007/execute-recovery", json={"force_outcome": "RECOVERED"})
    assert res_valid.status_code == 200

    res_invalid = client.post("/api/revenue-opportunities/EVT-2007/execute-recovery", json={"force_outcome": "HACKED"})
    assert res_invalid.status_code == 422

def test_18_terminal_state_recovered_event_cannot_be_recovered_again():
    """TEST 18: A RECOVERED event cannot undergo recovery again."""
    db: Session = SessionLocal()
    try:
        evt = db.query(RevenueEvent).filter(RevenueEvent.id == "EVT-2001").first()
        evt.status = "RECOVERED"
        db.commit()

        res = RecoveryWorkflowController.execute_recovery_step("EVT-2001", db, force_outcome="RECOVERED")
        assert res["workflow"]["status"] == "STOPPED"
        assert res["workflow"]["stop_reason"] == "EVENT_ALREADY_RECOVERED"
        assert res["guardrail"]["allowed"] is False
    finally:
        db.close()

def test_19_merchant_policy_persistence_and_guardrail_enforcement():
    """TEST 19: Merchant policy update persists to DB and guardrail reads updated policy."""
    db: Session = SessionLocal()
    try:
        merchant = db.query(MerchantPolicy).first()
        m_id = merchant.merchant_id
    finally:
        db.close()

    update_res = client.put(f"/api/merchants/{m_id}/policy", json={"max_recovery_attempts": 1})
    assert update_res.status_code == 200
    assert update_res.json()["max_recovery_attempts"] == 1

    db: Session = SessionLocal()
    try:
        pol = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == m_id).first()
        assert pol.max_recovery_attempts == 1
    finally:
        db.close()
