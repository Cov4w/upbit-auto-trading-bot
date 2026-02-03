"""
FastAPI Backend for Trading Bot
================================
기존 Streamlit 앱을 대체하는 FastAPI 기반 백엔드

Features:
- REST API for bot control
- WebSocket for real-time updates
- Async support for better performance
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from typing import Dict, List, Set
from datetime import datetime

from core.trading_bot import TradingBot
from models.schemas import (
    BotStatus, AccountBalance, TradeHistoryResponse,
    RecommendationsResponse, StartBotRequest, StopBotRequest,
    UpdateConfigRequest, TickerToggleRequest, SuccessResponse,
    ErrorResponse, OHLCVData
)
from routers import bot as bot_router
from routers import data as data_router
from routers import websocket as websocket_router
from routers import auth as auth_router
from routers import capital as capital_router


# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global bot instance (Singleton)
trading_bot: TradingBot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 수명 주기 관리
    - 시작 시: TradingBot 인스턴스 생성
    - 종료 시: 리소스 정리
    """
    global trading_bot

    logger.info("=" * 60)
    logger.info("🚀 FastAPI Application Starting...")
    logger.info("=" * 60)

    # Bot 인스턴스 생성
    trading_bot = TradingBot()
    logger.info("✅ Trading Bot Initialized")

    yield

    # Cleanup
    logger.info("🛑 Shutting down...")
    if trading_bot and trading_bot.is_running:
        trading_bot.stop()
    logger.info("✅ Cleanup Complete")


# FastAPI App
app = FastAPI(
    title="Trading Bot API",
    description="Self-Evolving Trading System REST API",
    version="2.0.0",
    lifespan=lifespan
)


# CORS Middleware (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React Dev Server
        "http://localhost:5173",  # Vite Dev Server
        "http://localhost:8080",  # 기타 로컬 서버
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include Routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(bot_router.router, prefix="/api/bot", tags=["Bot Control"])
app.include_router(data_router.router, prefix="/api/data", tags=["Data"])
app.include_router(capital_router.router, prefix="/api/capital", tags=["Capital"])
app.include_router(websocket_router.router, prefix="/ws", tags=["WebSocket"])


@app.get("/", response_model=SuccessResponse)
async def root():
    """
    Health Check Endpoint
    """
    return SuccessResponse(
        success=True,
        message="Trading Bot API is running",
        data={
            "version": "2.0.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/api/health")
async def health_check():
    """
    상세 헬스 체크
    """
    try:
        bot_status = trading_bot.get_status()
        return {
            "status": "healthy",
            "bot_running": bot_status['is_running'],
            "model_loaded": trading_bot.learner.model is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """일반 예외 핸들러"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Uvicorn으로 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드: 코드 변경 시 자동 재시작
        log_level="info"
    )
