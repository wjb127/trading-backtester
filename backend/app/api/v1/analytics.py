"""
Analytics API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.supabase_client import get_supabase
from uuid import UUID
from typing import List
import pandas as pd


router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    backtest_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """성과 지표 조회"""
    try:
        response = supabase.table("bt_backtests")\
            .select("result")\
            .eq("id", str(backtest_id))\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Backtest not found")

        return response.data[0].get("result", {})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart")
async def get_chart_data(
    backtest_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """차트 데이터 조회 (수익 곡선, 거래 표시)"""
    try:
        # 백테스트 정보
        backtest_response = supabase.table("bt_backtests")\
            .select("*")\
            .eq("id", str(backtest_id))\
            .execute()

        if not backtest_response.data:
            raise HTTPException(status_code=404, detail="Backtest not found")

        backtest = backtest_response.data[0]

        # 거래 기록
        trades_response = supabase.table("bt_backtest_trades")\
            .select("*")\
            .eq("backtest_id", str(backtest_id))\
            .order("timestamp")\
            .execute()

        trades = trades_response.data or []

        # 수익 곡선 데이터 생성
        # portfolio_value 필드 사용
        equity_curve = []
        for trade in trades:
            equity_curve.append({
                "timestamp": trade["timestamp"],
                "value": trade.get("portfolio_value", 0)
            })

        # 시장 데이터
        market_response = supabase.table("bt_market_data")\
            .select("*")\
            .eq("symbol", backtest["symbol"])\
            .gte("timestamp", backtest["start_date"])\
            .lte("timestamp", backtest["end_date"])\
            .order("timestamp")\
            .execute()

        market_data = market_response.data or []

        result = backtest.get("result", {}) or {}
        return {
            "equity_curve": equity_curve,
            "trades": trades,
            "market_data": market_data,
            "initial_capital": backtest["initial_capital"],
            "final_capital": result.get("final_capital", backtest["initial_capital"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_strategies(
    backtest_ids: str,  # 콤마로 구분된 ID 리스트
    supabase: Client = Depends(get_supabase)
):
    """전략 비교"""
    try:
        ids = backtest_ids.split(',')

        comparisons = []
        for backtest_id in ids:
            response = supabase.table("bt_backtests")\
                .select("*, bt_strategies(name)")\
                .eq("id", backtest_id.strip())\
                .execute()

            if response.data:
                backtest = response.data[0]
                result = backtest.get("result", {}) or {}
                comparisons.append({
                    "backtest_id": backtest["id"],
                    "strategy_name": backtest.get("bt_strategies", {}).get("name", "Unknown"),
                    "symbol": backtest["symbol"],
                    "total_return": result.get("total_return", 0),
                    "max_drawdown": result.get("max_drawdown", 0),
                    "sharpe_ratio": result.get("sharpe_ratio", 0),
                    "total_trades": result.get("total_trades", 0),
                    "win_rate": result.get("win_rate", 0),
                })

        return {"comparisons": comparisons}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
