#!/bin/bash

# Development Startup Script
# 개발 환경에서 Backend와 Frontend를 동시에 실행합니다.

echo "🚀 Starting Trading Bot Development Environment..."

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend 시작
echo -e "${BLUE}[1/2]${NC} Starting Backend (FastAPI + Uvicorn)..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 백엔드가 시작될 때까지 대기
sleep 3

# Frontend 시작
echo -e "${BLUE}[2/2]${NC} Starting Frontend (React + Vite)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# 종료 핸들러
trap "echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

echo ""
echo -e "${GREEN}✅ Development environment is running!${NC}"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# 프로세스 대기
wait
