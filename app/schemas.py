from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    sender_mobile: str
    receiver_mobile: str

class PaymentResponse(BaseModel):
    payment_id: int
    payment_uid: str
    status: str

class PaymentStatusUpdate(BaseModel):
    status: str  # "SUCCESS" or "FAILED"