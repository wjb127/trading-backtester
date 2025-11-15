"""
Backtest Model
"""

from sqlalchemy import Column, String, Date, DateTime, DECIMAL, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Backtest(Base):
    """백테스트 모델"""

    __tablename__ = "bt_backtests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("bt_strategies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(DECIMAL(20, 2), nullable=False, default=10000.00)
    status = Column(String(20), nullable=False, default="pending")
    result = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    strategy = relationship("Strategy", backref="backtests")

    def __repr__(self):
        return f"<Backtest(id={self.id}, symbol={self.symbol}, status={self.status})>"
