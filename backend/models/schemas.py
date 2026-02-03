"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime


class BotStatus(BaseModel):
    """봇 상태 응답 모델"""
    is_running: bool
    tickers: List[str]
    use_ai_selection: bool
    recommended_coins: List[Dict[str, Any]]
    positions: Dict[str, Dict[str, Any]]
    model_accuracy: float
    total_trades: int
    win_rate: float
    avg_profit_pct: float
    session_trades: int
    session_win_rate: float
    last_trained: Optional[str]
    total_learning_samples: int
    today_profit: Optional[float] = None
    is_updating_recommendations: bool
    
    # Configuration
    trade_amount: Optional[float] = None
    target_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    rebuy_threshold: Optional[float] = None


class AccountBalance(BaseModel):
    """계좌 잔액 응답 모델"""
    krw_balance: float
    holdings: List[Dict[str, Any]]
    total_value: float
    api_ok: bool


class Trade(BaseModel):
    """거래 내역 모델"""
    id: Optional[int]
    ticker: str
    timestamp: str
    entry_price: float
    exit_price: Optional[float]
    profit_rate: Optional[float]
    is_profitable: Optional[bool]
    model_confidence: float
    status: str


class TradeHistoryResponse(BaseModel):
    """거래 내역 조회 응답"""
    trades: List[Trade]
    total: int
    page: int
    page_size: int


class CoinRecommendation(BaseModel):
    """코인 추천 모델"""
    ticker: str
    score: float
    confidence: float
    recommendation: bool
    current_price: Optional[float]
    features: Dict[str, float]


class RecommendationsResponse(BaseModel):
    """코인 추천 목록 응답"""
    recommendations: List[CoinRecommendation]
    updated_at: str


class StartBotRequest(BaseModel):
    """봇 시작 요청 (옵션)"""
    tickers: Optional[List[str]] = None


class StopBotRequest(BaseModel):
    """봇 중지 요청 (옵션)"""
    pass


class UpdateConfigRequest(BaseModel):
    """설정 업데이트 요청"""
    trade_amount: Optional[float] = None
    target_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    rebuy_threshold: Optional[float] = None


class TickerToggleRequest(BaseModel):
    """티커 토글 요청"""
    ticker: str


class WebSocketMessage(BaseModel):
    """WebSocket 메시지 모델"""
    type: str  # "log", "price", "status", "trade"
    data: Dict[str, Any]
    timestamp: str


class OHLCVData(BaseModel):
    """OHLCV 차트 데이터"""
    ticker: str
    interval: str
    data: List[Dict[str, Any]]


class SuccessResponse(BaseModel):
    """일반 성공 응답"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: str
    detail: Optional[str] = None
