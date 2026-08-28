import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import engine, SessionLocal, Base
from app.models import Merchant, MerchantPolicy, Customer, RevenueEvent, RecoveryAttempt, RecoveryOutcome, AuditLog
from seed import generate_seed_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Seed the database before running tests."""
    generate_seed_data()
    yield

def test_database_tables_populated():
    """Verify that all 7 tables contain seeded records."""
    db: Session = SessionLocal()
    try:
        assert db.query(Merchant).count() >= 3
        assert db.query(MerchantPolicy).count() >= 3
        assert db.query(Customer).count() >= 150
        assert db.query(RevenueEvent).count() >= 400
        assert db.query(RecoveryAttempt).count() >= 1
        assert db.query(RecoveryOutcome).count() >= 1
        assert db.query(AuditLog).count() >= 1
    finally:
        db.close()

def test_foreign_key_relationships():
    """Verify that relationships between RevenueEvent, Customer, and Merchant resolve cleanly."""
    db: Session = SessionLocal()
    try:
        event = db.query(RevenueEvent).filter(RevenueEvent.id == "EVT-2001").first()
        assert event is not None
        assert event.merchant.name == "UrbanKart Retail"
        assert event.customer.name == "Aarav Sharma"
        assert event.amount == 4999.00
        assert event.currency == "INR"
        assert event.event_type == "PAYMENT_FAILURE"
    finally:
        db.close()

def test_api_get_merchants():
    """Test GET /api/merchants endpoint."""
    response = client.get("/api/merchants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["name"] in ["UrbanKart Retail", "SaaSify Pro", "B2BSupply Co"]
    assert "policies" in data[0]

def test_api_get_revenue_events():
    """Test GET /api/revenue-events endpoint."""
    response = client.get("/api/revenue-events")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Check that event_type matches one of the 4 allowed workflows
    assert data[0]["event_type"] in [
        "PAYMENT_FAILURE", "CHECKOUT_ABANDONMENT", 
        "SUBSCRIPTION_FAILURE", "OVERDUE_INVOICE"
    ]

def test_api_get_single_revenue_event():
    """Test GET /api/revenue-events/{event_id} endpoint."""
    response = client.get("/api/revenue-events/EVT-2001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "EVT-2001"
    assert data["amount"] == "4999.00" or data["amount"] == 4999.0
