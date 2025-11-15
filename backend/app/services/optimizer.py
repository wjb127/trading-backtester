"""
전략 파라미터 최적화 서비스
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from app.services.backtest_engine import BacktestEngine
import itertools


class StrategyOptimizer:
    """전략 파라미터 최적화기"""

    def __init__(
        self,
        strategy_code: str,
        market_data: pd.DataFrame,
        initial_capital: float = 10000.0
    ):
        self.strategy_code = strategy_code
        self.market_data = market_data
        self.initial_capital = initial_capital
        self.optimization_results = []

    def grid_search(
        self,
        param_grid: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """
        그리드 서치 최적화

        Args:
            param_grid: 파라미터 그리드
                예: {"short_period": [10, 20, 30], "long_period": [40, 50, 60]}

        Returns:
            최적 파라미터 및 결과
        """

        # 모든 파라미터 조합 생성
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))

        best_return = float('-inf')
        best_params = None
        best_metrics = None

        results = []

        for i, combination in enumerate(param_combinations):
            # 파라미터 딕셔너리 생성
            params = dict(zip(param_names, combination))

            # 백테스트 실행
            engine = BacktestEngine(
                strategy_code=self.strategy_code,
                parameters=params,
                initial_capital=self.initial_capital
            )

            result = engine.execute(self.market_data)

            # 결과 저장
            total_return = result.metrics.get('total_return', 0)
            results.append({
                'params': params,
                'metrics': result.metrics,
                'total_return': total_return
            })

            # 최고 수익률 업데이트
            if total_return > best_return:
                best_return = total_return
                best_params = params
                best_metrics = result.metrics

        self.optimization_results = results

        return {
            'method': 'grid_search',
            'best_params': best_params,
            'best_metrics': best_metrics,
            'total_iterations': len(param_combinations),
            'all_results': results
        }

    def bayesian_optimization(
        self,
        param_space: Dict[str, Tuple[float, float]],
        n_calls: int = 50
    ) -> Dict[str, Any]:
        """
        베이지안 최적화

        Args:
            param_space: 파라미터 범위
                예: {"short_period": (5, 30), "long_period": (30, 100)}
            n_calls: 최적화 반복 횟수

        Returns:
            최적 파라미터 및 결과
        """

        # skopt 공간 정의
        param_names = list(param_space.keys())
        dimensions = [
            Integer(int(bounds[0]), int(bounds[1]), name=name)
            for name, bounds in param_space.items()
        ]

        results = []

        @use_named_args(dimensions)
        def objective(**params):
            """최소화할 목적 함수 (음수 수익률)"""

            # 백테스트 실행
            engine = BacktestEngine(
                strategy_code=self.strategy_code,
                parameters=params,
                initial_capital=self.initial_capital
            )

            result = engine.execute(self.market_data)
            total_return = result.metrics.get('total_return', 0)

            # 결과 저장
            results.append({
                'params': params.copy(),
                'metrics': result.metrics,
                'total_return': total_return
            })

            # 음수 반환 (최소화 문제로 변환)
            return -total_return

        # 베이지안 최적화 실행
        res = gp_minimize(
            objective,
            dimensions,
            n_calls=n_calls,
            random_state=42,
            verbose=False
        )

        # 최적 파라미터
        best_params = dict(zip(param_names, res.x))
        best_return = -res.fun

        # 최적 파라미터로 재실행하여 메트릭 얻기
        engine = BacktestEngine(
            strategy_code=self.strategy_code,
            parameters=best_params,
            initial_capital=self.initial_capital
        )
        result = engine.execute(self.market_data)

        self.optimization_results = results

        return {
            'method': 'bayesian',
            'best_params': best_params,
            'best_metrics': result.metrics,
            'total_iterations': n_calls,
            'all_results': results
        }

    def random_search(
        self,
        param_space: Dict[str, Tuple[float, float]],
        n_iter: int = 100
    ) -> Dict[str, Any]:
        """
        무작위 서치 최적화

        Args:
            param_space: 파라미터 범위
            n_iter: 반복 횟수

        Returns:
            최적 파라미터 및 결과
        """

        best_return = float('-inf')
        best_params = None
        best_metrics = None
        results = []

        for i in range(n_iter):
            # 무작위 파라미터 생성
            params = {}
            for name, (min_val, max_val) in param_space.items():
                # 정수형 파라미터인지 확인
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[name] = np.random.uniform(min_val, max_val)

            # 백테스트 실행
            engine = BacktestEngine(
                strategy_code=self.strategy_code,
                parameters=params,
                initial_capital=self.initial_capital
            )

            result = engine.execute(self.market_data)
            total_return = result.metrics.get('total_return', 0)

            # 결과 저장
            results.append({
                'params': params,
                'metrics': result.metrics,
                'total_return': total_return
            })

            # 최고 수익률 업데이트
            if total_return > best_return:
                best_return = total_return
                best_params = params
                best_metrics = result.metrics

        self.optimization_results = results

        return {
            'method': 'random_search',
            'best_params': best_params,
            'best_metrics': best_metrics,
            'total_iterations': n_iter,
            'all_results': results
        }
