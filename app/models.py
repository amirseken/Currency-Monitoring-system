from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base
from datetime import datetime

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String, index=True)
    target_currency = Column(String, index=True)
    rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Rate(Base):
    __tablename__ = "rates"
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String)
    target_currency = Column(String)
    rate = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Difference(Base):
    __tablename__ = "differences"
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String)
    target_currency = Column(String)
    rate_api = Column(Float)
    rate_site = Column(Float)
    diff_percent = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
