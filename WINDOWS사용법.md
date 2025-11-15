# Trading Backtest Platform - Windows 사용법

## 🚀 빠른 시작 (더블클릭으로 실행)

바탕화면에 두 개의 배치 파일이 있습니다:

### 1. `Trading-Backtest-시작.bat`
- **더블클릭**하면 자동으로:
  - 백엔드 서버 시작 (포트 8000)
  - 프론트엔드 서버 시작 (포트 3000)
  - 브라우저에서 http://localhost:3000 자동으로 열림

### 2. `Trading-Backtest-종료.bat`
- **더블클릭**하면 실행 중인 모든 서버를 종료합니다

## 📱 접속 URL

실행 후 다음 URL로 접속할 수 있습니다:

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/docs

## 🎯 주요 기능

### 1. 전략 관리 (`/strategies`)
- 이동평균, RSI, 볼린저 밴드 등 예시 전략 제공
- 커스텀 전략 생성 가능
- 파라미터 최적화 (Grid Search, Bayesian, Random Search)

### 2. 백테스팅 (`/backtests`)
- 전략 선택
- 심볼 입력 (AAPL, TSLA, BTC-USD 등)
- 기간 설정
- 초기 자본 설정
- 백테스트 실행 및 결과 확인

### 3. 결과 분석
- 수익률, 최대낙폭, 샤프비율 등 지표
- 수익 곡선 차트
- 거래 내역
- PDF 리포트 다운로드

## 🛠️ 수동 실행 방법 (개발자용)

WSL2 터미널에서:

```bash
# 백엔드 실행
cd /home/jbwi127/trading-backtest/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 새 터미널에서 프론트엔드 실행
cd /home/jbwi127/trading-backtest/frontend
npm run dev
```

## 🔧 문제 해결

### 서버가 시작되지 않는 경우
1. `Trading-Backtest-종료.bat` 실행
2. 2-3초 대기
3. `Trading-Backtest-시작.bat` 다시 실행

### 포트 충돌 문제
```bash
# WSL2에서 실행
lsof -ti:8000 | xargs kill -9  # 백엔드 포트
lsof -ti:3000 | xargs kill -9  # 프론트엔드 포트
```

### 데이터베이스 연결 문제
- `.env` 파일에서 `SUPABASE_URL`과 `SUPABASE_KEY` 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

## 📦 의존성 업데이트

백엔드 패키지 업데이트:
```bash
cd /home/jbwi127/trading-backtest/backend
source venv/bin/activate
pip install -r requirements.txt
```

프론트엔드 패키지 업데이트:
```bash
cd /home/jbwi127/trading-backtest/frontend
npm install
```

## 🔄 Git 업데이트

최신 코드 받기:
```bash
cd /home/jbwi127/trading-backtest
git pull origin main
```

## 📊 백테스트 예시

### AAPL 백테스트
- 심볼: `AAPL`
- 기간: `2023-01-01` ~ `2024-01-01`
- 초기 자본: `10000`
- 전략: 이동평균 크로스오버

**결과 예시**:
- 수익률: 2.48%
- 최대낙폭: 2.68%
- 샤프비율: 0.62
- 거래 횟수: 1

## 💡 팁

1. **백테스트 전에**: 전략의 파라미터를 최적화해보세요
2. **다양한 기간**: 여러 기간으로 테스트하여 전략의 강건성 확인
3. **다양한 심볼**: 다른 주식이나 암호화폐로도 테스트
4. **PDF 리포트**: 중요한 백테스트 결과는 PDF로 저장

## 📞 지원

문제가 발생하면:
1. GitHub Issues: [trading-backtester](https://github.com/wjb127/trading-backtester)
2. 로그 확인: 터미널 창에서 오류 메시지 확인

## 📝 버전 정보

- Python: 3.10+
- Node.js: 20+
- yfinance: 0.2.66
- FastAPI: 최신 버전
- Next.js: 14

---

**즐거운 백테스팅 되세요!** 🎉
