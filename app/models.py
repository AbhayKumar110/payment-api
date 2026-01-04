from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_uid = Column(String, unique=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    sender_mobile = Column(String, nullable=False)
    receiver_mobile = Column(String, nullable=False)
    status = Column(String, default="PENDING")
