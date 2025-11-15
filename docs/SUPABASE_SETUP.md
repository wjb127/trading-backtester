# Supabase 연동 가이드

이 문서는 Trading Backtest 프로젝트를 Supabase와 연동하는 방법을 설명합니다.

## 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 에 접속하여 로그인
2. "New Project" 클릭
3. 프로젝트 정보 입력:
   - **Name**: trading-backtest
   - **Database Password**: 안전한 비밀번호 생성 (나중에 필요함)
   - **Region**: Northeast Asia (Seoul) - 가장 가까운 리전 선택
4. "Create new project" 클릭

## 2. 데이터베이스 스키마 생성

### 2.1 SQL Editor에서 직접 실행

1. Supabase 대시보드에서 **SQL Editor** 메뉴로 이동
2. "+ New query" 클릭
3. `docs/supabase_schema.sql` 파일의 내용을 복사하여 붙여넣기
4. "Run" 버튼 클릭하여 실행

### 2.2 스키마 확인

SQL Editor에서 다음 쿼리를 실행하여 테이블이 정상적으로 생성되었는지 확인:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'bt_%';
```

생성된 테이블:
- `bt_strategies` - 전략
- `bt_backtests` - 백테스트
- `bt_backtest_trades` - 거래 기록
- `bt_market_data` - 시장 데이터

## 3. 연결 정보 확인

1. Supabase 대시보드에서 **Settings** > **Database** 메뉴로 이동
2. **Connection string** 섹션에서 연결 정보 확인

### 3.1 Connection Pooler (추천)

```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres
```

### 3.2 Direct Connection

```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

> **참고**: Connection Pooler를 사용하는 것이 권장됩니다.

## 4. 백엔드 환경 변수 설정

### 4.1 `.env` 파일 생성

`trading-backtest/backend/.env` 파일을 생성하고 다음 내용을 입력:

```bash
# Supabase Database Connection
DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres

# Redis (로컬 개발용)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Debug
DEBUG=True
```

### 4.2 환경 변수 설명

- `[PROJECT-REF]`: Supabase 프로젝트 참조 ID (대시보드에서 확인)
- `[PASSWORD]`: Supabase 프로젝트 생성 시 설정한 데이터베이스 비밀번호
- `DATABASE_URL`: **주의** - `postgresql+asyncpg://` 프로토콜 사용 (asyncpg 드라이버)

## 5. 백엔드 서버 재시작

### 5.1 서버 중지

현재 실행 중인 백엔드 서버가 있다면 중지 (Ctrl+C)

### 5.2 서버 시작

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. API 테스트

### 6.1 Health Check

```bash
curl http://localhost:8000/
```

응답:
```json
{
  "message": "Trading Backtest API",
  "version": "0.1.0",
  "docs": "/api/docs"
}
```

### 6.2 전략 목록 조회

```bash
curl http://localhost:8000/api/v1/strategies
```

응답 (샘플 데이터가 있는 경우):
```json
{
  "strategies": [
    {
      "id": "...",
      "name": "이동평균 크로스오버",
      "description": "단기 이동평균이 장기 이동평균을 상향 돌파할 때 매수...",
      ...
    }
  ],
  "total": 3
}
```

### 6.3 전략 생성 테스트

```bash
curl -X POST http://localhost:8000/api/v1/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 전략",
    "description": "간단한 테스트 전략입니다",
    "code": "def strategy(data):\n    return []",
    "parameters": {"test": true}
  }'
```

## 7. Swagger UI에서 테스트

브라우저에서 http://localhost:8000/api/docs 로 접속하여 대화형 API 문서에서 테스트할 수 있습니다.

## 8. 문제 해결

### 8.1 연결 오류

**증상**: `could not translate host name` 또는 `connection refused`

**해결책**:
1. DATABASE_URL이 올바른지 확인
2. Supabase 대시보드에서 프로젝트가 활성 상태인지 확인
3. 방화벽 설정 확인

### 8.2 인증 오류

**증상**: `password authentication failed`

**해결책**:
1. 비밀번호가 정확한지 확인
2. URL 인코딩이 필요한 특수문자가 있는지 확인
3. Supabase에서 비밀번호 재설정

### 8.3 테이블을 찾을 수 없음

**증상**: `relation "bt_strategies" does not exist`

**해결책**:
1. SQL Editor에서 스키마 생성 SQL을 다시 실행
2. 올바른 데이터베이스에 연결되었는지 확인

## 9. 프로덕션 배포 시 고려사항

### 9.1 Connection Pooling

Supabase의 Connection Pooler를 사용하는 것이 좋습니다:
- 포트: 6543 (Pooler) 또는 5432 (Direct)
- Pooler 사용 시 더 많은 동시 연결 지원

### 9.2 환경 변수 관리

- 프로덕션 환경에서는 `.env` 파일 대신 환경 변수 사용
- 민감한 정보는 절대 Git에 커밋하지 않기
- Fly.io 배포 시: `flyctl secrets set DATABASE_URL=...`

### 9.3 보안

- 강력한 비밀번호 사용
- 필요한 경우 Row Level Security (RLS) 활성화
- IP 화이트리스트 설정 (Supabase Pro 이상)

## 10. 다음 단계

- ✅ 데이터베이스 연결 완료
- ✅ 전략 CRUD API 테스트
- 🔲 백테스팅 엔진 구현
- 🔲 프론트엔드 API 연동
- 🔲 실시간 데이터 수집 구현

## 11. 참고 자료

- [Supabase 공식 문서](https://supabase.com/docs)
- [SQLAlchemy Async 문서](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI 데이터베이스 가이드](https://fastapi.tiangolo.com/tutorial/sql-databases/)
