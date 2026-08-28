import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import (
    Merchant, MerchantPolicy, Customer, 
    RevenueEvent, RecoveryAttempt, RecoveryOutcome, AuditLog
)

# Seed dataset parameters
NUM_CUSTOMERS = 150
NUM_EVENTS = 400

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Aditya", "Pooja",
    "Rahul", "Sneha", "Karan", "Divya", "Siddharth", "Ishita", "Amit", "Kavya",
    "Varun", "Riya", "Manish", "Shreya", "Dev", "Meera", "Yash", "Tanvi"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Mehta", "Gupta", "Singh", "Kumar", "Joshi",
    "Rao", "Nair", "Iyer", "Deshmukh", "Chopra", "Reddy", "Kulkarni", "Bhat"
]

INDIAN_CITIES = ["Mumbai", "Bengaluru", "Delhi", "Hyderabad", "Pune", "Chennai", "Ahmedabad", "Kolkata"]

def generate_seed_data():
    """
    Populates the database with realistic synthetic data for Razorpay merchants,
    customers, revenue events, recovery attempts, outcomes, and audit logs.
    """
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # 1. Create Merchants & Merchant Policies
        print("Creating merchants and policies...")
        merchants_data = [
            {
                "id": "MERCH-1001",
                "name": "UrbanKart Retail",
                "industry": "E-Commerce & Direct-to-Consumer",
                "max_attempts": 3,
                "max_reminders": 2,
                "max_discount": Decimal("10.00"),
                "window_days": 14,
                "min_recovery": Decimal("100.00")
            },
            {
                "id": "MERCH-1002",
                "name": "SaaSify Pro",
                "industry": "Software & Subscription Services",
                "max_attempts": 4,
                "max_reminders": 3,
                "max_discount": Decimal("15.00"),
                "window_days": 21,
                "min_recovery": Decimal("250.00")
            },
            {
                "id": "MERCH-1003",
                "name": "B2BSupply Co",
                "industry": "Wholesale & Business Supplies",
                "max_attempts": 2,
                "max_reminders": 2,
                "max_discount": Decimal("5.00"),
                "window_days": 30,
                "min_recovery": Decimal("1000.00")
            }
        ]

        merchants = []
        for m in merchants_data:
            merchant = Merchant(
                id=m["id"],
                name=m["name"],
                industry=m["industry"],
                created_at=datetime.utcnow() - timedelta(days=180)
            )
            policy = MerchantPolicy(
                id=f"POL-{m['id'].split('-')[1]}",
                merchant_id=m["id"],
                max_recovery_attempts=m["max_attempts"],
                max_reminders=m["max_reminders"],
                max_discount_percentage=m["max_discount"],
                recovery_window_days=m["window_days"],
                minimum_expected_recovery=m["min_recovery"],
                created_at=datetime.utcnow() - timedelta(days=180)
            )
            db.add(merchant)
            db.add(policy)
            merchants.append(merchant)

        db.commit()

        # 2. Create Customers
        print("Creating synthetic customers...")
        customers = []

        # Explicit Special Case 1: High Recoverability Customer
        c_high = Customer(
            id="CUST-1001",
            merchant_id="MERCH-1001",
            customer_reference="RAZOR-CUST-1001",
            name="Aarav Sharma",
            email="aarav.sharma@example.com",
            customer_value="HIGH_VALUE",
            previous_payment_count=12,
            previous_success_count=12,
            previous_recovery_attempts=0,
            is_opted_out=False,
            created_at=datetime.utcnow() - timedelta(days=120)
        )
        db.add(c_high)
        customers.append(c_high)

        # Explicit Special Case 2: Low Recoverability Customer
        c_low = Customer(
            id="CUST-1002",
            merchant_id="MERCH-1001",
            customer_reference="RAZOR-CUST-1002",
            name="Vikram Patel",
            email="vikram.patel@example.com",
            customer_value="AT_RISK",
            previous_payment_count=6,
            previous_success_count=1,
            previous_recovery_attempts=4,
            is_opted_out=False,
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        db.add(c_low)
        customers.append(c_low)

        # Explicit Special Case 3: Opted-Out Customer (Guardrail Case)
        c_opt = Customer(
            id="CUST-1003",
            merchant_id="MERCH-1002",
            customer_reference="RAZOR-CUST-1003",
            name="Priya Mehta",
            email="priya.mehta@example.com",
            customer_value="STANDARD",
            previous_payment_count=4,
            previous_success_count=4,
            previous_recovery_attempts=1,
            is_opted_out=True,
            created_at=datetime.utcnow() - timedelta(days=60)
        )
        db.add(c_opt)
        customers.append(c_opt)

        # Generate Remaining Customers (CUST-1004 to CUST-1150)
        for i in range(4, NUM_CUSTOMERS + 1):
            cust_id = f"CUST-{1000 + i}"
            m_id = random.choice(["MERCH-1001", "MERCH-1002", "MERCH-1003"])
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            
            total_pay = random.randint(1, 20)
            success_pay = random.randint(int(total_pay * 0.4), total_pay)
            prev_attempts = random.randint(0, 3)
            
            c_tier = "STANDARD"
            if success_pay >= 10:
                c_tier = "HIGH_VALUE"
            elif success_pay <= 2 and total_pay >= 5:
                c_tier = "AT_RISK"

            cust = Customer(
                id=cust_id,
                merchant_id=m_id,
                customer_reference=f"RAZOR-CUST-{1000 + i}",
                name=f"{fname} {lname}",
                email=f"{fname.lower()}.{lname.lower()}{i}@example.com",
                customer_value=c_tier,
                previous_payment_count=total_pay,
                previous_success_count=success_pay,
                previous_recovery_attempts=prev_attempts,
                is_opted_out=(random.random() < 0.05),  # 5% opt-out rate
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 180))
            )
            db.add(cust)
            customers.append(cust)

        db.commit()

        # 3. Create Revenue Events across 4 event types
        print("Creating synthetic revenue events...")
        revenue_events = []

        # Explicit Scenario Events
        scenarios = [
            # 1. High Recoverability Event
            {
                "id": "EVT-2001",
                "merchant_id": "MERCH-1001",
                "customer_id": "CUST-1001",
                "event_type": "PAYMENT_FAILURE",
                "amount": Decimal("4999.00"),
                "currency": "INR",
                "status": "OPEN",
                "payment_method": "UPI",
                "failure_reason": "BANK_DECLINE_TIMED_OUT",
                "days_overdue": 0,
                "days_ago": 1
            },
            # 2. Low Recoverability Event
            {
                "id": "EVT-2002",
                "merchant_id": "MERCH-1001",
                "customer_id": "CUST-1002",
                "event_type": "PAYMENT_FAILURE",
                "amount": Decimal("1999.00"),
                "currency": "INR",
                "status": "FAILED",
                "payment_method": "CREDIT_CARD",
                "failure_reason": "INSUFFICIENT_FUNDS_REPEATED",
                "days_overdue": 0,
                "days_ago": 12
            },
            # 3. High-Value Overdue Invoice
            {
                "id": "EVT-2003",
                "merchant_id": "MERCH-1003",
                "customer_id": "CUST-1001",
                "event_type": "OVERDUE_INVOICE",
                "amount": Decimal("125000.00"),
                "currency": "INR",
                "status": "OPEN",
                "payment_method": "INVOICE",
                "failure_reason": "OVERDUE_PAYMENT_45D",
                "days_overdue": 45,
                "days_ago": 45
            },
            # 4. Checkout Abandonment Event
            {
                "id": "EVT-2004",
                "merchant_id": "MERCH-1001",
                "customer_id": "CUST-1004",
                "event_type": "CHECKOUT_ABANDONMENT",
                "amount": Decimal("14999.00"),
                "currency": "INR",
                "status": "OPEN",
                "payment_method": "CREDIT_CARD",
                "failure_reason": "CART_INACTIVITY_HIGH_VALUE",
                "days_overdue": 0,
                "days_ago": 2
            },
            # 5. Subscription Failure Event
            {
                "id": "EVT-2005",
                "merchant_id": "MERCH-1002",
                "customer_id": "CUST-1005",
                "event_type": "SUBSCRIPTION_FAILURE",
                "amount": Decimal("2499.00"),
                "currency": "INR",
                "status": "OPEN",
                "payment_method": "CREDIT_CARD",
                "failure_reason": "EXPIRED_CARD",
                "days_overdue": 0,
                "days_ago": 3
            },
            # 6. Guardrail Block Event (Opted out customer)
            {
                "id": "EVT-2006",
                "merchant_id": "MERCH-1002",
                "customer_id": "CUST-1003",
                "event_type": "SUBSCRIPTION_FAILURE",
                "amount": Decimal("1999.00"),
                "currency": "INR",
                "status": "STOPPED",
                "payment_method": "UPI",
                "failure_reason": "AUTO_DEBIT_FAILED",
                "days_overdue": 0,
                "days_ago": 5
            }
        ]

        for s in scenarios:
            evt = RevenueEvent(
                id=s["id"],
                merchant_id=s["merchant_id"],
                customer_id=s["customer_id"],
                event_type=s["event_type"],
                amount=s["amount"],
                currency=s["currency"],
                status=s["status"],
                payment_method=s["payment_method"],
                failure_reason=s["failure_reason"],
                event_timestamp=datetime.utcnow() - timedelta(days=s["days_ago"]),
                days_overdue=s["days_overdue"],
                created_at=datetime.utcnow() - timedelta(days=s["days_ago"])
            )
            db.add(evt)
            revenue_events.append(evt)

        # Generate Remaining Events (EVT-2007 to EVT-2400)
        event_types = ["PAYMENT_FAILURE", "CHECKOUT_ABANDONMENT", "SUBSCRIPTION_FAILURE", "OVERDUE_INVOICE"]
        payment_methods = ["UPI", "CREDIT_CARD", "NETBANKING", "DEBIT_CARD", "INVOICE"]
        common_amounts = [Decimal("499.00"), Decimal("999.00"), Decimal("1999.00"), Decimal("4999.00"), Decimal("12500.00"), Decimal("50000.00")]

        for i in range(7, NUM_EVENTS + 1):
            evt_id = f"EVT-{2000 + i}"
            cust = random.choice(customers)
            e_type = random.choice(event_types)
            amt = random.choice(common_amounts)
            days_ago = random.randint(1, 30)
            
            days_overdue = 0
            if e_type == "OVERDUE_INVOICE":
                days_overdue = random.randint(15, 60)
            
            f_reason = "PAYMENT_GATEWAY_TIMEOUT"
            if e_type == "PAYMENT_FAILURE":
                f_reason = random.choice(["BANK_DECLINE", "INSUFFICIENT_FUNDS", "AUTHENTICATION_FAILED", "EXPIRED_CARD"])
            elif e_type == "CHECKOUT_ABANDONMENT":
                f_reason = random.choice(["CART_INACTIVITY", "REPEATED_VISIT_NO_PAYMENT", "HIGH_CART_VALUE"])
            elif e_type == "SUBSCRIPTION_FAILURE":
                f_reason = random.choice(["AUTO_DEBIT_DECLINE", "EXPIRED_CARD", "INSUFFICIENT_FUNDS"])
            elif e_type == "OVERDUE_INVOICE":
                f_reason = f"OVERDUE_PAYMENT_{days_overdue}D"

            evt = RevenueEvent(
                id=evt_id,
                merchant_id=cust.merchant_id,
                customer_id=cust.id,
                event_type=e_type,
                amount=amt,
                currency="INR",
                status=random.choice(["OPEN", "OPEN", "IN_RECOVERY", "RECOVERED", "FAILED", "STOPPED"]),
                payment_method=random.choice(payment_methods),
                failure_reason=f_reason,
                event_timestamp=datetime.utcnow() - timedelta(days=days_ago),
                days_overdue=days_overdue,
                created_at=datetime.utcnow() - timedelta(days=days_ago)
            )
            db.add(evt)
            revenue_events.append(evt)

        db.commit()

        # 4. Generate Recovery Attempts, Outcomes, and Audit Logs
        print("Generating recovery attempts, outcomes, and audit logs...")
        attempts_count = 0
        outcomes_count = 0
        audit_count = 0

        action_types = [
            "RETRY_PAYMENT", "SEND_PAYMENT_LINK", "SEND_REMINDER", 
            "OFFER_APPROVED_INCENTIVE", "ESCALATE_TO_HUMAN", "NO_ACTION"
        ]

        # Explicit Scenario Attempts & Outcomes
        # Attempt 1 for EVT-2002 (Low Recoverability Failure Case)
        att_low = RecoveryAttempt(
            id="ATT-3001",
            revenue_event_id="EVT-2002",
            action_type="SEND_PAYMENT_LINK",
            attempt_number=1,
            status="FAILED",
            attempted_at=datetime.utcnow() - timedelta(days=10)
        )
        out_low = RecoveryOutcome(
            id="OUT-4001",
            recovery_attempt_id="ATT-3001",
            outcome="FAILED",
            recovered_amount=Decimal("0.00"),
            outcome_timestamp=datetime.utcnow() - timedelta(days=10)
        )
        aud_low = AuditLog(
            id="AUD-5001",
            revenue_event_id="EVT-2002",
            action="SEND_PAYMENT_LINK",
            reason="Low initial recoverability score. Payment link sent but expired.",
            guardrail_result="PASSED",
            timestamp=datetime.utcnow() - timedelta(days=10)
        )
        db.add_all([att_low, out_low, aud_low])
        attempts_count += 1
        outcomes_count += 1
        audit_count += 1

        # Guardrail Block Audit for EVT-2006 (Opted out customer)
        aud_guard = AuditLog(
            id="AUD-5002",
            revenue_event_id="EVT-2006",
            action="NO_ACTION",
            reason="Recovery attempt blocked because customer is explicitly opted out of communications.",
            guardrail_result="BLOCKED_CUSTOMER_OPT_OUT",
            timestamp=datetime.utcnow() - timedelta(days=5)
        )
        db.add(aud_guard)
        audit_count += 1

        # Generate additional attempts for non-OPEN events
        attempt_id_counter = 3002
        outcome_id_counter = 4002
        audit_id_counter = 5003

        for evt in revenue_events:
            if evt.status in ["IN_RECOVERY", "RECOVERED", "FAILED"]:
                num_attempts = random.randint(1, 2)
                for att_num in range(1, num_attempts + 1):
                    act = random.choice(["SEND_PAYMENT_LINK", "SEND_REMINDER", "RETRY_PAYMENT"])
                    att_status = "SUCCESS" if (evt.status == "RECOVERED" and att_num == num_attempts) else "FAILED"
                    
                    att = RecoveryAttempt(
                        id=f"ATT-{attempt_id_counter}",
                        revenue_event_id=evt.id,
                        action_type=act,
                        attempt_number=att_num,
                        status=att_status,
                        attempted_at=evt.event_timestamp + timedelta(hours=att_num * 12)
                    )
                    db.add(att)
                    attempts_count += 1

                    if att_status in ["SUCCESS", "FAILED"]:
                        rec_amt = evt.amount if att_status == "SUCCESS" else Decimal("0.00")
                        out_val = "RECOVERED" if att_status == "SUCCESS" else "FAILED"
                        
                        out = RecoveryOutcome(
                            id=f"OUT-{outcome_id_counter}",
                            recovery_attempt_id=f"ATT-{attempt_id_counter}",
                            outcome=out_val,
                            recovered_amount=rec_amt,
                            outcome_timestamp=att.attempted_at + timedelta(hours=2)
                        )
                        db.add(out)
                        outcomes_count += 1
                        outcome_id_counter += 1

                    aud = AuditLog(
                        id=f"AUD-{audit_id_counter}",
                        revenue_event_id=evt.id,
                        action=act,
                        reason=f"System executed {act} based on failure reason ({evt.failure_reason}).",
                        guardrail_result="PASSED",
                        timestamp=att.attempted_at
                    )
                    db.add(aud)
                    audit_count += 1
                    audit_id_counter += 1

                    attempt_id_counter += 1

        db.commit()

        # Summary Statistics Output
        print("\n==================================================")
        print("Database seeded successfully!")
        print("--------------------------------------------------")
        print(f"Merchants:          {db.query(Merchant).count()}")
        print(f"Merchant Policies:  {db.query(MerchantPolicy).count()}")
        print(f"Customers:          {db.query(Customer).count()}")
        print(f"Revenue Events:     {db.query(RevenueEvent).count()}")
        print(f"Recovery Attempts:  {db.query(RecoveryAttempt).count()}")
        print(f"Recovery Outcomes:  {db.query(RecoveryOutcome).count()}")
        print(f"Audit Logs:         {db.query(AuditLog).count()}")
        print("==================================================\n")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    generate_seed_data()
