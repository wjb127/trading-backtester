"""
Backtests API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends
from supabase import Client
from app.supabase_client import get_supabase

router = APIRouter()


@router.get("")
async def get_backtests(supabase: Client = Depends(get_supabase)):
    """백테스팅 목록 조회"""
    return {"message": "Get backtests - To be implemented"}


@router.post("")
async def create_backtest(supabase: Client = Depends(get_supabase)):
    """백테스팅 시작"""
    return {"message": "Create backtest - To be implemented"}


@router.get("/{backtest_id}")
async def get_backtest(backtest_id: str, supabase: Client = Depends(get_supabase)):
    """백테스팅 결과 조회"""
    return {"message": f"Get backtest {backtest_id} - To be implemented"}


@router.get("/{backtest_id}/status")
async def get_backtest_status(backtest_id: str, supabase: Client = Depends(get_supabase)):
    """백테스팅 진행 상태 조회"""
    return {"message": f"Get backtest status {backtest_id} - To be implemented"}


@router.delete("/{backtest_id}")
async def delete_backtest(backtest_id: str, supabase: Client = Depends(get_supabase)):
    """백테스팅 삭제"""
    return {"message": f"Delete backtest {backtest_id} - To be implemented"}
