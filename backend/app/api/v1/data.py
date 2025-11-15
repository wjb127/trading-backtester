"""
Data API Routes - Supabase REST API
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.supabase_client import get_supabase
from app.services.data_collector import DataCollector
from pydantic import BaseModel


class DataImportRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    interval: str = "1d"
    asset_type: str = "stock"  # "stock" or "crypto"


router = APIRouter()
data_collector = DataCollector()


@router.get("/symbols")
async def get_symbols(asset_type: str = "stock"):
    """심볼 목록 조회"""
    symbols = data_collector.get_available_symbols(asset_type)
    return {"symbols": symbols}


@router.get("/historical")
async def get_historical_data(
    symbol: str,
    start_date: str,
    end_date: str,
    supabase: Client = Depends(get_supabase)
):
    """과거 데이터 조회 (DB에서)"""
    try:
        response = supabase.table("bt_market_data")\
            .select("*")\
            .eq("symbol", symbol)\
            .gte("timestamp", start_date)\
            .lte("timestamp", end_date)\
            .order("timestamp")\
            .execute()

        return {"data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_data(
    request: DataImportRequest,
    supabase: Client = Depends(get_supabase)
):
    """데이터 가져오기 (Yahoo Finance -> DB)"""
    try:
        # 데이터 수집
        if request.asset_type == "crypto":
            data = await data_collector.fetch_crypto_data(
                request.symbol,
                request.start_date,
                request.end_date,
                request.interval
            )
        else:
            data = await data_collector.fetch_stock_data(
                request.symbol,
                request.start_date,
                request.end_date,
                request.interval
            )

        # DB에 저장
        records_count = await data_collector.save_to_database(
            supabase,
            request.symbol,
            data
        )

        return {
            "success": True,
            "records_imported": records_count,
            "symbol": request.symbol
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
