"""
Backtest Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class BacktestBase(BaseModel):
    """백테스트 기본 스키마"""
    strategy_id: UUID = Field(..., description="전략 ID")
    symbol: str = Field(..., max_length=50, description="거래 심볼")
    start_date: date = Field(..., description="백테스트 시작일")
    end_date: date = Field(..., description="백테스트 종료일")
    initial_capital: Decimal = Field(10000.00, description="초기 자본")


class BacktestCreate(BacktestBase):
    """백테스트 생성 스키마"""
    pass


class BacktestResponse(BacktestBase):
    """백테스트 응답 스키마"""
    id: UUID
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BacktestListResponse(BaseModel):
    """백테스트 목록 응답 스키마"""
    backtests: list[BacktestResponse]
    total: int


class BacktestStatusResponse(BaseModel):
    """백테스트 상태 응답 스키마"""
    id: UUID
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
