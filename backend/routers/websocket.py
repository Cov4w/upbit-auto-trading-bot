"""
WebSocket Router
================
실시간 데이터 스트리밍 (로그, 가격, 상태 변경 등)
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import logging
import asyncio
import json
from datetime import datetime


router = APIRouter()
logger = logging.getLogger(__name__)


# 연결된 클라이언트 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """모든 클라이언트에게 메시지 전송"""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")
                disconnected.add(connection)

        # 연결 끊긴 클라이언트 제거
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


def get_bot():
    """봇 인스턴스 가져오기"""
    from main import trading_bot
    return trading_bot


@router.websocket("/live")
async def websocket_live_updates(websocket: WebSocket):
    """
    실시간 업데이트 WebSocket 엔드포인트

    전송 메시지 타입:
    - status: 봇 상태 업데이트
    - price: 가격 업데이트
    - trade: 거래 실행 알림
    - log: 로그 메시지
    """
    await manager.connect(websocket)

    try:
        # 초기 상태 전송
        bot = get_bot()
        if bot:
            status = bot.get_status()
            await websocket.send_json({
                "type": "status",
                "data": status,
                "timestamp": datetime.now().isoformat()
            })

        # 클라이언트로부터 메시지 수신 대기
        while True:
            try:
                # 클라이언트 메시지 수신 (keep-alive)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)

                # ping/pong 처리
                if data == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                # 주기적으로 상태 업데이트 전송
                if bot:
                    try:
                        # 봇 상태
                        status = bot.get_status()

                        # 현재 가격 정보
                        prices = {}
                        for ticker in bot.tickers:
                            price = bot.exchange.get_current_price(ticker)
                            if price:
                                prices[ticker] = price

                        # 상태 전송
                        await websocket.send_json({
                            "type": "update",
                            "data": {
                                "status": status,
                                "prices": prices
                            },
                            "timestamp": datetime.now().isoformat()
                        })

                    except Exception as e:
                        logger.error(f"Error sending update: {e}")

            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")

    finally:
        manager.disconnect(websocket)


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """
    실시간 로그 스트리밍 WebSocket 엔드포인트

    로그 레벨에 따른 메시지 전송
    """
    await websocket.accept()
    logger.info("Log streaming client connected")

    try:
        # 로그 핸들러를 통해 실시간 로그 전송
        # (실제 구현은 logging handler를 커스터마이징 필요)

        # 예시: 주기적으로 최근 로그 전송
        while True:
            try:
                # Keep-alive
                await asyncio.sleep(5)

                # 로그 메시지 전송 (실제로는 로그 핸들러에서 가져와야 함)
                await websocket.send_json({
                    "type": "log",
                    "level": "info",
                    "message": "System is running normally",
                    "timestamp": datetime.now().isoformat()
                })

            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"Log WebSocket error: {e}")

    finally:
        logger.info("Log streaming client disconnected")


async def broadcast_trade_event(trade_data: dict):
    """
    거래 이벤트 브로드캐스트
    (trading_bot.py에서 호출 가능)
    """
    await manager.broadcast({
        "type": "trade",
        "data": trade_data,
        "timestamp": datetime.now().isoformat()
    })


async def broadcast_log(level: str, message: str):
    """
    로그 메시지 브로드캐스트
    (로그 핸들러에서 호출 가능)
    """
    await manager.broadcast({
        "type": "log",
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
