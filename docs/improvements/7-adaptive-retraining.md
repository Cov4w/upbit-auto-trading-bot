# 7. Adaptive Retraining (적응형 재학습)

## 📋 개요
- **우선순위:** 7위
- **효과:** ⭐⭐⭐⭐
- **난이도:** 보통
- **소요 시간:** 2시간
- **예상 효과:** 불필요한 재학습 방지, 시장 변화 빠른 적응

## 🎯 목적
**정확도 하락 또는 시간 경과 시 자동으로 재학습**하여 시장 변화에 적응합니다.

## ❌ 현재 방식 (고정 주기)
```python
# 10건마다 무조건 재학습
if trade_count % 10 == 0:
    retrain_model()

문제점:
- 정확도가 높아도 재학습 (시간 낭비)
- 정확도가 급락해도 10건 대기 (손실 누적)
```

## ✅ 해결 방법 (적응형)

### 1. 정확도 기반 재학습
```python
class ModelLearner:
    def __init__(self):
        self.accuracy_threshold = 0.05  # 5%p 하락 시
        self.last_accuracy = None
        self.performance_window = []  # 최근 20거래 승률
    
    def should_retrain(self):
        if not self.last_accuracy:
            return False
        
        current_accuracy = self.metrics.get('accuracy', 0)
        
        # 정확도 5%p 이상 하락
        if current_accuracy < self.last_accuracy - self.accuracy_threshold:
            logger.warning(
                f"📉 Accuracy dropped: {self.last_accuracy:.2%} → {current_accuracy:.2%}"
            )
            return True
        
        return False
```

### 2. 실전 승률 기반 재학습
```python
def check_performance_degradation(self):
    # 최근 20거래 승률
    recent_trades = self.memory.get_recent_trades(limit=20)
    recent_win_rate = sum(t['is_profitable'] for t in recent_trades) / len(recent_trades)
    
    # 전체 승률 대비 10%p 이상 하락
    overall_win_rate = self.memory.get_overall_win_rate()
    
    if recent_win_rate < overall_win_rate - 0.10:
        logger.warning(
            f"⚠️ Recent performance drop: {recent_win_rate:.1%} (Overall: {overall_win_rate:.1%})"
        )
        return True
    
    return False
```

### 3. 시간 기반 재학습
```python
def time_based_retrain(self):
    from datetime import datetime, timedelta
    
    if not hasattr(self, 'last_train_time'):
        self.last_train_time = datetime.now()
        return False
    
    hours_since_train = (datetime.now() - self.last_train_time).total_seconds() / 3600
    
    # 24시간마다 재학습
    if hours_since_train >= 24:
        logger.info(f"⏰ {hours_since_train:.1f} hours since last training")
        return True
    
    return False
```

### 4. 통합 재학습 로직
```python
def adaptive_retrain_check(self):
    reasons = []
    
    # 1. 정확도 하락 체크
    if self.learner.should_retrain():
        reasons.append("Accuracy Degradation")
    
    # 2. 실전 성능 하락 체크
    if self.check_performance_degradation():
        reasons.append("Performance Drop")
    
    # 3. 시간 경과 체크
    if self.learner.time_based_retrain():
        reasons.append("Time Elapsed (24h)")
    
    # 4. 최소 데이터 체크
    trade_count = len(self.memory.get_all_trades())
    min_trades_since_last = 30
    
    if trade_count < self.last_retrain_count + min_trades_since_last:
        return False  # 데이터 부족
    
    if reasons:
        logger.info(f"🔄 Retraining triggered by: {', '.join(reasons)}")
        self._retrain_model()
        self.last_retrain_count = trade_count
        return True
    
    return False
```

## 📊 적용 전후 비교

### Before (고정 주기)
```
0~10건: 정확도 60% (높음) → 재학습 (불필요)
11~20건: 정확도 45% (낮음) → 대기 중...
21건: 재학습 (너무 늦음, 손실 누적)
```

### After (적응형)
```
0~12건: 정확도 60% → 60% 유지 (재학습 안 함)
13건: 정확도 급락 54% (-6%p) → 즉시 재학습! ⚡
14~25건: 정확도 58% 회복 → 안정
```

## 🔧 구현 위치
- **파일:** `trading_bot.py`, `data_manager.py`
- **메서드:** `_trading_loop()` 내부에 추가

```python
def _trading_loop(self):
    while self.is_running:
        try:
            # 적응형 재학습 체크
            self.adaptive_retrain_check()
            
            # 기존 로직
            ...
```

## 📈 기대 효과
1. **불필요한 재학습 방지:** CPU/시간 절약
2. **빠른 적응:** 시장 변화 즉시 감지
3. **손실 최소화:** 성능 하락 즉시 대응
4. **안정성:** 과도한 재학습 방지

## 💡 권장 임계값

| 항목 | 권장값 | 설명 |
|------|--------|------|
| **정확도 하락** | -5%p | 너무 민감 X |
| **승률 하락** | -10%p | 단기 변동 고려 |
| **시간 경과** | 24시간 | 시장 변화 반영 |
| **최소 데이터** | 30건 | 통계적 신뢰도 |

## 🔗 참고 자료
- Freqtrade Adaptive Training: https://www.freqtrade.io/en/stable/freqai-running/#live-deployments
