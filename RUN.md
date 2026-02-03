# 🚀 트레이딩 봇 실행 가이드

## 빠른 시작 (Quick Start)

### 1️⃣ 최초 설정 (한 번만 실행)

```bash
# Python 의존성 설치
pip install -r requirements.txt

# Frontend 의존성 설치
cd frontend
npm install
cd ..
```

### 2️⃣ 봇 실행

**방법 A: 자동 스크립트 (추천)**
```bash
./start_dev.sh
```

**방법 B: 수동 실행**
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3️⃣ 접속

- 🌐 **메인 대시보드**: http://localhost:3000
- 🔧 **API 문서**: http://localhost:8000/docs
- ❤️ **헬스 체크**: http://localhost:8000/api/health

---

## 📋 실행 전 체크리스트

✅ `.env` 파일에 API 키 설정 완료
✅ `requirements.txt` 의존성 설치 완료
✅ `frontend/` 폴더에서 `npm install` 완료

---

## 🛑 종료 방법

자동 스크립트 사용 시:
```bash
Ctrl + C
```

수동 실행 시:
```bash
# 각 터미널에서
Ctrl + C
```

---

## 🐳 Docker로 실행 (프로덕션)

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 종료
docker-compose down
```

접속: http://localhost:3000

---

## ⚠️ 문제 해결

### Backend가 안 켜질 때
```bash
# 포트 확인
lsof -i :8000

# 의존성 재설치
pip install --upgrade -r requirements.txt
```

### Frontend가 안 켜질 때
```bash
# node_modules 삭제 후 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API 연결 안 될 때
```bash
# Backend 먼저 실행되었는지 확인
curl http://localhost:8000/api/health
```

---

## 📁 주요 파일 위치

- **Backend 코드**: `backend/`
- **Frontend 코드**: `frontend/`
- **환경 설정**: `.env`
- **데이터베이스**: `data/trading.db`
- **모델**: `models/`
- **레거시 파일**: `legacy/` (Streamlit 앱)

---

## 🎯 다음 단계

1. 대시보드 접속 (http://localhost:3000)
2. ▶️ START 버튼 클릭
3. 봇이 자동으로 거래 시작!

Good luck! 🚀
