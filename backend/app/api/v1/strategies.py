"""
Strategies API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from app.supabase_client import get_supabase
from supabase import Client
from app.schemas import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse,
)

router = APIRouter()


@router.get("", response_model=StrategyListResponse)
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    supabase: Client = Depends(get_supabase)
):
    """전략 목록 조회"""
    # 전략 목록 조회
    response = supabase.table("bt_strategies")\
        .select("*", count="exact")\
        .order("created_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()

    total = response.count if response.count else 0
    strategies = response.data if response.data else []

    return StrategyListResponse(
        strategies=strategies,
        total=total
    )


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    supabase: Client = Depends(get_supabase)
):
    """전략 생성"""
    response = supabase.table("bt_strategies")\
        .insert(strategy_data.model_dump())\
        .execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy"
        )

    return response.data[0]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """전략 상세 조회"""
    response = supabase.table("bt_strategies")\
        .select("*")\
        .eq("id", str(strategy_id))\
        .execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )

    return response.data[0]


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    supabase: Client = Depends(get_supabase)
):
    """전략 수정"""
    # 업데이트할 필드만 추출
    update_data = strategy_data.model_dump(exclude_unset=True)

    response = supabase.table("bt_strategies")\
        .update(update_data)\
        .eq("id", str(strategy_id))\
        .execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )

    return response.data[0]


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """전략 삭제"""
    response = supabase.table("bt_strategies")\
        .delete()\
        .eq("id", str(strategy_id))\
        .execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )

    return None
