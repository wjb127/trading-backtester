"""
Backtests API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.supabase_client import get_supabase
from app.services.backtest_engine import BacktestEngine
from app.services.data_collector import DataCollector
from pydantic import BaseModel
from uuid import UUID
import pandas as pd
from datetime import datetime


class BacktestCreate(BaseModel):
    strategy_id: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    commission: float = 0.001


router = APIRouter()
data_collector = DataCollector()


@router.get("")
async def get_backtests(
    skip: int = 0,
    limit: int = 100,
    supabase: Client = Depends(get_supabase)
):
    """백테스팅 목록 조회"""
    try:
        response = supabase.table("bt_backtests")\
            .select("*", count="exact")\
            .order("created_at", desc=True)\
            .range(skip, skip + limit - 1)\
            .execute()

        return {
            "backtests": response.data,
            "total": response.count or 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_backtest(
    backtest_data: BacktestCreate,
    supabase: Client = Depends(get_supabase)
):
    """백테스팅 시작"""
    try:
        # 1. 전략 조회
        strategy_response = supabase.table("bt_strategies")\
            .select("*")\
            .eq("id", backtest_data.strategy_id)\
            .execute()

        if not strategy_response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy {backtest_data.strategy_id} not found"
            )

        strategy = strategy_response.data[0]

        # 2. 시장 데이터 조회 (DB에서)
        data_response = supabase.table("bt_market_data")\
            .select("*")\
            .eq("symbol", backtest_data.symbol)\
            .gte("timestamp", backtest_data.start_date)\
            .lte("timestamp", backtest_data.end_date)\
            .order("timestamp")\
            .execute()

        if not data_response.data:
            # DB에 데이터가 없으면 자동으로 수집
            market_data = await data_collector.fetch_stock_data(
                backtest_data.symbol,
                backtest_data.start_date,
                backtest_data.end_date
            )

            # DB에 저장
            await data_collector.save_to_database(
                supabase,
                backtest_data.symbol,
                market_data
            )
        else:
            # DB 데이터를 DataFrame으로 변환
            market_data = pd.DataFrame(data_response.data)
            market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
            market_data = market_data.set_index('timestamp')
            market_data = market_data[['open', 'high', 'low', 'close', 'volume']]

        # 3. 백테스트 실행
        engine = BacktestEngine(
            strategy_code=strategy['code'],
            parameters=strategy['parameters'],
            initial_capital=backtest_data.initial_capital,
            commission=backtest_data.commission
        )

        result = engine.execute(market_data)

        # 4. 백테스트 결과 저장
        backtest_record = {
            "strategy_id": backtest_data.strategy_id,
            "symbol": backtest_data.symbol,
            "start_date": backtest_data.start_date,
            "end_date": backtest_data.end_date,
            "initial_capital": backtest_data.initial_capital,
            "final_capital": result.final_capital,
            "total_return": result.metrics.get('total_return', 0),
            "max_drawdown": result.metrics.get('max_drawdown', 0),
            "sharpe_ratio": result.metrics.get('sharpe_ratio', 0),
            "total_trades": result.metrics.get('total_trades', 0),
            "win_rate": result.metrics.get('win_rate', 0),
            "status": "completed",
            "metrics": result.metrics,
        }

        backtest_response = supabase.table("bt_backtests")\
            .insert(backtest_record)\
            .execute()

        if not backtest_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to save backtest"
            )

        backtest_id = backtest_response.data[0]['id']

        # 5. 거래 기록 저장
        if result.trades:
            trade_records = []
            for trade in result.trades:
                trade_records.append({
                    "backtest_id": backtest_id,
                    "timestamp": trade.timestamp.isoformat(),
                    "action": trade.action,
                    "price": trade.price,
                    "quantity": trade.quantity,
                    "balance": trade.balance,
                    "position": trade.position,
                })

            supabase.table("bt_backtest_trades")\
                .insert(trade_records)\
                .execute()

        return {
            "backtest_id": backtest_id,
            "status": "completed",
            "metrics": result.metrics,
            "trades_count": len(result.trades)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{backtest_id}")
async def get_backtest(
    backtest_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """백테스팅 결과 조회"""
    try:
        # 백테스트 정보 조회
        backtest_response = supabase.table("bt_backtests")\
            .select("*")\
            .eq("id", str(backtest_id))\
            .execute()

        if not backtest_response.data:
            raise HTTPException(status_code=404, detail="Backtest not found")

        # 거래 기록 조회
        trades_response = supabase.table("bt_backtest_trades")\
            .select("*")\
            .eq("backtest_id", str(backtest_id))\
            .order("timestamp")\
            .execute()

        return {
            "backtest": backtest_response.data[0],
            "trades": trades_response.data or []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{backtest_id}/status")
async def get_backtest_status(
    backtest_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """백테스팅 진행 상태 조회"""
    try:
        response = supabase.table("bt_backtests")\
            .select("status, metrics")\
            .eq("id", str(backtest_id))\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Backtest not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(
    backtest_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """백테스팅 삭제"""
    try:
        # 거래 기록 삭제
        supabase.table("bt_backtest_trades")\
            .delete()\
            .eq("backtest_id", str(backtest_id))\
            .execute()

        # 백테스트 삭제
        response = supabase.table("bt_backtests")\
            .delete()\
            .eq("id", str(backtest_id))\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Backtest not found")

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
