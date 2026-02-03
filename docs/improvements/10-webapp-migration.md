# 10. Web App Migration (Streamlit → FastAPI + React)

## 📋 개요
- **우선순위:** Future (차기 메이저 업데이트)
- **난이도:** 매우 어려움 (Full-stack Development)
- **소요 시간:** 3~5일 (예상)
- **목표:** CPU/RAM 리소스 효율화 및 실시간성이 보장되는 전문적인 트레이딩 대시보드 구축

## ❌ 현재 문제점 (Streamlit)
1.  **리소스 과다 점유:** 화면 갱신(Rerun) 때마다 파이썬 스크립트 전체 재실행으로 CPU 부하 발생 (CPU 100% 이슈).
2.  **구조적 한계:** `TradingBot` 프로세스와 UI 프로세스가 결합되어 있어, UI가 멈추면 봇도 영향받을 수 있음.
3.  **유저 경험:** 단순 새로고침 방식이라 차트가 깜빡이거나 반응이 느림.

## ✅ 해결 방법: Modern Tech Stack 도입

### 1. 아키텍처 변경
```mermaid
graph TD
    User[사용자 브라우저 (React)] <-->|REST API / WebSocket| Server[FastAPI 서버]
    Server <-->|Control| Bot[Trading Bot Process]
    Bot <-->|Read/Write| DB[(SQLite)]
    Server <-->|Read Only| DB
```

### 2. 기술 스택 (Tech Stack)
*   **Backend:** `Python FastAPI` + `Uvicorn`
    *   비동기(ASGI) 지원으로 초고속 API 처리.
    *   `Uvicorn`: ASGI 서버로 FastAPI 애플리케이션 실행.
    *   WebSocket을 통해 실시간 호가/체결 정보 푸시.
    *   `Pydantic`을 이용한 데이터 검증.
*   **Frontend:** `React` (with `Vite`, `TypeScript`)
    *   **SPA (Single Page Application):** 깜빡임 없는 부드러운 화면 전환.
    *   **Charts:** `TradingView Lightweight Charts` (업비트와 동일한 차트 품질) 또는 `Recharts`.
    *   **UI Framework:** `TailwindCSS` + `Shadcn/UI` (모던하고 깔끔한 디자인).
*   **State Management:** `TanStack Query` (서버 상태 동기화) + `Zustand` (클라이언트 상태).

## 📁 프로젝트 구조

```
bitThumb_std/
├── backend/
│   ├── main.py                 # FastAPI 메인 애플리케이션
│   ├── routers/
│   │   ├── bot.py             # 봇 제어 API
│   │   ├── data.py            # 데이터 조회 API
│   │   └── websocket.py       # WebSocket 핸들러
│   ├── models/
│   │   └── schemas.py         # Pydantic 모델
│   ├── core/
│   │   ├── trading_bot.py     # 기존 trading_bot.py 재사용
│   │   ├── data_manager.py    # 기존 data_manager.py 재사용
│   │   ├── coin_selector.py   # 기존 coin_selector.py 재사용
│   │   └── exchange_manager.py # 기존 exchange_manager.py 재사용
│   └── requirements.txt       # Backend 의존성
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React 컴포넌트
│   │   ├── pages/             # 페이지 컴포넌트
│   │   ├── hooks/             # Custom Hooks
│   │   ├── api/               # API 클라이언트
│   │   └── App.tsx            # 메인 앱
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── .env
```

## 📅 구현 단계 (Roadmap)

### Phase 1: Backend API 구축 (FastAPI)
- [ ] 프로젝트 구조 분리 (`/backend`, `/frontend`)
- [ ] `main.py` 생성 및 `TradingBot`을 백그라운드 Task로 실행하도록 수정
- [ ] REST API 엔드포인트 구현:
    - `POST /api/bot/start`: 봇 시작
    - `POST /api/bot/stop`: 봇 정지
    - `GET /api/status`: 봇 상태, 자산, 포지션 조회
    - `GET /api/history`: 매매 기록 조회 (Pagination 적용)
    - `GET /api/coins/recommend`: 추천 코인 목록 조회
- [ ] WebSocket 구현: 실시간 로그 및 가격 정보 스트리밍

### Phase 2: Frontend UI 개발 (React)
- [ ] Vite 프로젝트 생성 (`npm create vite@latest`)
- [ ] 대시보드 레이아웃 설계 (사이드바, 헤더, 메인 컨텐츠)
- [ ] 컴포넌트 개발:
    - `StatusCard`: 봇 상태 및 자산 현황 표시
    - `TradingChart`: 캔들스틱 차트 및 매매 마커 표시
    - `TradeHistoryTable`: 매매 이력 테이블 (필터링/정렬 기능)
    - `LogViewer`: 실시간 로그 뷰어

### Phase 3: 연동 및 최적화
- [ ] CORS 설정 및 Proxy 설정
- [ ] API 연동 및 에러 핸들링
- [ ] 성능 최적화 (불필요한 리렌더링 방지)
- [ ] Docker Compose 배포 설정 (`Dockerfile`, `docker-compose.yml`)

## 📊 기대 효과
1.  **리소스 절감:** 서버는 데이터(JSON)만 보내므로 CPU 사용량 **70% 이상 감소 예상**.
2.  **안정성:** 봇 코어와 UI가 분리되어 봇의 안정적인 24시간 가동 보장.
3.  **확장성:** 추후 모바일 앱(React Native)이나 알림 서버 연동이 매우 쉬워짐.
4.  **UX 향상:** 실시간 데이터 갱신으로 전문 HTS(Home Trading System) 수준의 사용자 경험 제공.

## 🚀 실행 방법

### 개발 환경
```bash
# Backend 실행
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend 실행 (새 터미널)
cd frontend
npm install
npm run dev
```

### 프로덕션 환경 (Docker)
```bash
# Docker Compose로 전체 스택 실행
docker-compose up -d

# 접속: http://localhost:3000
```

### Uvicorn 고급 옵션
```bash
# 워커 프로세스 4개로 실행 (성능 향상)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# HTTPS 지원
uvicorn main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

## ⚠️ 주의사항
- 기존 `app.py`는 폐기되거나 레거시로 남겨둠.
- 프론트엔드 빌드 프로세스가 추가되어 배포 과정이 약간 복잡해짐.
- 초기 개발 비용(시간)이 듭니다.
- Backend와 Frontend가 분리되므로 CORS 설정 필수.
- WebSocket 연결은 로드 밸런서 사용 시 Sticky Session 필요.
