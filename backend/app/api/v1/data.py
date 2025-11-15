"""
Data API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends
from supabase import Client
from app.supabase_client import get_supabase

router = APIRouter()


@router.get("/symbols")
async def get_symbols(supabase: Client = Depends(get_supabase)):
    """심볼 목록 조회"""
    return {"message": "Get symbols - To be implemented"}


@router.get("/historical")
async def get_historical_data(supabase: Client = Depends(get_supabase)):
    """과거 데이터 조회"""
    return {"message": "Get historical data - To be implemented"}


@router.post("/import")
async def import_data(supabase: Client = Depends(get_supabase)):
    """데이터 가져오기"""
    return {"message": "Import data - To be implemented"}
