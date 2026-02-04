#!/usr/bin/env python3
"""
동적 티커 관리 테스트 (누적 + 즉시 제거)
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.trading_bot import TradingBot

def test_dynamic_ticker_management():
    """동적 티커 관리 로직 테스트 (누적 방식)"""
    print("=" * 80)
    print("🧪 Dynamic Ticker Management Test (Cumulative + Immediate Removal)")
    print("=" * 80)

    # TradingBot 인스턴스 생성
    bot = TradingBot()

    # 초기 상태
    print(f"\n📊 Initial State:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Origin Ranges: {bot.ticker_origin_range}")

    # 시나리오 1: 범위 0-50 스캔 - BTC, ETH, XRP, ADA, SOL 추가
    print("\n" + "=" * 80)
    print("시나리오 1: 범위 0-50 스캔 - Top 5 추가")
    print("=" * 80)

    bot.coin_selector.scan_index = 50
    bot.coin_selector.batch_size = 50

    mock_recs_1 = [
        {'ticker': 'BTC', 'score': 95.0, 'confidence': 0.85, 'features': {'rsi': 65.0}},
        {'ticker': 'ETH', 'score': 90.0, 'confidence': 0.80, 'features': {'rsi': 60.0}},
        {'ticker': 'XRP', 'score': 85.0, 'confidence': 0.75, 'features': {'rsi': 55.0}},
        {'ticker': 'ADA', 'score': 80.0, 'confidence': 0.70, 'features': {'rsi': 50.0}},
        {'ticker': 'SOL', 'score': 75.0, 'confidence': 0.65, 'features': {'rsi': 45.0}},
    ]

    bot._manage_tickers_dynamically(mock_recs_1)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")

    # 시나리오 2: 범위 50-100 스캔 - CTC, MATIC, AVAX, DOT, LINK 추가 (누적)
    print("\n" + "=" * 80)
    print("시나리오 2: 범위 50-100 스캔 - Top 5 추가 (누적됨)")
    print("=" * 80)

    bot.coin_selector.scan_index = 100

    mock_recs_2 = [
        {'ticker': 'CTC', 'score': 92.0, 'confidence': 0.82, 'features': {'rsi': 62.0}},
        {'ticker': 'MATIC', 'score': 88.0, 'confidence': 0.78, 'features': {'rsi': 58.0}},
        {'ticker': 'AVAX', 'score': 83.0, 'confidence': 0.73, 'features': {'rsi': 53.0}},
        {'ticker': 'DOT', 'score': 78.0, 'confidence': 0.68, 'features': {'rsi': 48.0}},
        {'ticker': 'LINK', 'score': 74.0, 'confidence': 0.64, 'features': {'rsi': 44.0}},
    ]

    bot._manage_tickers_dynamically(mock_recs_2)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")
    print(f"   ℹ️ 이전 범위(0-50) 코인들도 유지됨")

    # 시나리오 3: 범위 100-150 스캔 - 또 다른 5개 추가 (계속 누적)
    print("\n" + "=" * 80)
    print("시나리오 3: 범위 100-150 스캔 - Top 5 추가 (계속 누적)")
    print("=" * 80)

    bot.coin_selector.scan_index = 150

    mock_recs_3 = [
        {'ticker': 'UNI', 'score': 90.0, 'confidence': 0.80, 'features': {'rsi': 60.0}},
        {'ticker': 'ATOM', 'score': 85.0, 'confidence': 0.75, 'features': {'rsi': 55.0}},
        {'ticker': 'SAND', 'score': 80.0, 'confidence': 0.70, 'features': {'rsi': 50.0}},
        {'ticker': 'MANA', 'score': 75.0, 'confidence': 0.65, 'features': {'rsi': 45.0}},
        {'ticker': 'AXS', 'score': 70.0, 'confidence': 0.60, 'features': {'rsi': 40.0}},
    ]

    bot._manage_tickers_dynamically(mock_recs_3)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")
    print(f"   ℹ️ 모든 범위의 Top 5가 누적됨")

    # 시나리오 4: 범위 0-50 재스캔 - XRP 이탈 (즉시 제거)
    print("\n" + "=" * 80)
    print("시나리오 4: 범위 0-50 재스캔 - XRP 이탈 → 즉시 제거")
    print("=" * 80)

    bot.coin_selector.scan_index = 50

    mock_recs_4 = [
        {'ticker': 'BTC', 'score': 95.0, 'confidence': 0.85, 'features': {'rsi': 65.0}},
        {'ticker': 'ETH', 'score': 90.0, 'confidence': 0.80, 'features': {'rsi': 60.0}},
        {'ticker': 'ADA', 'score': 85.0, 'confidence': 0.75, 'features': {'rsi': 55.0}},
        {'ticker': 'SOL', 'score': 80.0, 'confidence': 0.70, 'features': {'rsi': 50.0}},
        {'ticker': 'DOGE', 'score': 75.0, 'confidence': 0.65, 'features': {'rsi': 45.0}},  # 신규
    ]

    bot._manage_tickers_dynamically(mock_recs_4)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")
    print(f"   ℹ️ XRP 제거됨, DOGE 추가됨")

    # 시나리오 5: 범위 50-100 재스캔 - CTC, MATIC 이탈 (즉시 제거)
    print("\n" + "=" * 80)
    print("시나리오 5: 범위 50-100 재스캔 - CTC, MATIC 이탈 → 즉시 제거")
    print("=" * 80)

    bot.coin_selector.scan_index = 100

    mock_recs_5 = [
        {'ticker': 'AVAX', 'score': 90.0, 'confidence': 0.80, 'features': {'rsi': 60.0}},
        {'ticker': 'DOT', 'score': 85.0, 'confidence': 0.75, 'features': {'rsi': 55.0}},
        {'ticker': 'LINK', 'score': 80.0, 'confidence': 0.70, 'features': {'rsi': 50.0}},
        {'ticker': 'ALGO', 'score': 75.0, 'confidence': 0.65, 'features': {'rsi': 45.0}},  # 신규
        {'ticker': 'XTZ', 'score': 70.0, 'confidence': 0.60, 'features': {'rsi': 40.0}},  # 신규
    ]

    bot._manage_tickers_dynamically(mock_recs_5)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")
    print(f"   ℹ️ CTC, MATIC 제거됨, ALGO, XTZ 추가됨")

    # 시나리오 6: ETH에 포지션 추가 후 이탈 (제거 방지)
    print("\n" + "=" * 80)
    print("시나리오 6: ETH에 포지션 추가 후 이탈 → 제거 방지")
    print("=" * 80)

    bot.positions['ETH'] = {
        'entry_price': 3000,
        'amount': 0.1,
        'entry_time': '2026-02-04 10:00:00'
    }
    print(f"   ✅ Added ETH position: {bot.positions['ETH']}")

    bot.coin_selector.scan_index = 50

    mock_recs_6 = [
        {'ticker': 'BTC', 'score': 95.0, 'confidence': 0.85, 'features': {'rsi': 65.0}},
        {'ticker': 'ADA', 'score': 90.0, 'confidence': 0.80, 'features': {'rsi': 60.0}},
        {'ticker': 'SOL', 'score': 85.0, 'confidence': 0.75, 'features': {'rsi': 55.0}},
        {'ticker': 'DOGE', 'score': 80.0, 'confidence': 0.70, 'features': {'rsi': 50.0}},
        {'ticker': 'SHIB', 'score': 75.0, 'confidence': 0.65, 'features': {'rsi': 45.0}},  # 신규
    ]

    bot._manage_tickers_dynamically(mock_recs_6)
    print(f"\n📊 After Update:")
    print(f"   Tickers: {bot.tickers}")
    print(f"   Total Watch List: {len(bot.tickers)} coins")
    print(f"   ℹ️ ETH는 포지션이 있어서 제거되지 않음")

    # 최종 결과
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    print(f"Final Tickers: {bot.tickers}")
    print(f"Total Watch List: {len(bot.tickers)} coins")
    print(f"Origin Ranges: {bot.ticker_origin_range}")
    print(f"Active Positions: {list(bot.positions.keys())}")
    print("\n💡 감시 대상은 계속 누적되며, 모든 코인을 실시간으로 분석합니다!")

if __name__ == "__main__":
    test_dynamic_ticker_management()
