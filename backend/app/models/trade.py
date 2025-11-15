"""
Trade Model
"""

from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class BacktestTrade(Base):
    """백테스트 거래 기록 모델"""

    __tablename__ = "bt_backtest_trades"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    backtest_id = Column(UUID(as_uuid=True), ForeignKey("bt_backtests.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    trade_type = Column(String(10), nullable=False)  # 'buy' or 'sell'
    price = Column(DECIMAL(20, 8), nullable=False)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    commission = Column(DECIMAL(20, 8), default=0)
    portfolio_value = Column(DECIMAL(20, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    backtest = relationship("Backtest", backref="trades")

    def __repr__(self):
        return f"<BacktestTrade(id={self.id}, type={self.trade_type}, price={self.price})>"
