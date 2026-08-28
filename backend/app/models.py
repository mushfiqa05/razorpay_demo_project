from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Merchant(Base):
    """
    1. MERCHANTS: Stores fictional Razorpay merchant profiles.
    """
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    policies = relationship("MerchantPolicy", back_populates="merchant", uselist=False, cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    revenue_events = relationship("RevenueEvent", back_populates="merchant", cascade="all, delete-orphan")


class MerchantPolicy(Base):
    """
    2. MERCHANT_POLICIES: Stores merchant-defined recovery policy rules & guardrails.
    """
    __tablename__ = "merchant_policies"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, unique=True)
    max_recovery_attempts = Column(Integer, default=3)
    max_reminders = Column(Integer, default=2)
    max_discount_percentage = Column(Numeric(5, 2), default=10.00)
    recovery_window_days = Column(Integer, default=14)
    minimum_expected_recovery = Column(Numeric(12, 2), default=100.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="policies")


class Customer(Base):
    """
    3. CUSTOMERS: Stores customer details and historical payment performance metrics.
    """
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    customer_reference = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    customer_value = Column(String, default="STANDARD")  # HIGH_VALUE, STANDARD, AT_RISK
    previous_payment_count = Column(Integer, default=0)
    previous_success_count = Column(Integer, default=0)
    previous_recovery_attempts = Column(Integer, default=0)
    is_opted_out = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    revenue_events = relationship("RevenueEvent", back_populates="customer", cascade="all, delete-orphan")


class RevenueEvent(Base):
    """
    4. REVENUE_EVENTS: Represents a revenue opportunity or leakage event across 4 workflows:
       - PAYMENT_FAILURE
       - CHECKOUT_ABANDONMENT
       - SUBSCRIPTION_FAILURE
       - OVERDUE_INVOICE
    """
    __tablename__ = "revenue_events"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    event_type = Column(String, nullable=False)  # PAYMENT_FAILURE, CHECKOUT_ABANDONMENT, SUBSCRIPTION_FAILURE, OVERDUE_INVOICE
    amount = Column(Numeric(12, 2), nullable=False)  # Stored as exact monetary decimal (e.g. 4999.00)
    currency = Column(String, default="INR")
    status = Column(String, default="OPEN")  # OPEN, IN_RECOVERY, RECOVERED, FAILED, STOPPED
    payment_method = Column(String, nullable=True)  # UPI, CREDIT_CARD, NETBANKING, DEBIT_CARD, INVOICE
    failure_reason = Column(String, nullable=True)
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    days_overdue = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="revenue_events")
    customer = relationship("Customer", back_populates="revenue_events")
    recovery_attempts = relationship("RecoveryAttempt", back_populates="revenue_event", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="revenue_event", cascade="all, delete-orphan")


class RecoveryAttempt(Base):
    """
    5. RECOVERY_ATTEMPTS: Stores recovery intervention steps taken for an event.
       Allowed action_type: RETRY_PAYMENT, SEND_PAYMENT_LINK, SEND_REMINDER, OFFER_APPROVED_INCENTIVE, ESCALATE_TO_HUMAN, NO_ACTION
    """
    __tablename__ = "recovery_attempts"

    id = Column(String, primary_key=True, index=True)
    revenue_event_id = Column(String, ForeignKey("revenue_events.id"), nullable=False)
    action_type = Column(String, nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(String, default="PENDING")  # PENDING, SUCCESS, FAILED, STOPPED, BLOCKED
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    revenue_event = relationship("RevenueEvent", back_populates="recovery_attempts")
    outcome = relationship("RecoveryOutcome", back_populates="recovery_attempt", uselist=False, cascade="all, delete-orphan")


class RecoveryOutcome(Base):
    """
    6. RECOVERY_OUTCOMES: Stores final outcome of a recovery attempt.
       Outcomes: RECOVERED, FAILED, STOPPED, BLOCKED
    """
    __tablename__ = "recovery_outcomes"

    id = Column(String, primary_key=True, index=True)
    recovery_attempt_id = Column(String, ForeignKey("recovery_attempts.id"), nullable=False, unique=True)
    outcome = Column(String, nullable=False)  # RECOVERED, FAILED, STOPPED, BLOCKED
    recovered_amount = Column(Numeric(12, 2), default=0.00)
    outcome_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recovery_attempt = relationship("RecoveryAttempt", back_populates="outcome")


class AuditLog(Base):
    """
    7. AUDIT_LOGS: Immutable ledger recording system decisions, reasoning, and policy guardrail checks.
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    revenue_event_id = Column(String, ForeignKey("revenue_events.id"), nullable=False)
    action = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    guardrail_result = Column(String, nullable=False)  # PASSED, BLOCKED, VIOLATED_MAX_ATTEMPTS, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    revenue_event = relationship("RevenueEvent", back_populates="audit_logs")
