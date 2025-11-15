# Trading Backtest Platform

주식/코인 트레이딩 전략을 백테스팅하고 성과를 분석하는 웹 플랫폼입니다.

## 프로젝트 구조

```
trading-backtest/
├── backend/          # FastAPI 백엔드
├── frontend/         # Next.js 프론트엔드
├── nginx/            # Nginx 리버스 프록시
├── docker/           # Docker Compose 설정
├── scripts/          # 유틸리티 스크립트
└── docs/             # 문서
```

## 기술 스택

### 백엔드
- FastAPI (Python 3.11+)
- PostgreSQL 16
- Redis
- SQLAlchemy 2.0
- Celery (비동기 작업)
- pandas, numpy, TA-Lib (데이터 처리)

### 프론트엔드
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Zustand (상태 관리)
- Recharts (차트)

### 인프라
- Docker & Docker Compose
- Nginx (리버스 프록시)
- Fly.io (배포)

## 로컬 개발 환경 설정

### 사전 요구사항
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- pnpm (Frontend 패키지 매니저)

### 1. 저장소 클론
```bash
git clone <repository-url>
cd trading-backtest
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 환경 변수 설정
```

### 3. Docker Compose로 실행 (권장)
```bash
cd docker
docker-compose up -d
```

서비스 접속:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Nginx: http://localhost:80

### 4. 개별 서비스 실행 (선택사항)

#### 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 프론트엔드
```bash
cd frontend
pnpm install
pnpm dev
```

## 데이터베이스 마이그레이션

### 마이그레이션 생성
```bash
cd backend
alembic revision --autogenerate -m "description"
```

### 마이그레이션 적용
```bash
alembic upgrade head
```

### 마이그레이션 롤백
```bash
alembic downgrade -1
```

## Fly.io 배포

### 1. Fly.io CLI 설치
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. 로그인
```bash
flyctl auth login
```

### 3. 앱 생성
```bash
flyctl apps create trading-backtest
```

### 4. PostgreSQL 생성 (선택사항)
```bash
flyctl postgres create --name trading-backtest-db
flyctl postgres attach --app trading-backtest trading-backtest-db
```

### 5. 시크릿 설정
```bash
flyctl secrets set SECRET_KEY=your-secret-key
flyctl secrets set DATABASE_URL=your-database-url
```

### 6. 배포
```bash
flyctl deploy
```

### 7. 앱 열기
```bash
flyctl open
```

## API 엔드포인트

### 인증
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/refresh` - 토큰 갱신
- `GET /api/v1/auth/me` - 사용자 정보

### 전략
- `GET /api/v1/strategies` - 전략 목록
- `POST /api/v1/strategies` - 전략 생성
- `GET /api/v1/strategies/{id}` - 전략 상세
- `PUT /api/v1/strategies/{id}` - 전략 수정
- `DELETE /api/v1/strategies/{id}` - 전략 삭제

### 백테스팅
- `POST /api/v1/backtests` - 백테스팅 시작
- `GET /api/v1/backtests` - 백테스팅 목록
- `GET /api/v1/backtests/{id}` - 백테스팅 결과
- `GET /api/v1/backtests/{id}/status` - 진행 상태
- `DELETE /api/v1/backtests/{id}` - 백테스팅 삭제

## 테스팅

### 백엔드 테스트
```bash
cd backend
pytest
```

### 프론트엔드 테스트
```bash
cd frontend
pnpm test
```

## 개발 가이드

자세한 내용은 다음 문서를 참조하세요:
- [구현방안.txt](./구현방안.txt) - 백테스팅 엔진 구현 방안
- [웹배포_기술스택.txt](./웹배포_기술스택.txt) - 웹 배포 기술 스택
- [docs/API.md](./docs/API.md) - API 문서
- [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) - 배포 가이드
- [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md) - 개발 가이드

## Supabase 마이그레이션

향후 Supabase로 마이그레이션할 계획입니다:
1. Supabase 프로젝트 생성
2. 스키마 복제
3. 데이터 마이그레이션
4. 연결 문자열 변경
5. Supabase Auth, Storage, Realtime 기능 활용

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!
