from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .database import SessionLocal
from .models import Payment
from .schemas import PaymentRequest, PaymentResponse, PaymentStatusUpdate

router = APIRouter()

# ----------------------
# Database session
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# API Key Authentication
# ----------------------
load_dotenv() 
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY not set in environment")


def verify_api_key(api_key: Optional[str] = Header(None, alias="api_key")):
    print("Received API key:", api_key)
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# ----------------------
# Payments POST endpoint
# ----------------------
@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)  # <-- API key check
):
    # Extract last 4 digits from sender and receiver
    sender_last4 = payment.sender_mobile[-4:]
    receiver_last4 = payment.receiver_mobile[-4:]

    # Timestamp for UID
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    # Random 4-character part for uniqueness
    random_part = uuid.uuid4().hex[:4].upper()

    # Construct payment UID
    payment_uid = f"PAY_{sender_last4}_{receiver_last4}_{timestamp}_{random_part}"

    # Create payment record
    new_payment = Payment(
        payment_uid=payment_uid,   
        amount=payment.amount,
        currency=payment.currency,
        sender_mobile=payment.sender_mobile,
        receiver_mobile=payment.receiver_mobile,
        status="PENDING"
    )

    # Insert into DB
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Return response
    return {
        "payment_id": new_payment.id,
        "payment_uid": new_payment.payment_uid,  
        "status": new_payment.status
    }

@router.get("/payments/{payment_uid}", response_model=PaymentResponse)
def get_payment_by_uid(
    payment_uid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    payment = db.query(Payment).filter(
        Payment.payment_uid == payment_uid
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "payment_id": payment.id,
        "payment_uid": payment.payment_uid,
        "status": payment.status
    }


@router.put("/payments/{payment_uid}", response_model=PaymentResponse)
def update_payment_status(
    payment_uid: str,
    status_update: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    payment = db.query(Payment).filter(Payment.payment_uid == payment_uid).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if status_update.status not in ["SUCCESS", "FAILED"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    payment.status = status_update.status
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "payment_uid": payment.payment_uid,
        "status": payment.status
    }

