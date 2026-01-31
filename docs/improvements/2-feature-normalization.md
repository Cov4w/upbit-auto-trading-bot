# 2. Feature Normalization (데이터 정규화)

## 📋 개요
- **우선순위:** 2위
- **효과:** ⭐⭐⭐⭐⭐
- **난이도:** 쉬움
- **소요 시간:** 1시간
- **예상 효과:** 정확도 +5~7%, 학습 속도 2배

## 🎯 목적
서로 다른 스케일의 특징들을 **동일한 범위**로 맞춰 AI가 공정하게 학습하도록 합니다.

## ❌ 현재 문제점
```python
# 스케일이 극단적으로 다른 데이터
RSI: 0 ~ 100
MACD: -50 ~ +50
BB Position: 0.0 ~ 1.0
Volume Ratio: 0.5 ~ 10.0
Price Change: -30% ~ +30%

→ AI가 큰 값(RSI, MACD)에 편향됨
→ 작은 값(BB Position)은 무시됨
```

## ✅ 해결 방법

### StandardScaler 사용
```python
from sklearn.preprocessing import StandardScaler

# 정규화기 생성 및 학습
scaler = StandardScaler()
scaler.fit(features)

# 데이터 변환
normalized_features = scaler.transform(features)

# 모든 특징이 평균 0, 표준편차 1
# RSI: -2.1 ~ +2.1
# MACD: -1.8 ~ +1.8
# BB Position: -1.5 ~ +1.5
```

## 📊 적용 전후 비교

### Before
```
RSI=70 (큼) → AI가 중요하게 판단
BB=0.2 (작음) → AI가 무시
```

### After
```
RSI=1.2 (정규화)
BB=1.1 (정규화)
→ 동등하게 평가
```

## 🔧 구현 위치
- **파일:** `data_manager.py`
- **클래스:** `ModelLearner`
- **메서드:** `train_initial_model()`, `predict()`

## 💾 저장 필요
```python
# Scaler를 모델과 함께 저장
joblib.dump({
    "model": self.model,
    "scaler": self.scaler,  # 추가!
    "metrics": self.metrics
}, self.model_path)
```

**이유:** 예측 시에도 동일한 Scaler를 사용해야 함

## 📈 예상 효과
1. **공정한 학습:** 모든 특징 동등하게 평가
2. **빠른 수렴:** 학습 속도 2배 향상
3. **정확도 향상:** 5~7% 포인트 상승
4. **안정성:** 예측 일관성 향상

## 💡 주의사항
- 학습 시 fit_transform(), 예측 시 transform()만 사용
- Scaler는 모델과 함께 저장/로드 필수
- 새 데이터도 동일한 Scaler로 변환해야 함

## 🔗 참고 자료
- Freqtrade: https://www.freqtrade.io/en/stable/freqai-feature-engineering/#building-the-data-pipeline
- Scikit-learn StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
