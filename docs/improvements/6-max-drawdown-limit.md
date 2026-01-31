# 6. Max Drawdown Limit (최대 손실 한도)

## 📋 개요
- **우선순위:** 6위
- **효과:** ⭐⭐⭐⭐
- **난이도:** 쉬움
- **소요 시간:** 1시간
- **예상 효과:** 자금 보호, 심리적 안정

## 🎯 목적
**누적 손실이 한도에 도달하면 자동으로 거래를 중단**하여 자금을 보호합니다.

## ❌ 현재 문제점
```python
# 연속 손실 시나리오
거래 1: -420원 (-7%)
거래 2: -390원 (-7%)
거래 3: -360원 (-7%)
...
거래 10: -210원 (-7%)
누적 손실: -3,570원 (-60%!)

→ 자금 고갈 위험! 😱
```

## ✅ 해결 방법

### Max Drawdown 설정
```python
class TradingBot:
    def __init__(self):
        self.max_drawdown = 0.10  # -10% 손실 시 중단
        self.initial_balance = None
        self.peak_balance = None
    
    def start(self):
        balance = self.get_account_balance()['krw_balance']
        self.initial_balance = balance
        self.peak_balance = balance
        logger.info(f"💰 Initial Balance: {balance:,.0f} KRW")
    
    def _check_drawdown_limit(self):
        current_balance = self.get_account_balance()['krw_balance']
        
        # Peak 업데이트
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Drawdown 계산 (최고점 대비)
        drawdown = (self.peak_balance - current_balance) / self.peak_balance
        
        logger.debug(f"💹 Drawdown: {drawdown:.2%} (Limit: {self.max_drawdown:.0%})")
        
        if drawdown >= self.max_drawdown:
            logger.error("=" * 60)
            logger.error(f"🛑 MAX DRAWDOWN REACHED: {drawdown:.2%}")
            logger.error(f"   Peak Balance: {self.peak_balance:,.0f} KRW")
            logger.error(f"   Current Balance: {current_balance:,.0f} KRW")
            logger.error(f"   Loss: {self.peak_balance - current_balance:,.0f} KRW")
            logger.error("🛑 STOPPING ALL TRADING ACTIVITIES!")
            logger.error("=" * 60)
            
            # 모든 포지션 청산
            for ticker in list(self.positions.keys()):
                current_price = self.exchange.get_current_price(ticker)
                self._execute_sell(ticker, current_price, "Max Drawdown Exit")
            
            # 봇 중지
            self.stop()
            
            # Telegram 알림 (선택)
            # self.send_telegram_alert(f"🚨 Max Drawdown! Trading stopped.")
            
            return True
        
        return False
```

## 📊 실제 동작

### 시나리오: 연속 손실
```
시작 잔액: 100,000원 (peak)
목표: -10% (90,000원) 도달 시 중지

거래 1: 93,000원 → Drawdown: -7%
거래 2: 91,500원 → Drawdown: -8.5%
거래 3: 89,800원 → Drawdown: -10.2% 🛑

→ 거래 자동 중단!
→ 잔액 보호! 89,800원 유지
```

### vs 한도 없을 때
```
거래 3: 89,800원
거래 4: 83,250원
거래 5: 77,200원 ← -22.8% 손실! 😱
```

## 🔧 적용 위치
```python
def _trading_loop(self):
    while self.is_running:
        try:
            # 🛡️ Drawdown 체크 (가장 먼저!)
            if self._check_drawdown_limit():
                break
            
            # 포지션 체크
            for ticker in list(self.positions.keys()):
                self._check_exit_conditions(ticker)
            
            # 진입 체크
            ...
```

## 💰 권장 한도 설정

| 거래 스타일 | Drawdown 한도 | 설명 |
|------------|--------------|------|
| **보수적** | -5% | 안전 우선 |
| **중립** | **-10%** | **권장** ⭐ |
| **공격적** | -15% | 높은 리스크 |
| **위험** | -20%+ | 비추천 ⚠️ |

## 📈 심리적 효과
```
한도 없을 때:
"손실이 계속 늘어나는데... 언제 멈춰야 하지?" 😰
→ 감정적 판단
→ 더 큰 손실

한도 있을 때:
"10% 손실이면 자동으로 멈춘다" 😌
→ 심리적 안정
→ 규칙 기반 거래
```

## 💡 주의사항
- 초기 잔액 vs Peak 잔액 선택
  - 초기 기준: 절대 손실 제한
  - Peak 기준: 최고점 대비 손실 제한 (권장)
- 포지션 청산 로직 포함 필수
- Telegram/Discord 알림 연동 권장

## 🔗 참고 자료
- Risk Management: https://www.investopedia.com/articles/trading/05/020305.asp
