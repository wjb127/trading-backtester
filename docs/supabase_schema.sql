-- ========================================
-- Trading Backtest Database Schema
-- Supabase PostgreSQL
-- ========================================

-- UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- 1. 전략 테이블 (bt_strategies)
-- ========================================
CREATE TABLE bt_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 전략 테이블 인덱스
CREATE INDEX idx_bt_strategies_name ON bt_strategies(name);
CREATE INDEX idx_bt_strategies_is_active ON bt_strategies(is_active);
CREATE INDEX idx_bt_strategies_created_at ON bt_strategies(created_at DESC);

-- 전략 테이블 코멘트
COMMENT ON TABLE bt_strategies IS '트레이딩 전략 정보';
COMMENT ON COLUMN bt_strategies.id IS '전략 고유 ID';
COMMENT ON COLUMN bt_strategies.name IS '전략 이름';
COMMENT ON COLUMN bt_strategies.description IS '전략 설명';
COMMENT ON COLUMN bt_strategies.code IS '전략 코드 (Python)';
COMMENT ON COLUMN bt_strategies.parameters IS '전략 파라미터 (JSON)';
COMMENT ON COLUMN bt_strategies.is_active IS '활성화 여부';


-- ========================================
-- 2. 백테스트 테이블 (bt_backtests)
-- ========================================
CREATE TABLE bt_backtests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id UUID NOT NULL REFERENCES bt_strategies(id) ON DELETE CASCADE,
    symbol VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20, 2) NOT NULL DEFAULT 10000.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT bt_backtests_status_check
        CHECK (status IN ('pending', 'running', 'completed', 'failed'))
);

-- 백테스트 테이블 인덱스
CREATE INDEX idx_bt_backtests_strategy_id ON bt_backtests(strategy_id);
CREATE INDEX idx_bt_backtests_symbol ON bt_backtests(symbol);
CREATE INDEX idx_bt_backtests_status ON bt_backtests(status);
CREATE INDEX idx_bt_backtests_created_at ON bt_backtests(created_at DESC);
CREATE INDEX idx_bt_backtests_date_range ON bt_backtests(start_date, end_date);

-- 백테스트 테이블 코멘트
COMMENT ON TABLE bt_backtests IS '백테스팅 실행 기록';
COMMENT ON COLUMN bt_backtests.id IS '백테스트 고유 ID';
COMMENT ON COLUMN bt_backtests.strategy_id IS '전략 ID (외래키)';
COMMENT ON COLUMN bt_backtests.symbol IS '거래 심볼 (예: AAPL, BTC/USDT)';
COMMENT ON COLUMN bt_backtests.start_date IS '백테스트 시작일';
COMMENT ON COLUMN bt_backtests.end_date IS '백테스트 종료일';
COMMENT ON COLUMN bt_backtests.initial_capital IS '초기 자본';
COMMENT ON COLUMN bt_backtests.status IS '상태 (pending, running, completed, failed)';
COMMENT ON COLUMN bt_backtests.result IS '백테스트 결과 (JSON)';


-- ========================================
-- 3. 백테스트 거래 기록 테이블 (bt_backtest_trades)
-- ========================================
CREATE TABLE bt_backtest_trades (
    id BIGSERIAL PRIMARY KEY,
    backtest_id UUID NOT NULL REFERENCES bt_backtests(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    commission DECIMAL(20, 8) DEFAULT 0,
    portfolio_value DECIMAL(20, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT bt_backtest_trades_type_check
        CHECK (trade_type IN ('buy', 'sell'))
);

-- 거래 기록 테이블 인덱스
CREATE INDEX idx_bt_backtest_trades_backtest_id ON bt_backtest_trades(backtest_id);
CREATE INDEX idx_bt_backtest_trades_timestamp ON bt_backtest_trades(timestamp);
CREATE INDEX idx_bt_backtest_trades_type ON bt_backtest_trades(trade_type);

-- 거래 기록 테이블 코멘트
COMMENT ON TABLE bt_backtest_trades IS '백테스트 거래 내역';
COMMENT ON COLUMN bt_backtest_trades.backtest_id IS '백테스트 ID (외래키)';
COMMENT ON COLUMN bt_backtest_trades.timestamp IS '거래 시각';
COMMENT ON COLUMN bt_backtest_trades.trade_type IS '거래 유형 (buy, sell)';
COMMENT ON COLUMN bt_backtest_trades.price IS '거래 가격';
COMMENT ON COLUMN bt_backtest_trades.quantity IS '거래 수량';
COMMENT ON COLUMN bt_backtest_trades.commission IS '수수료';
COMMENT ON COLUMN bt_backtest_trades.portfolio_value IS '포트폴리오 가치';


-- ========================================
-- 4. 시장 데이터 테이블 (bt_market_data)
-- ========================================
CREATE TABLE bt_market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(30, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT bt_market_data_unique UNIQUE (symbol, timestamp)
);

-- 시장 데이터 테이블 인덱스
CREATE INDEX idx_bt_market_data_symbol ON bt_market_data(symbol);
CREATE INDEX idx_bt_market_data_timestamp ON bt_market_data(timestamp);
CREATE INDEX idx_bt_market_data_symbol_timestamp ON bt_market_data(symbol, timestamp DESC);

-- 시장 데이터 테이블 코멘트
COMMENT ON TABLE bt_market_data IS '시장 가격 데이터 (OHLCV)';
COMMENT ON COLUMN bt_market_data.symbol IS '거래 심볼';
COMMENT ON COLUMN bt_market_data.timestamp IS '데이터 시각';
COMMENT ON COLUMN bt_market_data.open IS '시가';
COMMENT ON COLUMN bt_market_data.high IS '고가';
COMMENT ON COLUMN bt_market_data.low IS '저가';
COMMENT ON COLUMN bt_market_data.close IS '종가';
COMMENT ON COLUMN bt_market_data.volume IS '거래량';


-- ========================================
-- 5. 트리거: updated_at 자동 업데이트
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bt_strategies_updated_at
    BEFORE UPDATE ON bt_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ========================================
-- 6. 샘플 데이터 삽입 (선택사항)
-- ========================================

-- 샘플 전략 1: 이동평균 크로스오버
INSERT INTO bt_strategies (name, description, code, parameters) VALUES
(
    '이동평균 크로스오버',
    '단기 이동평균이 장기 이동평균을 상향 돌파할 때 매수, 하향 돌파할 때 매도',
    'def strategy(data):
    short_ma = data[''close''].rolling(window=20).mean()
    long_ma = data[''close''].rolling(window=50).mean()

    signals = []
    for i in range(len(data)):
        if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
            signals.append(''buy'')
        elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
            signals.append(''sell'')
        else:
            signals.append(''hold'')

    return signals',
    '{"short_period": 20, "long_period": 50}'::jsonb
);

-- 샘플 전략 2: RSI 전략
INSERT INTO bt_strategies (name, description, code, parameters) VALUES
(
    'RSI 과매수/과매도',
    'RSI가 30 이하일 때 매수, 70 이상일 때 매도',
    'def strategy(data):
    rsi_period = 14
    delta = data[''close''].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    signals = []
    for i in range(len(data)):
        if rsi[i] < 30:
            signals.append(''buy'')
        elif rsi[i] > 70:
            signals.append(''sell'')
        else:
            signals.append(''hold'')

    return signals',
    '{"rsi_period": 14, "oversold": 30, "overbought": 70}'::jsonb
);

-- 샘플 전략 3: 볼린저 밴드
INSERT INTO bt_strategies (name, description, code, parameters) VALUES
(
    '볼린저 밴드 돌파',
    '가격이 하단 밴드를 터치하면 매수, 상단 밴드를 터치하면 매도',
    'def strategy(data):
    period = 20
    std_dev = 2

    sma = data[''close''].rolling(window=period).mean()
    std = data[''close''].rolling(window=period).std()

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    signals = []
    for i in range(len(data)):
        if data[''close''][i] <= lower_band[i]:
            signals.append(''buy'')
        elif data[''close''][i] >= upper_band[i]:
            signals.append(''sell'')
        else:
            signals.append(''hold'')

    return signals',
    '{"period": 20, "std_dev": 2}'::jsonb
);


-- ========================================
-- 7. Row Level Security (RLS) 설정 (선택사항)
-- ========================================
-- Supabase에서 인증을 사용하는 경우 활성화

-- ALTER TABLE bt_strategies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bt_backtests ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bt_backtest_trades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bt_market_data ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능 (혼자 사용하는 경우)
-- CREATE POLICY "Enable read access for all users" ON bt_strategies FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON bt_backtests FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON bt_backtest_trades FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON bt_market_data FOR SELECT USING (true);

-- 모든 사용자가 쓰기 가능 (혼자 사용하는 경우)
-- CREATE POLICY "Enable insert for all users" ON bt_strategies FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable insert for all users" ON bt_backtests FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable insert for all users" ON bt_backtest_trades FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Enable insert for all users" ON bt_market_data FOR INSERT WITH CHECK (true);


-- ========================================
-- 8. 뷰 생성: 백테스트 통계
-- ========================================
CREATE OR REPLACE VIEW vw_bt_backtest_stats AS
SELECT
    b.id,
    b.symbol,
    s.name AS strategy_name,
    b.start_date,
    b.end_date,
    b.initial_capital,
    b.status,
    (b.result->>'total_return')::DECIMAL AS total_return,
    (b.result->>'total_return_pct')::DECIMAL AS total_return_pct,
    (b.result->>'max_drawdown')::DECIMAL AS max_drawdown,
    (b.result->>'sharpe_ratio')::DECIMAL AS sharpe_ratio,
    (b.result->>'total_trades')::INTEGER AS total_trades,
    (b.result->>'win_rate')::DECIMAL AS win_rate,
    b.created_at,
    b.completed_at
FROM bt_backtests b
JOIN bt_strategies s ON b.strategy_id = s.id
WHERE b.status = 'completed';

COMMENT ON VIEW vw_bt_backtest_stats IS '백테스트 통계 뷰';


-- ========================================
-- 완료 메시지
-- ========================================
DO $$
BEGIN
    RAISE NOTICE 'Trading Backtest 데이터베이스 스키마 생성 완료!';
    RAISE NOTICE '테이블 목록:';
    RAISE NOTICE '  - bt_strategies (전략)';
    RAISE NOTICE '  - bt_backtests (백테스트)';
    RAISE NOTICE '  - bt_backtest_trades (거래 기록)';
    RAISE NOTICE '  - bt_market_data (시장 데이터)';
    RAISE NOTICE '뷰:';
    RAISE NOTICE '  - vw_bt_backtest_stats (백테스트 통계)';
END $$;
