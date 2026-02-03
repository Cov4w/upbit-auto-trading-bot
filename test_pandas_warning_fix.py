#!/usr/bin/env python3
"""
Pandas SettingWithCopyWarning 수정 검증
========================================
fillna() 경고가 수정되었는지 확인합니다.
"""

import warnings
import sys
import os
import pandas as pd
import numpy as np

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, '/Users/cov4/bitThumb_std/backend')

def test_model_learning():
    """모델 학습 시 경고 확인"""
    print("=" * 60)
    print("  📊 모델 학습 테스트 (Pandas 경고 확인)")
    print("=" * 60)

    # Pandas 경고를 에러로 변환 (경고 발생 시 즉시 중단)
    warnings.filterwarnings('error', category=pd.errors.SettingWithCopyWarning)

    try:
        from core.data_manager import TradeMemory, ModelLearner

        print("\n1️⃣ TradeMemory 초기화...")
        memory = TradeMemory()
        print("   ✅ 성공")

        print("\n2️⃣ ModelLearner 초기화...")
        learner = ModelLearner()
        print("   ✅ 성공")

        print("\n3️⃣ 학습 데이터 생성 (테스트용)...")
        # 테스트 데이터 생성
        X = pd.DataFrame({
            'rsi': np.random.uniform(30, 70, 50),
            'macd': np.random.uniform(-1, 1, 50),
            'macd_signal': np.random.uniform(-1, 1, 50),
            'bb_position': np.random.uniform(0, 1, 50),
            'volume_ratio': np.random.uniform(0.5, 2, 50),
            'price_change_5m': np.random.uniform(-0.02, 0.02, 50),
            'price_change_15m': np.random.uniform(-0.05, 0.05, 50),
            'ema_9': np.random.uniform(10000, 50000, 50),
            'ema_21': np.random.uniform(10000, 50000, 50),
            'atr': np.random.uniform(100, 1000, 50),
            'hour_of_day': np.random.randint(0, 24, 50),
            'day_of_week': np.random.randint(0, 7, 50),
            'rsi_change': np.random.uniform(-5, 5, 50),
            'volume_trend': np.random.uniform(-0.3, 0.3, 50),
            'rsi_prev_5m': np.random.uniform(30, 70, 50),
            'bb_position_prev_5m': np.random.uniform(0, 1, 50),
        })

        # 일부 NaN 값 추가 (fillna 테스트용)
        X.iloc[0, 0] = np.nan
        X.iloc[5, 3] = np.nan
        X.iloc[10, 7] = np.nan

        y = pd.Series(np.random.choice([0, 1, 2], 50))

        print(f"   ✅ 데이터 생성: {len(X)}개 샘플, {len(X.columns)}개 특징")
        print(f"   ℹ️  NaN 개수: {X.isna().sum().sum()}개")

        print("\n4️⃣ 모델 학습 실행 (경고 감지 중)...")
        learner.train_initial_model(X, y)
        print("   ✅ 학습 완료 - 경고 없음!")

        print("\n5️⃣ 예측 테스트 (경고 감지 중)...")
        test_features = pd.DataFrame([{
            'rsi': 35.0,
            'macd': 0.5,
            'macd_signal': 0.3,
            'bb_position': 0.2,
            'volume_ratio': 1.2,
            'price_change_5m': 0.01,
            'price_change_15m': 0.02,
            'ema_9': 25000,
            'ema_21': 24500,
            'atr': 500,
            'hour_of_day': 14,
            'day_of_week': 2,
            'rsi_change': 2.5,
            'volume_trend': 0.1,
            'rsi_prev_5m': 32.5,
            'bb_position_prev_5m': 0.25,
        }])

        # 일부 NaN 추가 (fillna 테스트)
        test_features.iloc[0, 1] = np.nan

        prediction, confidence = learner.predict(test_features)
        print(f"   ✅ 예측 완료 - 경고 없음!")
        print(f"   📊 결과: Class {prediction}, 확신도 {confidence:.2%}")

        print("\n" + "=" * 60)
        print("  ✅ 모든 테스트 통과! Pandas 경고 수정 완료!")
        print("=" * 60)

        return True

    except pd.errors.SettingWithCopyWarning as e:
        print(f"\n❌ Pandas 경고 발생!")
        print(f"   에러: {e}")
        print("\n💡 수정 필요: inplace=True를 제거하고 재할당하세요.")
        return False

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🔧 Pandas SettingWithCopyWarning Fix Test          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    success = test_model_learning()

    if success:
        print("\n✅ 수정 완료! 백엔드 재시작 시 경고가 사라집니다.\n")
        sys.exit(0)
    else:
        print("\n❌ 추가 수정이 필요합니다.\n")
        sys.exit(1)
