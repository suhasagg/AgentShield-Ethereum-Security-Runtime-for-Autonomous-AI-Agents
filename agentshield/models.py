from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, JSON

class Base(DeclarativeBase): pass

class DecisionRecord(Base):
    __tablename__ = "decision_records"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    tx_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    intent_hash: Mapped[str] = mapped_column(String)
    delegation_root: Mapped[str] = mapped_column(String)
    provenance_root: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(String)
    risk_score: Mapped[int] = mapped_column(Integer)
    reasons: Mapped[list] = mapped_column(JSON)
    policy_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
