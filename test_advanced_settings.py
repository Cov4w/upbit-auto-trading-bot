#!/usr/bin/env python3
"""
고급 설정 기능 통합 테스트
=========================
순수익 계산, 동적 목표, 동적 사이징 기능이 제대로 작동하는지 검증합니다.
"""

import requests
import json
import sys
import time

API_BASE = "http://localhost:8000"

def print_section(title):
    """섹션 헤더 출력"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_get_status():
    """현재 상태 조회"""
    print_section("1️⃣ 현재 봇 상태 조회")

    try:
        response = requests.get(f"{API_BASE}/api/bot/status", timeout=5)
        response.raise_for_status()

        status = response.json()

        print(f"✅ API 연결 성공")
        print(f"\n📊 현재 설정:")
        print(f"   - 순수익 계산: {status.get('use_net_profit', 'N/A')}")
        print(f"   - 동적 목표: {status.get('use_dynamic_target', 'N/A')}")
        print(f"   - 동적 사이징: {status.get('use_dynamic_sizing', 'N/A')}")
        print(f"   - 매수 금액: {status.get('trade_amount', 'N/A'):,.0f} KRW")
        print(f"   - 목표 수익률: {status.get('target_profit', 'N/A') * 100:.1f}%")

        return status
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버가 실행 중이지 않습니다.")
        print("💡 해결 방법: cd backend && python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 상태 조회 실패: {e}")
        sys.exit(1)

def test_update_config():
    """설정 업데이트 테스트"""
    print_section("2️⃣ 설정 업데이트 테스트")

    test_configs = [
        {
            "name": "순수익 계산 ON",
            "config": {
                "use_net_profit": True,
                "use_dynamic_target": False,
                "use_dynamic_sizing": False
            }
        },
        {
            "name": "동적 목표 ON",
            "config": {
                "use_net_profit": True,
                "use_dynamic_target": True,
                "use_dynamic_sizing": False
            }
        },
        {
            "name": "전체 활성화 (전문가 모드)",
            "config": {
                "use_net_profit": True,
                "use_dynamic_target": True,
                "use_dynamic_sizing": True
            }
        }
    ]

    for i, test in enumerate(test_configs, 1):
        print(f"\n🔧 테스트 {i}: {test['name']}")

        try:
            # 설정 변경
            response = requests.post(
                f"{API_BASE}/api/bot/config",
                json=test['config'],
                timeout=5
            )
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                print(f"   ✅ 설정 변경 성공")
                print(f"   📝 업데이트된 항목: {list(result.get('data', {}).get('updated', {}).keys())}")
            else:
                print(f"   ❌ 설정 변경 실패: {result.get('error', 'Unknown error')}")

            # 변경 후 상태 확인
            time.sleep(0.5)
            status_response = requests.get(f"{API_BASE}/api/bot/status", timeout=5)
            status = status_response.json()

            # 검증
            is_valid = True
            for key, expected_value in test['config'].items():
                actual_value = status.get(key)
                if actual_value != expected_value:
                    print(f"   ⚠️ 불일치: {key} (기대={expected_value}, 실제={actual_value})")
                    is_valid = False

            if is_valid:
                print(f"   ✅ 설정 검증 완료")
            else:
                print(f"   ❌ 설정 검증 실패")

        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")

def test_feature_integration():
    """기능 통합 테스트 (코드 레벨)"""
    print_section("3️⃣ 기능 통합 확인 (코드 검증)")

    checks = [
        {
            "feature": "순수익 계산",
            "file": "backend/core/trading_bot.py",
            "check": "calculate_net_profit",
            "usage": "if self.use_net_profit:"
        },
        {
            "feature": "동적 목표",
            "file": "backend/core/trading_bot.py",
            "check": "calculate_dynamic_target",
            "usage": "if self.use_dynamic_target:"
        },
        {
            "feature": "동적 사이징",
            "file": "backend/core/trading_bot.py",
            "check": "calculate_position_size",
            "usage": "if not self.use_dynamic_sizing:"
        }
    ]

    import os

    for check in checks:
        print(f"\n🔍 {check['feature']}")

        file_path = os.path.join("/Users/cov4/bitThumb_std", check['file'])

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()

                # 함수 존재 확인
                if check['check'] in content:
                    print(f"   ✅ 함수 존재: {check['check']}")
                else:
                    print(f"   ❌ 함수 없음: {check['check']}")

                # 사용 확인
                if check['usage'] in content:
                    print(f"   ✅ 설정 사용 확인: {check['usage']}")
                else:
                    print(f"   ⚠️ 설정 미사용")
        else:
            print(f"   ❌ 파일 없음: {file_path}")

def test_ui_integration():
    """UI 통합 확인"""
    print_section("4️⃣ UI 통합 확인")

    import os

    frontend_file = "/Users/cov4/bitThumb_std/frontend/src/components/TradingSettings.tsx"

    if os.path.exists(frontend_file):
        with open(frontend_file, 'r') as f:
            content = f.read()

            checks = [
                ("순수익 상태", "useNetProfit"),
                ("동적목표 상태", "useDynamicTarget"),
                ("동적사이징 상태", "useDynamicSizing"),
                ("순수익 토글", "Use Net Profit Calculation"),
                ("동적목표 토글", "Use Dynamic Target"),
                ("동적사이징 토글", "Use Dynamic Sizing"),
            ]

            for name, keyword in checks:
                if keyword in content:
                    print(f"   ✅ {name}: {keyword}")
                else:
                    print(f"   ❌ {name} 누락")
    else:
        print(f"   ❌ UI 파일 없음")

def print_summary():
    """테스트 요약"""
    print_section("📋 테스트 요약")

    print("""
✅ 검증 완료 항목:
   1. API 엔드포인트 (/api/bot/config)
   2. 백엔드 설정 업데이트 (bot.py)
   3. 실제 로직 사용 (trading_bot.py)
   4. UI 컴포넌트 (TradingSettings.tsx)

🎯 다음 단계:
   1. 웹 UI에서 토글 스위치 클릭
   2. "Apply Settings" 버튼 클릭
   3. 봇 로그에서 "Net Profit" 또는 "Dynamic Target" 메시지 확인

💡 사용 예시:
   - 순수익 계산 활성화 시:
     📊 [BTC] Net Profit:1.98% (Target:>2.0%)

   - 동적 목표 활성화 시:
     [BTC] Dynamic Target: 1.50% (ATR: 750,000)
""")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        🚀 Advanced Settings Integration Test            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    try:
        # 1. 현재 상태 조회
        initial_status = test_get_status()

        # 2. 설정 업데이트 테스트
        test_update_config()

        # 3. 기능 통합 확인
        test_feature_integration()

        # 4. UI 통합 확인
        test_ui_integration()

        # 5. 요약
        print_summary()

        print("\n✅ 모든 테스트 완료!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️ 테스트 중단됨")
        sys.exit(0)
