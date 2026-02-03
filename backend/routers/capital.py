"""
Capital Routes
=============
입출금 내역 관리 API
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from models.schemas import User
from routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency: Get Trading Bot Instance
def get_bot():
    from main import trading_bot
    if trading_bot is None:
        raise HTTPException(status_code=503, detail="Trading bot not initialized")
    return trading_bot


class DepositRequest(BaseModel):
    """입금 요청"""
    amount: float
    note: Optional[str] = ""


class WithdrawalRequest(BaseModel):
    """출금 요청"""
    amount: float
    note: Optional[str] = ""


class TransactionResponse(BaseModel):
    """거래 응답"""
    success: bool
    message: str
    transaction_id: Optional[int] = None


class CapitalSummary(BaseModel):
    """자본 요약"""
    total_deposits: float
    total_withdrawals: float
    net_capital: float


@router.post("/deposit", response_model=TransactionResponse)
async def add_deposit(
    request: DepositRequest,
    current_user: User = Depends(get_current_user)
):
    """입금 기록 추가"""
    try:
        bot = get_bot()
        transaction_id = bot.capital.add_deposit(request.amount, request.note)

        return TransactionResponse(
            success=True,
            message=f"{request.amount:,.0f} 원 입금 기록 완료",
            transaction_id=transaction_id
        )
    except Exception as e:
        logger.error(f"Failed to add deposit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/withdrawal", response_model=TransactionResponse)
async def add_withdrawal(
    request: WithdrawalRequest,
    current_user: User = Depends(get_current_user)
):
    """출금 기록 추가"""
    try:
        bot = get_bot()
        transaction_id = bot.capital.add_withdrawal(request.amount, request.note)

        return TransactionResponse(
            success=True,
            message=f"{request.amount:,.0f} 원 출금 기록 완료",
            transaction_id=transaction_id
        )
    except Exception as e:
        logger.error(f"Failed to add withdrawal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=CapitalSummary)
async def get_capital_summary(current_user: User = Depends(get_current_user)):
    """자본 요약 조회"""
    try:
        bot = get_bot()

        return CapitalSummary(
            total_deposits=bot.capital.get_total_deposits(),
            total_withdrawals=bot.capital.get_total_withdrawals(),
            net_capital=bot.capital.get_net_capital()
        )
    except Exception as e:
        logger.error(f"Failed to get capital summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
async def get_transactions(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """전체 입출금 내역 조회"""
    try:
        bot = get_bot()
        transactions = bot.capital.get_all_transactions(limit)

        return {
            "success": True,
            "data": transactions
        }
    except Exception as e:
        logger.error(f"Failed to get transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deposit/{deposit_id}", response_model=TransactionResponse)
async def delete_deposit(
    deposit_id: int,
    current_user: User = Depends(get_current_user)
):
    """입금 기록 삭제"""
    try:
        bot = get_bot()
        success = bot.capital.delete_deposit(deposit_id)

        if success:
            return TransactionResponse(
                success=True,
                message="입금 기록 삭제 완료"
            )
        else:
            raise HTTPException(status_code=404, detail="입금 기록을 찾을 수 없습니다")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete deposit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/withdrawal/{withdrawal_id}", response_model=TransactionResponse)
async def delete_withdrawal(
    withdrawal_id: int,
    current_user: User = Depends(get_current_user)
):
    """출금 기록 삭제"""
    try:
        bot = get_bot()
        success = bot.capital.delete_withdrawal(withdrawal_id)

        if success:
            return TransactionResponse(
                success=True,
                message="출금 기록 삭제 완료"
            )
        else:
            raise HTTPException(status_code=404, detail="출금 기록을 찾을 수 없습니다")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete withdrawal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
