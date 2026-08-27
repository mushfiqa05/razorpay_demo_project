import uuid
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config import settings
from app.database import engine, Base, get_db
from app.models import Merchant, MerchantPolicy, Customer, RevenueEvent, RecoveryAttempt, AuditLog
from app.schemas import (
    HealthCheckResponse, MerchantSchema, MerchantPolicySchema, UpdateMerchantPolicyRequest,
    CustomerSchema, RevenueEventSchema, RevenueOpportunitySchema, RevenueOpportunityListResponse,
    RevenueOpportunityRecommendationResponse, AIDecisionRecommendationSchema,
    ExecuteRecoveryRequest, ExecuteRecoveryResponse, AuditLogSchema, RecoveryAttemptSchema
)
from app.services.revenue_opportunity import RevenueOpportunityEngine
from app.services.ai_decision import AIDecisionEngine
from app.services.recovery_workflow import RecoveryWorkflowController

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI Revenue Recovery Control Tower API for Razorpay Merchants"
)

# Enable CORS for React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def root_endpoint():
    """Root landing endpoint."""
    return {
        "message": "Welcome to the Razorpay AI Revenue Recovery Control Tower API",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthCheckResponse, tags=["Diagnostics"])
def health_check():
    """System Health Check Endpoint."""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENV
    )

@app.get("/api/merchants", response_model=List[MerchantSchema], tags=["Merchants"])
def get_merchants(db: Session = Depends(get_db)):
    """Fetch all merchant profiles and their associated policy rules."""
    return db.query(Merchant).all()

@app.put("/api/merchants/{merchant_id}/policy", response_model=MerchantPolicySchema, tags=["Merchants"])
def update_merchant_policy(
    merchant_id: str,
    policy_update: UpdateMerchantPolicyRequest,
    db: Session = Depends(get_db)
):
    """
    Phase 6.2 Fix: Persists merchant policy guardrail changes directly to backend database.
    The Guardrail Engine immediately reads these updated values.
    """
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant '{merchant_id}' not found")

    policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == merchant_id).first()
    if not policy:
        policy = MerchantPolicy(id=f"POL-{merchant_id}", merchant_id=merchant_id)
        db.add(policy)

    if policy_update.max_recovery_attempts is not None:
        policy.max_recovery_attempts = policy_update.max_recovery_attempts
    if policy_update.max_reminders is not None:
        policy.max_reminders = policy_update.max_reminders
    if policy_update.max_discount_percentage is not None:
        policy.max_discount_percentage = policy_update.max_discount_percentage
    if policy_update.recovery_window_days is not None:
        policy.recovery_window_days = policy_update.recovery_window_days
    if policy_update.minimum_expected_recovery is not None:
        policy.minimum_expected_recovery = policy_update.minimum_expected_recovery

    db.commit()
    db.refresh(policy)
    return policy

@app.get("/api/customers", response_model=List[CustomerSchema], tags=["Customers"])
def get_customers(
    merchant_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """Fetch customer profiles, optionally filtered by merchant_id."""
    query = db.query(Customer)
    if merchant_id:
        query = query.filter(Customer.merchant_id == merchant_id)
    return query.limit(limit).all()

@app.get("/api/revenue-events", response_model=List[RevenueEventSchema], tags=["Revenue Events"])
def get_revenue_events(
    merchant_id: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """Fetch raw revenue events from database."""
    query = db.query(RevenueEvent)
    if merchant_id:
        query = query.filter(RevenueEvent.merchant_id == merchant_id)
    if event_type:
        query = query.filter(RevenueEvent.event_type == event_type)
    if status:
        query = query.filter(RevenueEvent.status == status)
    
    return query.order_by(RevenueEvent.created_at.desc()).limit(limit).all()

@app.get("/api/revenue-events/{event_id}", response_model=RevenueEventSchema, tags=["Revenue Events"])
def get_revenue_event_by_id(event_id: str, db: Session = Depends(get_db)):
    """Fetch a single raw revenue event by its unique ID."""
    event = db.query(RevenueEvent).filter(RevenueEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Revenue event '{event_id}' not found")
    return event

@app.get("/api/revenue-opportunities", response_model=RevenueOpportunityListResponse, tags=["Revenue Opportunity Engine"])
def get_revenue_opportunities(
    merchant_id: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    minimum_priority: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """
    Revenue Opportunity Priority Queue Endpoint.
    Retrieves revenue events from database, runs RevenueOpportunityEngine,
    and returns opportunities sorted by Priority Score descending.
    """
    query = db.query(RevenueEvent)
    if merchant_id:
        query = query.filter(RevenueEvent.merchant_id == merchant_id)
    if event_type:
        query = query.filter(RevenueEvent.event_type == event_type)
    if status:
        query = query.filter(RevenueEvent.status == status)

    events = query.limit(limit).all()

    opportunities = []
    for event in events:
        customer = db.query(Customer).filter(Customer.id == event.customer_id).first()
        opp_data = RevenueOpportunityEngine.analyze_event(event, customer)
        
        if minimum_priority is not None and opp_data["priority_score"] < minimum_priority:
            continue
            
        opportunities.append(opp_data)

    opportunities.sort(key=lambda x: x["priority_score"], reverse=True)

    return RevenueOpportunityListResponse(
        total_opportunities=len(opportunities),
        opportunities=opportunities
    )

@app.get("/api/revenue-opportunities/{event_id}", response_model=RevenueOpportunitySchema, tags=["Revenue Opportunity Engine"])
def get_revenue_opportunity_by_id(event_id: str, db: Session = Depends(get_db)):
    """Fetch single detailed opportunity analysis by revenue event ID."""
    event = db.query(RevenueEvent).filter(RevenueEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Revenue event '{event_id}' not found")

    customer = db.query(Customer).filter(Customer.id == event.customer_id).first()
    opp_data = RevenueOpportunityEngine.analyze_event(event, customer)
    return opp_data

@app.post("/api/revenue-opportunities/{event_id}/recommendation", response_model=RevenueOpportunityRecommendationResponse, tags=["AI Decision Engine"])
def generate_opportunity_recommendation(event_id: str, db: Session = Depends(get_db)):
    """
    Phase 4: AI Decision Engine Endpoint.
    Generates next-best action recommendation and logs advisory audit record.
    """
    event = db.query(RevenueEvent).filter(RevenueEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Revenue event '{event_id}' not found")

    customer = db.query(Customer).filter(Customer.id == event.customer_id).first()
    opportunity = RevenueOpportunityEngine.analyze_event(event, customer)
    recommendation = AIDecisionEngine.recommend_next_action(opportunity, api_key=settings.LLM_API_KEY)

    audit_entry = AuditLog(
        id=f"AUD-REC-{uuid.uuid4().hex[:8]}",
        revenue_event_id=event_id,
        action=recommendation["recommended_action"],
        reason=f"AI Recommendation ({recommendation['recommendation_source']}): {recommendation['reason']}",
        guardrail_result="AI_RECOMMENDATION_GENERATED",
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()

    return RevenueOpportunityRecommendationResponse(
        event_id=event_id,
        opportunity=opportunity,
        recommendation=recommendation
    )

@app.post("/api/revenue-opportunities/{event_id}/execute-recovery", response_model=ExecuteRecoveryResponse, tags=["Bounded Workflow Controller"])
def execute_recovery_workflow(
    event_id: str, 
    request_data: Optional[ExecuteRecoveryRequest] = None, 
    db: Session = Depends(get_db)
):
    """
    Phase 5: Bounded Recovery Workflow Execution Endpoint.
    
    1. Loads event, customer, and merchant policy.
    2. Evaluates Phase 3 Opportunity Engine & Phase 4 AI Recommendation.
    3. Evaluates Phase 5 Guardrail Engine.
    4. If BLOCKED: logs audit and halts workflow.
    5. If ALLOWED: executes single simulated action, logs attempts & outcomes, updates event status.
    """
    try:
        force_out = request_data.force_outcome.value if (request_data and request_data.force_outcome) else None
        disc_pct = request_data.offered_discount_pct if request_data else 0.0

        res = RecoveryWorkflowController.execute_recovery_step(
            event_id=event_id,
            db=db,
            api_key=settings.LLM_API_KEY,
            force_outcome=force_out,
            offered_discount_pct=disc_pct
        )
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))

@app.get("/api/audit-logs", response_model=List[AuditLogSchema], tags=["Audit Logs"])
def get_audit_logs(
    merchant_id: Optional[str] = None,
    event_id: Optional[str] = None,
    action: Optional[str] = None,
    guardrail_result: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """
    Phase 6.2 Fix #1: Real Audit Trail Endpoint.
    Returns immutable audit records directly from database.
    """
    query = db.query(AuditLog)
    if event_id:
        query = query.filter(AuditLog.revenue_event_id == event_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if guardrail_result:
        query = query.filter(AuditLog.guardrail_result == guardrail_result)
    if merchant_id:
        query = query.join(RevenueEvent, AuditLog.revenue_event_id == RevenueEvent.id).filter(RevenueEvent.merchant_id == merchant_id)

    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

@app.get("/api/recovery-attempts", response_model=List[RecoveryAttemptSchema], tags=["Recovery Activity"])
def get_recovery_attempts(
    merchant_id: Optional[str] = None,
    event_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """
    Phase 6.2 Fix #6: Real Recovery Attempts Endpoint.
    Returns actual recovery attempt execution logs stored in database.
    """
    query = db.query(RecoveryAttempt)
    if event_id:
        query = query.filter(RecoveryAttempt.revenue_event_id == event_id)
    if status:
        query = query.filter(RecoveryAttempt.status == status)
    if merchant_id:
        query = query.join(RevenueEvent, RecoveryAttempt.revenue_event_id == RevenueEvent.id).filter(RevenueEvent.merchant_id == merchant_id)

    return query.order_by(RecoveryAttempt.attempted_at.desc()).limit(limit).all()
