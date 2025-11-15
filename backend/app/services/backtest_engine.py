"""
백테스트 실행 엔진
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Trade:
    """거래 기록"""
    timestamp: datetime
    action: str  # 'buy' or 'sell'
    price: float
    quantity: float
    balance: float
    position: float


@dataclass
class BacktestResult:
    """백테스트 결과"""
    trades: List[Trade]
    equity_curve: List[float]
    metrics: Dict[str, Any]
    initial_capital: float
    final_capital: float


class BacktestEngine:
    """백테스트 실행 엔진"""

    def __init__(
        self,
        strategy_code: str,
        parameters: dict,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1% 수수료
    ):
        self.strategy_code = strategy_code
        self.parameters = parameters
        self.initial_capital = initial_capital
        self.commission = commission

    def execute(self, market_data: pd.DataFrame) -> BacktestResult:
        """백테스트 실행"""

        # 전략 실행하여 신호 생성
        signals = self._execute_strategy(market_data)

        # 매매 시뮬레이션
        trades, equity_curve = self._simulate_trading(market_data, signals)

        # 성과 지표 계산
        metrics = self._calculate_metrics(trades, equity_curve)

        final_capital = equity_curve[-1] if equity_curve else self.initial_capital

        return BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            metrics=metrics,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
        )

    def _execute_strategy(self, data: pd.DataFrame) -> List[str]:
        """전략 코드를 실행하여 매매 신호 생성"""

        # 안전한 실행 환경 설정
        safe_globals = {
            'pd': pd,
            'np': np,
            '__builtins__': {
                'range': range,
                'len': len,
                'print': print,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
            }
        }

        # 전략 코드 실행
        try:
            exec(self.strategy_code, safe_globals)
            strategy_func = safe_globals.get('strategy')

            if not strategy_func:
                raise ValueError("Strategy function not found")

            signals = strategy_func(data)
            return signals

        except Exception as e:
            print(f"Strategy execution error: {e}")
            # 에러 발생 시 모든 신호를 'hold'로 설정
            return ['hold'] * len(data)

    def _simulate_trading(
        self, market_data: pd.DataFrame, signals: List[str]
    ) -> tuple[List[Trade], List[float]]:
        """매매 시뮬레이션"""

        trades = []
        equity_curve = []

        balance = self.initial_capital  # 현금
        position = 0.0  # 보유 주식 수

        for i in range(len(market_data)):
            price = market_data['close'].iloc[i]
            signal = signals[i] if i < len(signals) else 'hold'

            # 매수 신호
            if signal == 'buy' and balance > 0:
                # 사용 가능한 현금으로 최대한 매수
                cost = balance * 0.95  # 95% 사용 (안전 마진)
                quantity = cost / (price * (1 + self.commission))

                position += quantity
                balance -= cost

                trades.append(Trade(
                    timestamp=market_data.index[i],
                    action='buy',
                    price=price,
                    quantity=quantity,
                    balance=balance,
                    position=position,
                ))

            # 매도 신호
            elif signal == 'sell' and position > 0:
                # 보유 주식 전량 매도
                proceeds = position * price * (1 - self.commission)
                balance += proceeds

                trades.append(Trade(
                    timestamp=market_data.index[i],
                    action='sell',
                    price=price,
                    quantity=position,
                    balance=balance,
                    position=0,
                ))

                position = 0

            # 포트폴리오 가치 기록
            portfolio_value = balance + (position * price)
            equity_curve.append(portfolio_value)

        return trades, equity_curve

    def _calculate_metrics(
        self, trades: List[Trade], equity_curve: List[float]
    ) -> Dict[str, Any]:
        """성과 지표 계산"""

        if not equity_curve:
            return {}

        # 수익률 계산
        total_return = (
            (equity_curve[-1] - self.initial_capital) / self.initial_capital * 100
        )

        # 최대 낙폭 (Maximum Drawdown)
        peak = equity_curve[0]
        max_drawdown = 0.0

        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # 거래 통계
        buy_trades = [t for t in trades if t.action == 'buy']
        sell_trades = [t for t in trades if t.action == 'sell']

        total_trades = len(buy_trades)

        # 승률 계산 (매수-매도 쌍)
        winning_trades = 0
        if len(buy_trades) > 0 and len(sell_trades) > 0:
            for i in range(min(len(buy_trades), len(sell_trades))):
                if sell_trades[i].price > buy_trades[i].price:
                    winning_trades += 1

        win_rate = (
            (winning_trades / total_trades * 100)
            if total_trades > 0
            else 0
        )

        # 샤프 비율 (간단한 버전)
        if len(equity_curve) > 1:
            returns = np.diff(equity_curve) / equity_curve[:-1]
            sharpe_ratio = (
                (np.mean(returns) / np.std(returns)) * np.sqrt(252)
                if np.std(returns) > 0
                else 0
            )
        else:
            sharpe_ratio = 0

        return {
            'total_return': round(total_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'final_value': round(equity_curve[-1], 2),
        }
