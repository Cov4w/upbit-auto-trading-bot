# 5. Emergency Exit (긴급 청산)

## 📋 개요
- **우선순위:** 5위
- **효과:** ⭐⭐⭐⭐
- **난이도:** 보통
- **소요 시간:** 2시간
- **예상 효과:** 플래시 크래시 대응, 큰 손실 방지

## 🎯 목적
급격한 시장 변동 시 **즉시 청산**하여 큰 손실을 방지합니다.

## ❌ 현재 문제점
```python
# 정상 손절: -0.7%
# 급락 시나리오:
100원 → 95원 (-5% 급락) → 손절선 대기 중
→ 실제 매도: 94원 (-6%)
→ 예상보다 큰 손실! 😱
```

## ✅ 해결 방법

### 1. 급락 감지 (Flash Crash)
```python
def _check_flash_crash(self, ticker):
    # 1분 전 가격
    price_1m_ago = self.price_history.get(ticker, {}).get('1m')
    current_price = self.exchange.get_current_price(ticker)
    
    if price_1m_ago:
        change_1m = (current_price - price_1m_ago) / price_1m_ago
        
        # 1분 내 -5% 이상 급락
        if change_1m < -0.05:
            logger.error(f"🚨 FLASH CRASH: {ticker} dropped {change_1m:.1%} in 1min!")
            self._execute_sell(ticker, current_price, "Emergency: Flash Crash")
            return True
    
    return False
```

### 2. 변동성 급증 감지
```python
def _check_volatility_spike(self, ticker):
    # ATR (Average True Range) 계산
    df = self.exchange.get_ohlcv(ticker, interval="1m", count=20)
    current_atr = ta.volatility.AverageTrueRange(
        df['high'], df['low'], df['close'], window=14
    ).average_true_range().iloc[-1]
    
    # 정상 ATR 대비 3배 이상
    if current_atr > self.normal_atr[ticker] * 3:
        logger.warning(f"🚨 VOLATILITY SPIKE: {ticker} ATR={current_atr:.0f}")
        # 포지션 50% 축소 또는 전량 청산
        self._emergency_reduce_position(ticker, ratio=0.5)
        return True
    
    return False
```

### 3. 거래량 이상 감지
```python
def _check_volume_anomaly(self, ticker):
    df = self.exchange.get_ohlcv(ticker, interval="1m", count=20)
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].iloc[-20:-1].mean()
    
    # 거래량 10배 이상 급증
    if current_volume > avg_volume * 10:
        logger.warning(f"⚠️ VOLUME SPIKE: {ticker} {current_volume/avg_volume:.1f}x")
        # 주의 상태 전환 (손절선 타이트하게)
        self.emergency_mode[ticker] = True
        return True
    
    return False
```

## 📊 실제 케이스

### 케이스 1: 플래시 크래시
```
2024-03-15 14:32:00
BTC: 70,000,000원
→ 14:33:00: 66,500,000원 (-5% in 1min)
→ 긴급 청산 발동!
→ 손실: -5.2% (손절선 -0.7%보다 크지만 최소화)

vs 정상 손절:
→ 계속 하락 시 -8~10% 가능
```

### 케이스 2: 변동성 급증
```
정상 ATR: 50,000원
급증 ATR: 180,000원 (3.6배)
→ 포지션 50% 축소
→ 리스크 절반 감소
```

## 🔧 구현 위치
- **파일:** `trading_bot.py`
- **메서드:** `_check_exit_conditions()` 내부에 추가

## 📈 우선순위 설정
```python
def _check_exit_conditions(self, ticker):
    # 1순위: 긴급 청산
    if self._check_emergency_conditions(ticker):
        return
    
    # 2순위: 트레일링 스톱
    if self._check_trailing_stop(ticker):
        return
    
    # 3순위: 목표 수익
    if profit_rate >= self.target_profit:
        self._execute_sell(ticker, current_price, "Target Profit")
        return
    
    # 4순위: 손절
    if profit_rate <= -self.stop_loss:
        self._execute_sell(ticker, current_price, "Stop Loss")
        return
```

## 💡 주의사항
- 과도한 민감도는 불필요한 청산 유발
- 거래소 API 지연 고려 (실시간 감지 어려움)
- 백테스팅으로 임계값 조정 필요

## 🔗 참고 자료
- Freqtrade Emergency Exit: https://www.freqtrade.io/en/stable/stoploss/#emergency_exit
