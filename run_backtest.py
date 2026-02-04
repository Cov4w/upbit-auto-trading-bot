#!/usr/bin/env python3
"""
백테스팅 직접 실행 스크립트
서버 없이 독립적으로 백테스팅을 실행합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.trading_bot import TradingBot

def main():
    print("=" * 60)
    print("🚀 백테스팅 시작")
    print("=" * 60)

    # TradingBot 인스턴스 생성
    print("\n📊 TradingBot 초기화 중...")
    bot = TradingBot()

    # 백테스팅 실행 (동기 모드)
    print("\n🎮 백테스팅 실행 중... (멀티 코인, 200일)")
    print("⏳ 예상 소요 시간: 1-3분\n")

    result = bot.run_backtest(
        tickers=None,      # 자동으로 거래 내역에서 선택
        days=200,          # 200일 백테스팅
        async_mode=False   # 동기 모드 (결과 대기)
    )

    # 결과 출력
    if result['status'] == 'completed' and result.get('results'):
        results = result['results']
        print("\n" + "=" * 60)
        print("✅ 백테스팅 완료!")
        print("=" * 60)

        if results.get('total_trades', 0) > 0:
            print(f"\n📊 테스트한 코인: {', '.join(results.get('tested_coins', []))}")
            print(f"총 거래 수: {results['total_trades']}건")
            print(f"승률: {results['win_rate']*100:.2f}%")
            print(f"총 수익률: {results['total_return']*100:+.2f}%")
            print(f"최종 자본: {results['final_capital']:,.0f}원")
            print(f"최대 낙폭(MDD): {results['max_drawdown']*100:.2f}%")
            print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

            # 평가
            if results['win_rate'] >= 0.45 and results['profit_loss_ratio'] >= 1.5:
                print("\n✅ 전략 검증 성공! 실전 투입 가능 수준입니다.")
            else:
                print("\n⚠️ 전략 개선 필요:")
                if results['win_rate'] < 0.45:
                    print(f"   - 승률 {results['win_rate']*100:.1f}% < 목표 45%")
                if results['profit_loss_ratio'] < 1.5:
                    print(f"   - 손익비 {results['profit_loss_ratio']:.2f} < 목표 1.5")
        else:
            print("\n⚠️ 거래가 발생하지 않았습니다 (매수 신호 없음)")
    else:
        print("\n❌ 백테스팅 실패")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
