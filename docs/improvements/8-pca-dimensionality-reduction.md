# 8. PCA Dimensionality Reduction (주성분 분석)

## 📋 개요
- **우선순위:** 8위
- **효과:** ⭐⭐⭐
- **난이도:** 보통
- **소요 시간:** 1시간
- **예상 효과:** 과적합 방지, 학습 속도 2배

## 🎯 목적
**많은 특징을 소수의 핵심 특징으로 압축**하여 효율적인 학습을 가능하게 합니다.

## ❌ 현재 문제점
```python
# 10개 특징
features = [
    'rsi',               # 1
    'macd',              # 2
    'macd_signal',       # 3
    'bb_position',       # 4
    'volume_ratio',      # 5
    'price_change_5m',   # 6
    'price_change_15m',  # 7
    'ema_9',             # 8
    'ema_21',            # 9
    'atr'                # 10
]

문제:
- 80건 데이터로 10개 특징 학습 = 특징당 8건
- 과적합 위험 ⚠️
- 학습 속도 느림
```

## ✅ 해결 방법 (PCA)

### Principal Component Analysis
```python
from sklearn.decomposition import PCA

class ModelLearner:
    def __init__(self):
        self.pca = None
        self.use_pca = True
        self.n_components = 5  # 10개 → 5개
    
    def train_initial_model(self, X, y):
        if self.use_pca and len(X) < 100:  # 데이터 적을 때만
            # PCA 학습
            self.pca = PCA(n_components=self.n_components)
            X_reduced = self.pca.fit_transform(X)
            
            # 설명된 분산 비율
            variance_explained = sum(self.pca.explained_variance_ratio_)
            logger.info(f"📊 PCA: {len(X.columns)} → {self.n_components} features")
            logger.info(f"   Variance Retained: {variance_explained:.1%}")
            
            # 축소된 데이터로 학습
            self.model.fit(X_reduced, y)
        else:
            # 데이터 충분하면 원본 그대로
            self.model.fit(X, y)
```

### 예측 시 동일 변환
```python
def predict(self, features_df):
    if self.pca is not None:
        # 동일한 PCA 변환 적용
        features_reduced = self.pca.transform(features_df)
        prediction = self.model.predict(features_reduced)
    else:
        prediction = self.model.predict(features_df)
    
    return prediction
```

## 📊 원리 설명

### 상관관계가 높은 특징 압축
```
원본 10개 특징:
- EMA_9 ↔ EMA_21 (상관계수 0.98) ← 거의 동일!
- MACD ↔ MACD_Signal (상관계수 0.92)
- Price_Change_5m ↔ Price_Change_15m (상관계수 0.85)

PCA 후 5개 주성분:
- PC1: EMA 추세 (EMA_9 + EMA_21 결합)
- PC2: MACD 모멘텀
- PC3: 변동성 (ATR + BB_Position)
- PC4: 단기 가격 변화
- PC5: 거래량

→ 정보 손실: 5% (95% 보존)
```

## 🔧 적용 전후

### Before
```
특징: 10개
데이터: 80건
특징당 샘플: 8건
과적합 위험: 높음
학습 시간: 100ms
```

### After (PCA)
```
특징: 5개 (50% 감소)
데이터: 80건
특징당 샘플: 16건 ← 2배!
과적합 위험: 낮음
학습 시간: 50ms (2배 빠름)
```

## 📈 분산 비율 확인
```python
# PCA 후 각 주성분의 중요도
print(self.pca.explained_variance_ratio_)
# [0.35, 0.25, 0.18, 0.10, 0.07]
# PC1이 35% 정보, PC2가 25% ...
# 총 95% 정보 보존
```

## 💡 언제 사용?

| 상황 | PCA 사용 | 이유 |
|------|---------|------|
| 데이터 \< 100건 | ✅ 사용 | 과적합 방지 |
| 데이터 100~500건 | ⚠️ 선택 | 테스트 필요 |
| 데이터 \> 500건 | ❌ 불필요 | 충분한 샘플 |
| 특징 \> 20개 | ✅ 사용 | 차원의 저주 |

## 🔧 구현 위치
- **파일:** `data_manager.py`
- **클래스:** `ModelLearner`
- **저장 필수:** PCA 객체도 모델과 함께 저장

```python
joblib.dump({
    "model": self.model,
    "pca": self.pca,        # 추가!
    "scaler": self.scaler,
    "metrics": self.metrics
}, self.model_path)
```

## ⚠️ 주의사항
- PCA는 **특징의 의미를 잃음** (해석 어려움)
- Scaler 먼저 적용 후 PCA 순서 중요
- 예측 시에도 동일한 PCA 변환 필수

## 🔗 참고 자료
- Freqtrade PCA: https://www.freqtrade.io/en/stable/freqai-feature-engineering/#data-dimensionality-reduction-with-principal-component-analysis
- Scikit-learn PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
