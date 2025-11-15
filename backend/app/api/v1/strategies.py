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


@router.post("/{strategy_id}/optimize")
async def optimize_strategy(
    strategy_id: UUID,
    symbol: str,
    start_date: str,
    end_date: str,
    method: str = "grid",  # "grid", "bayesian", "random"
    param_grid: dict = None,
    n_iter: int = 50,
    supabase: Client = Depends(get_supabase)
):
    """전략 파라미터 최적화"""
    from app.services.optimizer import StrategyOptimizer
    from app.services.data_collector import DataCollector

    try:
        # 전략 조회
        strategy_response = supabase.table("bt_strategies")\
            .select("*")\
            .eq("id", str(strategy_id))\
            .execute()

        if not strategy_response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy {strategy_id} not found"
            )

        strategy = strategy_response.data[0]

        # 시장 데이터 조회
        data_collector = DataCollector()
        market_data = await data_collector.fetch_stock_data(
            symbol, start_date, end_date
        )

        # 최적화 실행
        optimizer = StrategyOptimizer(
            strategy_code=strategy['code'],
            market_data=market_data
        )

        if method == "grid":
            if not param_grid:
                # 기본 그리드 (이동평균 전략 예시)
                param_grid = {
                    "short_period": [10, 20, 30],
                    "long_period": [40, 50, 60]
                }
            result = optimizer.grid_search(param_grid)

        elif method == "bayesian":
            if not param_grid:
                # 기본 범위
                param_grid = {
                    "short_period": (5, 30),
                    "long_period": (30, 100)
                }
            result = optimizer.bayesian_optimization(param_grid, n_calls=n_iter)

        elif method == "random":
            if not param_grid:
                param_grid = {
                    "short_period": (5, 30),
                    "long_period": (30, 100)
                }
            result = optimizer.random_search(param_grid, n_iter=n_iter)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown optimization method: {method}"
            )

        return {
            "success": True,
            "optimization_result": result,
            "strategy_id": str(strategy_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
