from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    customer_id = Column(String, primary_key=True)
    account_age_days = Column(Integer)
    transaction_volume_30d = Column(Float)
    international_tx_count = Column(Integer)
    high_risk_jurisdiction_flag = Column(Boolean)
    pep_status = Column(Boolean)
    cash_intensive_business_flag = Column(Boolean)
    avg_tx_size = Column(Float)
    velocity_1h = Column(Integer)
    velocity_24h = Column(Integer)
    structured_tx_flag = Column(Boolean)
    crypto_exchange_tx_count = Column(Integer)

class HistoricalCase(Base):
    __tablename__ = 'historical_cases'

    case_id = Column(String, primary_key=True)
    customer_id = Column(String)
    risk_score = Column(Float)
    resolution = Column(String)
    case_summary = Column(String)
    vector_embedding = Column(Vector(12)) # 12 dimensional vector based on features
