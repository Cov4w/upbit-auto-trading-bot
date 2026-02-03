"""
Data Router
===========
데이터 조회 API (계좌 잔액, 거래 내역, 추천 코인, 차트 데이터 등)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
import sqlite3
import pandas as pd
from datetime import datetime

from models.schemas import (
    AccountBalance, TradeHistoryResponse, RecommendationsResponse,
    CoinRecommendation, OHLCVData, Trade, User
)


router = APIRouter()
logger = logging.getLogger(__name__)


def get_current_user():
    """Import auth dependency to avoid circular imports"""
    from routers.auth import get_current_user
    return get_current_user


def get_bot():
    """봇 인스턴스 가져오기"""
    from main import trading_bot
    if trading_bot is None:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    return trading_bot


@router.get("/balance", response_model=AccountBalance)
async def get_account_balance(current_user: User = Depends(get_current_user)):
    """
    계좌 잔액 조회

    Returns:
        AccountBalance: KRW 잔액 및 보유 코인 정보
    """
    try:
        bot = get_bot()
        balance = bot.get_account_balance()
        return AccountBalance(**balance)
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=TradeHistoryResponse)
async def get_trade_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (open/closed)"),
    current_user: User = Depends(get_current_user)
):
    """
    거래 내역 조회 (페이지네이션)

    Args:
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지당 항목 수 (1~100)
        status: 상태 필터 (open/closed)

    Returns:
        TradeHistoryResponse: 거래 내역 리스트
    """
    try:
        bot = get_bot()

        # DB 조회 (use context manager for safe connection handling)
        with sqlite3.connect(bot.memory.db_path) as conn:
            # 전체 개수 (parameterized query for safety)
            if status:
                count_query = "SELECT COUNT(*) FROM trades WHERE status = ?"
                total = pd.read_sql_query(count_query, conn, params=(status,)).iloc[0, 0]
            else:
                count_query = "SELECT COUNT(*) FROM trades"
                total = pd.read_sql_query(count_query, conn).iloc[0, 0]

            # 데이터 조회 (parameterized query)
            if status:
                query = """
                    SELECT
                        id, ticker, timestamp, entry_price, exit_price,
                        profit_rate, is_profitable, model_confidence, status
                    FROM trades
                    WHERE status = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
                df = pd.read_sql_query(query, conn, params=(status, page_size, (page - 1) * page_size))
            else:
                query = """
                    SELECT
                        id, ticker, timestamp, entry_price, exit_price,
                        profit_rate, is_profitable, model_confidence, status
                    FROM trades
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
                df = pd.read_sql_query(query, conn, params=(page_size, (page - 1) * page_size))

        # Trade 모델로 변환
        trades = []
        for _, row in df.iterrows():
            trades.append(Trade(
                id=int(row['id']) if pd.notna(row['id']) else None,
                ticker=row['ticker'],
                timestamp=row['timestamp'],
                entry_price=float(row['entry_price']),
                exit_price=float(row['exit_price']) if pd.notna(row['exit_price']) else None,
                profit_rate=float(row['profit_rate']) if pd.notna(row['profit_rate']) else None,
                is_profitable=bool(row['is_profitable']) if pd.notna(row['is_profitable']) else None,
                model_confidence=float(row['model_confidence']),
                status=row['status']
            ))

        return TradeHistoryResponse(
            trades=trades,
            total=int(total),
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Failed to get trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(current_user: User = Depends(get_current_user)):
    """
    AI 추천 코인 목록 조회

    Returns:
        RecommendationsResponse: 추천 코인 리스트 (상위 5개)
    """
    try:
        bot = get_bot()

        # 캐시된 추천 목록 사용
        recs = bot.recommended_coins

        # 추천 목록이 비어있으면 새로 생성
        if not recs:
            recs = bot.update_coin_recommendations()

        # CoinRecommendation 모델로 변환
        recommendations = []
        for rec in recs:
            recommendations.append(CoinRecommendation(
                ticker=rec['ticker'],
                score=rec['score'],
                confidence=rec['confidence'],
                recommendation=rec['recommendation'],
                current_price=rec.get('current_price'),
                features=rec['features']
            ))

        return RecommendationsResponse(
            recommendations=recommendations,
            updated_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ohlcv/{ticker}", response_model=OHLCVData)
async def get_ohlcv_data(
    ticker: str,
    interval: str = Query("day", description="Candle interval (minute1, minute3, minute5, day)"),
    current_user: User = Depends(get_current_user)
):
    """
    OHLCV 차트 데이터 조회

    Args:
        ticker: 코인 티커 (예: BTC, ETH)
        interval: 캔들 간격 (minute1, minute3, minute5, day)

    Returns:
        OHLCVData: OHLCV 데이터
    """
    try:
        bot = get_bot()

        # 데이터 조회
        df = bot.exchange.get_ohlcv(ticker, interval=interval)

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        # DataFrame을 dict 리스트로 변환
        data = []
        for idx, row in df.iterrows():
            data.append({
                "timestamp": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume']) if 'volume' in row else 0
            })

        return OHLCVData(
            ticker=ticker,
            interval=interval,
            data=data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get OHLCV data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(current_user: User = Depends(get_current_user)):
    """
    트레이딩 통계 조회

    Returns:
        dict: 통계 정보 (승률, 평균 수익률, 총 거래 수 등)
    """
    try:
        bot = get_bot()
        stats = bot.memory.get_statistics()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_current_positions(current_user: User = Depends(get_current_user)):
    """
    현재 보유 포지션 조회

    Returns:
        dict: 현재 보유 중인 포지션 정보
    """
    try:
        bot = get_bot()

        positions = []
        for ticker, position in bot.positions.items():
            # 현재 가격 조회
            current_price = bot.exchange.get_current_price(ticker)

            # 수익률 계산
            profit_rate = 0
            if current_price and position['entry_price'] > 0:
                profit_rate = (current_price - position['entry_price']) / position['entry_price']

            positions.append({
                "ticker": ticker,
                "entry_price": position['entry_price'],
                "amount": position['amount'],
                "entry_time": position['entry_time'].isoformat() if hasattr(position['entry_time'], 'isoformat') else str(position['entry_time']),
                "current_price": current_price,
                "profit_rate": profit_rate,
                "profit_pct": profit_rate * 100
            })

        return {
            "success": True,
            "data": {
                "positions": positions,
                "total_positions": len(positions)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
