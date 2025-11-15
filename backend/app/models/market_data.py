"""
Market Data Model
"""

from sqlalchemy import Column, String, DateTime, DECIMAL, BigInteger, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class MarketData(Base):
    """시장 데이터 모델"""

    __tablename__ = "bt_market_data"
    __table_args__ = (
        UniqueConstraint('symbol', 'timestamp', name='bt_market_data_unique'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open = Column(DECIMAL(20, 8), nullable=False)
    high = Column(DECIMAL(20, 8), nullable=False)
    low = Column(DECIMAL(20, 8), nullable=False)
    close = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(30, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MarketData(symbol={self.symbol}, timestamp={self.timestamp}, close={self.close})>"
