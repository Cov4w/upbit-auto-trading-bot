# 9. Dynamic Position Sizing (동적 포지션 크기)

## 📋 개요
- **우선순위:** 9위
- **효과:** ⭐⭐⭐⭐
- **난이도:** 어려움
- **소요 시간:** 3시간
- **예상 효과:** 복리 효과 극대화, 리스크 관리 개선

## 🎯 목적
**확신도와 잔액에 따라 투자 금액을 동적으로 조절**하여 수익을 극대화합니다.

## ❌ 현재 방식 (고정 금액)
```python
trade_amount = 6,000원 (항상 동일)

문제점:
- 확신도 90%일 때도 6,000원
- 확신도 70%일 때도 6,000원
→ 기회 손실 😢
```

## ✅ 해결 방법 (Kelly Criterion)

### Kelly Criterion 공식
```
f* = (p × b - q) / b

f* = 최적 투자 비율
p = 승률 (Win Rate)
q = 패율 (1 - p)
b = 승률 시 수익 / 패율 시 손실
```

### 구현 코드
```python
class TradingBot:
    def calculate_position_size(self, ticker, confidence):
        # 최근 성과 분석
        stats = self.memory.get_statistics()
        win_rate = stats.get('win_rate', 0.5)      # p
        avg_win = stats.get('avg_profit', 0.007)   # 0.7%
        avg_loss = abs(stats.get('avg_loss', -0.007))  # 0.7%
        
        # Kelly Criterion
        if avg_win > 0:
            b = avg_win / avg_loss  # 승률 대 패율 비율
            kelly_fraction = (win_rate * b - (1 - win_rate)) / b
        else:
            kelly_fraction = 0
        
        # Kelly 값 제한 (너무 크면 위험)
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 최대 25%
        
        # 현재 잔액
        balance = self.get_account_balance()['krw_balance']
        
        # AI 확신도 반영
        adjusted_kelly = kelly_fraction * confidence
        
        # 최종 금액 계산
        optimal_amount = balance * adjusted_kelly
        
        # 제한 설정
        min_amount = 5000   # 최소 5,000원
        max_amount = balance * 0.3  # 최대 30%
        
        final_amount = max(min_amount, min(optimal_amount, max_amount))
        
        logger.info(f"💰 Position Sizing: {final_amount:,.0f} KRW")
        logger.info(f"   Kelly: {kelly_fraction:.1%}, Confidence: {confidence:.1%}")
        
        return final_amount
```

## 📊 실제 예시

### 케이스 1: 높은 확신도
```
잔액: 100,000원
승률: 58.8%
평균 수익: 0.7%
평균 손실: 0.7%
Kelly: 17.6%

AI 확신도: 95%
조정 Kelly: 17.6% × 0.95 = 16.7%
투자 금액: 100,000 × 16.7% = 16,700원

vs 고정: 6,000원
차이: +178% 더 투자! 🚀
```

### 케이스 2: 낮은 확신도
```
같은 조건
AI 확신도: 72%
조정 Kelly: 17.6% × 0.72 = 12.7%
투자 금액: 100,000 × 12.7% = 12,700원

vs 확신도 95%: 16,700원
차이: -24% (리스크 감소)
```

### 케이스 3: 잔액 증가
```
잔액: 200,000원 (이익 누적)
켈리: 17.6%
확신도: 90%
투자 금액: 200,000 × 17.6% × 0.9 = 31,680원

→ 복리 효과! 💰
```

## 📈 복리 효과 시뮬레이션

### 고정 금액 (6,000원)
```
Day 1: 6,000원 투자 → +420원 → 잔액 100,420원
Day 2: 6,000원 투자 → +420원 → 잔액 100,840원
...
Day 30: 총 수익 +12,600원 (선형 증가)
```

### 동적 금액 (Kelly)
```
Day 1: 16,700원 투자 → +1,169원 → 잔액 101,169원
Day 2: 16,906원 투자 → +1,183원 → 잔액 102,352원
...
Day 30: 총 수익 +39,780원 (지수 증가) 🚀
```

**차이: +216% 더 벌림!**

## 🛡️ 리스크 관리

### Half-Kelly (안전 버전)
```python
# Kelly 값의 50%만 사용 (보수적)
conservative_kelly = kelly_fraction * 0.5
```

**이유:**
- Kelly는 이론적 최적값
- 실전에서는 과도하게 공격적일 수 있음
- Half-Kelly는 안정성 유지하며 80% 수익 달성

### 최대/최소 제한
```python
# 최소: 5,000원 (거래소 최소 주문)
# 최대: 잔액의 30% (분산 투자)
final_amount = max(5000, min(optimal_amount, balance * 0.3))
```

## 🔧 구현 위치
- **파일:** `trading_bot.py`
- **메서드:** `_execute_buy()` 내부 수정

```python
def _execute_buy(self, ticker, features, confidence):
    # 동적 금액 계산
    trade_amount = self.calculate_position_size(ticker, confidence)
    
    # 기존 로직에 적용
    current_price = self.exchange.get_current_price(ticker)
    buy_amount = trade_amount / current_price
    ...
```

## 💡 주의사항
- 승률/수익률 통계가 안정될 때까지(50건+) 고정 금액 사용
- Kelly 값이 음수면 거래하지 말 것 (기대값 -이면)
- 백테스팅으로 최적 비율 조정 필요

## 📊 권장 설정

| 스타일 | Kelly 비율 | 최대 비율 |
|--------|-----------|----------|
| **보수적** | Half-Kelly (50%) | 20% |
| **중립** | Full-Kelly (100%) | 30% |
| **공격적** | 1.5x Kelly | 50% |

## 🔗 참고 자료
- Kelly Criterion: https://en.wikipedia.org/wiki/Kelly_criterion
- Position Sizing: https://www.investopedia.com/articles/trading/09/determine-position-size.asp
