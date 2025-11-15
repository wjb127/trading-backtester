"""
Strategy Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class StrategyBase(BaseModel):
    """전략 기본 스키마"""
    name: str = Field(..., max_length=255, description="전략 이름")
    description: Optional[str] = Field(None, description="전략 설명")
    code: str = Field(..., description="전략 코드 (Python)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="전략 파라미터")
    is_active: bool = Field(True, description="활성화 여부")


class StrategyCreate(StrategyBase):
    """전략 생성 스키마"""
    pass


class StrategyUpdate(BaseModel):
    """전략 수정 스키마"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """전략 응답 스키마"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    """전략 목록 응답 스키마"""
    strategies: list[StrategyResponse]
    total: int
