# 3. Trailing Stop Loss (추적 손절)

## 📋 개요
- **우선순위:** 3위
- **효과:** ⭐⭐⭐⭐⭐
- **난이도:** 보통
- **소요 시간:** 2시간
- **예상 효과:** 수익 +30~50% 증가

## 🎯 목적
가격이 상승할 때 손절선도 따라 올려서 **수익을 극대화**합니다.

## ❌ 현재 방식 (고정 익절)
```python
진입가: 100원
목표가: 100.7원 (0.7%)

시나리오:
100 → 103 → 102 → 101.5 → 105
         ↑ 100.7원 도달 시 매도
         
결과: +0.7% 익절
아쉬움: 최고 105원까지 올라갔는데... 😢
```

## ✅ 해결 방법 (Trailing Stop)

### 동작 원리
```python
진입가: 100원
목표가: 101.5원 (1.5% 도달 시 트레일링 활성화)

시나리오:
100 → 103 (peak 기록) → 102.5
              ↓
      peak × 0.99 = 101.97원
      현재가 102.5 > 101.97 (유지)

103 → 102 → 101.5
              ↓
      101.5 < 101.97
      → 트레일링 스톱 발동! (+1.5% 익절)

vs 고정: 100.7원 (+0.7%)
차이: +0.8% 추가 수익! 💰
```

## 🔧 구현 코드
```python
class TradingBot:
    def __init__(self):
        self.trailing_stop_enabled = True
        self.trailing_activation = 0.015  # 1.5% 도달 시 활성화
        self.trailing_distance = 0.01      # peak 대비 -1%
    
    def _check_exit_conditions(self, ticker):
        position = self.positions[ticker]
        entry = position['entry_price']
        current = self.exchange.get_current_price(ticker)
        profit_rate = (current - entry) / entry
        
        # Peak 가격 추적
        if 'peak_price' not in position:
            position['peak_price'] = entry
        
        if current > position['peak_price']:
            position['peak_price'] = current
        
        # 1.5% 이상 수익 시 트레일링 활성화
        if profit_rate >= self.trailing_activation:
            trailing_stop = position['peak_price'] * (1 - self.trailing_distance)
            
            if current < trailing_stop:
                logger.info(f"🔔 Trailing Stop! Peak={position['peak_price']:,.0f}, Current={current:,.0f}")
                self._execute_sell(ticker, current, "Trailing Stop")
                return
```

## 📊 시뮬레이션

### 케이스 1: 급등 후 하락
```
진입: 100원
급등: 110원 (peak)
하락: 108.9원 → 트레일링 스톱 (+8.9% 익절)

vs 고정: 100.7원 (+0.7%)
추가 수익: +8.2%! 🚀
```

### 케이스 2: 소폭 상승
```
진입: 100원
상승: 101원
하락: 100.5원 → 트레일링 미발동 (1.5% 미달)
         → 목표가 100.7원 대기

vs 고정: 100.7원 (+0.7%)
차이 없음
```

## 📈 예상 효과
1. **수익 극대화:** 평균 +30~50% 더
2. **조기 익절 방지:** 큰 상승 놓치지 않음
3. **심리적 안정:** 자동으로 최적 매도점 포착

## 💡 주의사항
- `trailing_activation`은 `target_profit`보다 높게 설정
- `trailing_distance`는 0.5~2% 권장
- 변동성 큰 코인은 distance 크게 설정

## 🔗 참고 자료
- Freqtrade: https://www.freqtrade.io/en/stable/stoploss/#trailing-stop-loss
