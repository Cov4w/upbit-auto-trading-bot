# 🚀 Advanced Profit Logic (향후 도입 예정)

이 문서는 트레이딩 봇의 수익률 관리 로직을 고도화하기 위한 설계 문서입니다.
현재의 고정된 목표 수익률 및 단순 수익 계산 방식을 개선하여, **실제 수수료 반영** 및 **시장 변동성에 따른 유동적 대응**을 목표로 합니다.

---

## 1. 수수료 포함 순수익 계산 (Net Profit Calculation)

### 🎯 목적
현재는 `(현재가 - 매수가) / 매수가`로 단순 수익률을 계산합니다.
하지만 거래소 수수료(약 0.1% 왕복)를 고려하지 않으면, **스캘핑 시 "수익인 줄 알고 팔았는데 계좌는 줄어드는" 손실**이 발생할 수 있습니다.

### 🛠 구현 계획
`TradingBot._check_exit_conditions` 메서드 내 수익률 계산 로직을 변경합니다.

#### ✅ 예시 코드
```python
# Constants
FEE_RATE = 0.0005  # 0.05% (업비트 기준 편도)

def calculate_net_profit(entry_price, current_price, amount):
    # 매수 비용 = 진입가 * 수량 + 매수 수수료
    buy_cost = (entry_price * amount) * (1 + FEE_RATE)
    
    # 매도 수익 = 현재가 * 수량 - 매도 수수료
    sell_proceeds = (current_price * amount) * (1 - FEE_RATE)
    
    # 순수익률 계산
    net_profit_rate = (sell_proceeds - buy_cost) / buy_cost
    return net_profit_rate
```

#### 📋 적용 시나리오
1.  목표 수익률이 `0.5%`일 때, 단순 계산으로는 `0.5%` 상승 시 매도하지만,
2.  순수익 로직 적용 시 `0.6%` (0.5% + 수수료 0.1%) 상승해야 매도 조건이 충족됨.
3.  **결과:** 헛된 매매 방지 및 실질 계좌 우상향 보장.

---

## 2. 변동성 기반 동적 수익률 (Volatility-Based Adaptive Targets)

### 🎯 목적
고정된 목표 수익률(예: 2%)은 시장 상황을 반영하지 못합니다.
*   **횡보장(변동성 ↓):** 2% 도달하기 힘듦 → **목표를 0.8%로 낮춰** 짧게 먹어야 함.
*   **불장/급등장(변동성 ↑):** 2%는 너무 쉽게 도달함 → **목표를 5%로 높여** 크게 먹어야 함.

### 🛠 구현 계획
**ATR (Average True Range)** 지표를 활용하여 시장의 "변동성(Coin's Energy)"을 측정하고, 이에 비례하게 목표 수익률을 조절합니다.

#### ✅ 예시 코드
```python
def calculate_dynamic_target(self, ticker, base_target=0.02):
    # 최근 14일치 ATR(변동성) 조회
    df = self.exchange.get_ohlcv(ticker)
    atr = indicator.average_true_range(df['high'], df['low'], df['close'])
    current_atr = atr.iloc[-1]
    current_price = df['close'].iloc[-1]
    
    # ATR 비율 계산 (현재가 대비 변동폭)
    # 예: 현재가 1000원, ATR 50원 -> 변동성 5%
    volatility_rate = current_atr / current_price
    
    # 변동성에 따라 목표 수익률 보정 (가중치 0.5)
    # 변동성이 5%라면 -> 목표 수익률 = 2.5% (기본 2% + 알파)
    dynamic_target = max(0.01, volatility_rate * 0.5) 
    
    return dynamic_target
```

#### 📋 적용 시나리오
1.  **DOGE (변동성 큼):** ATR이 높게 나와 목표 수익률이 자동으로 `3.5%`로 설정됨. 급등락을 견디며 큰 수익 추구.
2.  **BTC (변동성 낮음):** ATR이 낮게 나와 목표 수익률이 `1.2%`로 설정됨. 안정적으로 짧게 수익 실현.

---

## 📅 Roadmap
- [ ] **Phase 1:** `TradingBot` 클래스에 수수료 상수(`FEE_RATE`) 정의 및 순수익 계산 로직 적용.
- [ ] **Phase 2:** `FeatureEngineer`에 ATR 지표 추가 및 `TradingBot` 진입 시점에 동적 목표가(`dynamic_target`) 계산 로직 추가.
- [ ] **Phase 3:** UI 설정 화면에 "Dynamic Target Mode (On/Off)" 스위치 추가하여 사용자 선택권 제공.
