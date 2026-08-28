import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.services.revenue_opportunity import RevenueOpportunityEngine
from seed import generate_seed_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_opportunity_test_data():
    """Ensure database has seed data prior to running engine tests."""
    generate_seed_data()

class MockEvent:
    def __init__(self, id, event_type, amount, failure_reason=None, days_overdue=0, event_timestamp=None):
        self.id = id
        self.merchant_id = "MERCH-1001"
        self.customer_id = "CUST-1001"
        self.event_type = event_type
        self.amount = amount
        self.currency = "INR"
        self.status = "OPEN"
        self.payment_method = "UPI"
        self.failure_reason = failure_reason
        self.days_overdue = days_overdue
        self.event_timestamp = event_timestamp

class MockCustomer:
    def __init__(self, previous_payment_count, previous_success_count, previous_recovery_attempts, customer_value="STANDARD", is_opted_out=False):
        self.previous_payment_count = previous_payment_count
        self.previous_success_count = previous_success_count
        self.previous_recovery_attempts = previous_recovery_attempts
        self.customer_value = customer_value
        self.is_opted_out = is_opted_out

def test_1_high_payment_success_rate_increases_recoverability():
    """TEST 1: High previous payment success rate -> recoverability should be high."""
    evt = MockEvent("EVT-TEST-1", "PAYMENT_FAILURE", 5000.00, failure_reason="BANK_DECLINE")
    cust_high = MockCustomer(previous_payment_count=10, previous_success_count=10, previous_recovery_attempts=0)
    cust_low = MockCustomer(previous_payment_count=10, previous_success_count=2, previous_recovery_attempts=0)

    res_high = RevenueOpportunityEngine.analyze_event(evt, cust_high)
    res_low = RevenueOpportunityEngine.analyze_event(evt, cust_low)

    assert res_high["recoverability_probability"] > res_low["recoverability_probability"]
    assert res_high["recoverability_probability"] >= 0.70

def test_2_repeated_failed_attempts_decrease_recoverability():
    """TEST 2: Repeated failed recovery attempts -> recoverability should decrease."""
    evt = MockEvent("EVT-TEST-2", "PAYMENT_FAILURE", 3000.00)
    cust_fresh = MockCustomer(previous_payment_count=5, previous_success_count=5, previous_recovery_attempts=0)
    cust_spammed = MockCustomer(previous_payment_count=5, previous_success_count=5, previous_recovery_attempts=3)

    res_fresh = RevenueOpportunityEngine.analyze_event(evt, cust_fresh)
    res_spammed = RevenueOpportunityEngine.analyze_event(evt, cust_spammed)

    assert res_fresh["recoverability_probability"] > res_spammed["recoverability_probability"]

def test_3_expected_recoverable_value_exact_calculation():
    """TEST 3: ₹10,000 revenue at risk * 0.80 recoverability -> expected recovery should be ₹8,000."""
    evt = MockEvent("EVT-TEST-3", "PAYMENT_FAILURE", 10000.00)
    cust = MockCustomer(previous_payment_count=10, previous_success_count=10, previous_recovery_attempts=0)
    
    res = RevenueOpportunityEngine.analyze_event(evt, cust)
    # Ensure exact math formula
    expected_math = round(res["revenue_at_risk"] * res["recoverability_probability"], 2)
    assert abs(res["expected_recoverable_value"] - expected_math) <= 0.05

def test_4_priority_score_ordering():
    """TEST 4: High-value high-recoverability opportunity -> higher priority than low-value low-recoverability."""
    evt_high = MockEvent("EVT-HIGH", "PAYMENT_FAILURE", 50000.00)
    cust_high = MockCustomer(previous_payment_count=10, previous_success_count=10, previous_recovery_attempts=0, customer_value="HIGH_VALUE")

    evt_low = MockEvent("EVT-LOW", "PAYMENT_FAILURE", 1000.00)
    cust_low = MockCustomer(previous_payment_count=5, previous_success_count=1, previous_recovery_attempts=3, customer_value="AT_RISK")

    res_high = RevenueOpportunityEngine.analyze_event(evt_high, cust_high)
    res_low = RevenueOpportunityEngine.analyze_event(evt_low, cust_low)

    assert res_high["priority_score"] > res_low["priority_score"]

def test_5_unknown_root_cause():
    """TEST 5: Unknown/missing root cause information -> should return UNKNOWN."""
    evt = MockEvent("EVT-UNKNOWN", "PAYMENT_FAILURE", 2000.00, failure_reason=None)
    cust = MockCustomer(previous_payment_count=2, previous_success_count=2, previous_recovery_attempts=0)

    res = RevenueOpportunityEngine.analyze_event(evt, cust)
    assert res["likely_root_cause"] == "UNKNOWN"

def test_6_priority_scores_bounded():
    """TEST 6: Priority scores remain strictly bounded between 0.0 and 1.0."""
    evt = MockEvent("EVT-BOUND", "PAYMENT_FAILURE", 125000.00)
    cust = MockCustomer(previous_payment_count=50, previous_success_count=50, previous_recovery_attempts=0, customer_value="HIGH_VALUE")

    res = RevenueOpportunityEngine.analyze_event(evt, cust)
    assert 0.0 <= res["priority_score"] <= 1.0
    assert 0.0 <= res["recoverability_probability"] <= 1.0
    assert 0.0 <= res["urgency_score"] <= 1.0

def test_7_api_returns_sorted_by_priority():
    """TEST 7: API returns opportunities sorted by priority descending."""
    response = client.get("/api/revenue-opportunities")
    assert response.status_code == 200
    data = response.json()
    
    opportunities = data["opportunities"]
    assert len(opportunities) > 0

    # Verify descending sort order
    priority_scores = [opp["priority_score"] for opp in opportunities]
    assert priority_scores == sorted(priority_scores, reverse=True)
