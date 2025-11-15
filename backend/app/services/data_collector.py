"""
시장 데이터 수집 서비스
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional


class DataCollector:
    """시장 데이터 수집기"""

    def __init__(self):
        pass

    async def fetch_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """주식 데이터 수집 (Yahoo Finance)"""

        try:
            # yfinance를 사용하여 데이터 다운로드
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")

            # 컬럼명을 소문자로 변경
            data.columns = data.columns.str.lower()

            # 필요한 컬럼만 선택 (OHLCV)
            data = data[['open', 'high', 'low', 'close', 'volume']]

            return data

        except Exception as e:
            print(f"Error fetching stock data: {e}")
            raise

    async def fetch_crypto_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """암호화폐 데이터 수집"""

        try:
            # 암호화폐는 Yahoo Finance에서도 가능
            # 예: BTC-USD, ETH-USD
            if not symbol.endswith('-USD'):
                symbol = f"{symbol}-USD"

            return await self.fetch_stock_data(symbol, start_date, end_date, interval)

        except Exception as e:
            print(f"Error fetching crypto data: {e}")
            raise

    def get_available_symbols(self, asset_type: str = "stock") -> list:
        """사용 가능한 심볼 목록"""

        if asset_type == "stock":
            # 주요 한국 주식
            return [
                {"symbol": "005930.KS", "name": "삼성전자", "exchange": "KRX"},
                {"symbol": "000660.KS", "name": "SK하이닉스", "exchange": "KRX"},
                {"symbol": "035420.KS", "name": "NAVER", "exchange": "KRX"},
                {"symbol": "035720.KS", "name": "카카오", "exchange": "KRX"},
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "exchange": "NASDAQ"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
            ]
        elif asset_type == "crypto":
            # 주요 암호화폐
            return [
                {"symbol": "BTC-USD", "name": "Bitcoin", "exchange": "Crypto"},
                {"symbol": "ETH-USD", "name": "Ethereum", "exchange": "Crypto"},
                {"symbol": "BNB-USD", "name": "Binance Coin", "exchange": "Crypto"},
                {"symbol": "XRP-USD", "name": "Ripple", "exchange": "Crypto"},
                {"symbol": "ADA-USD", "name": "Cardano", "exchange": "Crypto"},
                {"symbol": "SOL-USD", "name": "Solana", "exchange": "Crypto"},
            ]
        else:
            return []

    async def save_to_database(self, supabase, symbol: str, data: pd.DataFrame):
        """Supabase bt_market_data 테이블에 저장"""

        try:
            # DataFrame을 레코드 리스트로 변환
            records = []
            for timestamp, row in data.iterrows():
                records.append({
                    "symbol": symbol,
                    "timestamp": timestamp.isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume']),
                })

            # Supabase에 배치 삽입
            # 중복 데이터 방지를 위해 upsert 사용
            response = supabase.table("bt_market_data").upsert(records).execute()

            return len(records)

        except Exception as e:
            print(f"Error saving to database: {e}")
            raise
