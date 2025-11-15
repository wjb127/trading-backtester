"""
Analytics API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends
from supabase import Client
from app.supabase_client import get_supabase

router = APIRouter()


@router.get("/metrics")
async def get_metrics(supabase: Client = Depends(get_supabase)):
    """성과 지표 조회"""
    return {"message": "Get metrics - To be implemented"}


@router.get("/chart")
async def get_chart_data(supabase: Client = Depends(get_supabase)):
    """차트 데이터 조회"""
    return {"message": "Get chart data - To be implemented"}


@router.get("/compare")
async def compare_strategies(supabase: Client = Depends(get_supabase)):
    """전략 비교"""
    return {"message": "Compare strategies - To be implemented"}
