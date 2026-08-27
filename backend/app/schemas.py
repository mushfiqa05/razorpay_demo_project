from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class SimulationOutcome(str, Enum):
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"

class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str

class MerchantPolicySchema(BaseModel):
    id: str
    merchant_id: str
    max_recovery_attempts: int
    max_reminders: int
    max_discount_percentage: Decimal
    recovery_window_days: int
    minimum_expected_recovery: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateMerchantPolicyRequest(BaseModel):
    max_recovery_attempts: Optional[int] = None
    max_reminders: Optional[int] = None
    max_discount_percentage: Optional[float] = None
    recovery_window_days: Optional[int] = None
    minimum_expected_recovery: Optional[float] = None

class MerchantSchema(BaseModel):
    id: str
    name: str
    industry: str
    created_at: datetime
    policies: Optional[MerchantPolicySchema] = None

    model_config = ConfigDict(from_attributes=True)

class CustomerSchema(BaseModel):
    id: str
    merchant_id: str
    customer_reference: str
    name: str
    email: str
    customer_value: str
    previous_payment_count: int
    previous_success_count: int
    previous_recovery_attempts: int
    is_opted_out: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RevenueEventSchema(BaseModel):
    id: str
    merchant_id: str
    customer_id: str
    event_type: str
    amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str] = None
    failure_reason: Optional[str] = None
    event_timestamp: datetime
    days_overdue: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RevenueOpportunitySchema(BaseModel):
    event_id: str
    merchant_id: str
    customer_id: str
    event_type: str
    amount: float
    currency: str
    status: str
    revenue_at_risk: float
    likely_root_cause: str
    recoverability_probability: float
    expected_recoverable_value: float
    urgency_score: float
    customer_value_factor: float
    priority_score: float
    suggested_action: str
    days_overdue: int
    days_ago: int

class RevenueOpportunityListResponse(BaseModel):
    total_opportunities: int
    opportunities: List[RevenueOpportunitySchema]

class AIDecisionRecommendationSchema(BaseModel):
    event_id: str
    recommended_action: str
    reason: str
    confidence: float
    alternative_action: str
    recommendation_source: str

class RevenueOpportunityRecommendationResponse(BaseModel):
    event_id: str
    opportunity: RevenueOpportunitySchema
    recommendation: AIDecisionRecommendationSchema

class ExecuteRecoveryRequest(BaseModel):
    force_outcome: Optional[SimulationOutcome] = None
    offered_discount_pct: Optional[float] = 0.0

class ExecuteRecoveryResponse(BaseModel):
    event_id: str
    recommendation: Dict[str, Any]
    guardrail: Dict[str, Any]
    execution: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None
    workflow: Dict[str, Any]

class AuditLogSchema(BaseModel):
    id: str
    revenue_event_id: str
    action: str
    reason: str
    guardrail_result: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class RecoveryOutcomeSchema(BaseModel):
    id: str
    recovery_attempt_id: str
    outcome: str
    recovered_amount: Decimal
    outcome_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class RecoveryAttemptSchema(BaseModel):
    id: str
    revenue_event_id: str
    action_type: str
    attempt_number: int
    status: str
    attempted_at: datetime
    outcome: Optional[RecoveryOutcomeSchema] = None

    model_config = ConfigDict(from_attributes=True)
