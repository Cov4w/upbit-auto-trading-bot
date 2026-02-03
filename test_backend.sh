#!/bin/bash

# Backend API Test Script
# 백엔드 API가 올바르게 작동하는지 테스트합니다.

echo "🧪 Testing Backend API..."

BASE_URL="http://localhost:8000"

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 헬스 체크
echo -n "Testing health endpoint... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/api/health)
if [ $STATUS -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $STATUS)"
fi

# 봇 상태 조회
echo -n "Testing bot status endpoint... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/api/bot/status)
if [ $STATUS -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $STATUS)"
fi

# 계좌 잔액 조회
echo -n "Testing balance endpoint... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/api/data/balance)
if [ $STATUS -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $STATUS)"
fi

# 거래 내역 조회
echo -n "Testing history endpoint... "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/api/data/history)
if [ $STATUS -eq 200 ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $STATUS)"
fi

echo ""
echo "📖 View full API documentation: ${BASE_URL}/docs"
