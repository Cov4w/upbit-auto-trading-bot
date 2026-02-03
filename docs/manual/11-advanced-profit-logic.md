# 🚀 Advanced Profit Logic - 사용 가이드

트레이딩 봇의 고도화된 수익률 관리 로직을 사용하는 방법을 설명합니다.

---

## ✅ 구현된 기능

### 1. 수수료 포함 순수익 계산 (Net Profit Calculation)

#### 🎯 목적
실제 거래소 수수료(왕복 0.1%)를 반영하여 **진짜 수익**을 계산합니다.
단순 수익률로는 "수익인 줄 알고 팔았는데 계좌는 줄어드는" 상황을 방지합니다.

#### 📊 작동 원리
```
매수 비용 = (진입가 × 수량) × (1 + 0.05%)
매도 수익 = (현재가 × 수량) × (1 - 0.05%)
순수익률 = (매도 수익 - 매수 비용) / 매수 비용
```

#### ⚙️ 사용 방법

**환경 변수 설정** (`.env` 파일):
```env
USE_NET_PROFIT=true  # 순수익 계산 활성화 (기본값: true)
```

**또는 웹 UI에서 설정** (✅ 구현 완료):
- Dashboard → Trading Settings → Advanced Settings → "💎 Use Net Profit Calculation" 토글

#### 📋 효과
- 목표 수익률 2%인 경우:
  - **단순 계산**: 2% 상승 시 매도 → 실제로는 손해 (수수료 0.1% 차감)
  - **순수익 계산**: 2.1% 상승 시 매도 → 실제 계좌 증가

---

### 2. 변동성 기반 동적 수익률 (Volatility-Based Adaptive Targets)

#### 🎯 목적
시장 변동성에 따라 목표 수익률을 자동 조절합니다.
- **횡보장** (변동성 ↓): 목표를 낮춰 짧게 먹음
- **불장/급등장** (변동성 ↑): 목표를 높여 크게 먹음

#### 📊 작동 원리
```
1. ATR(Average True Range) 지표로 변동성 측정
2. 변동성 비율 = ATR / 현재가
3. 동적 목표 = 변동성 비율 × 0.5 (최소 1%)
```

#### ⚙️ 사용 방법

**환경 변수 설정** (`.env` 파일):
```env
USE_DYNAMIC_TARGET=false  # 동적 목표 수익률 (기본값: false)
```

**또는 웹 UI에서 설정** (✅ 구현 완료):
- Dashboard → Trading Settings → Advanced Settings → "📊 Use Dynamic Target (ATR-based)" 토글

#### 📋 효과
- **DOGE** (변동성 큼, ATR=5%): 목표 2.5% (기본 2% → 자동 상향)
- **BTC** (변동성 낮음, ATR=2%): 목표 1.0% (기본 2% → 자동 하향)

---

### 3. 동적 포지션 사이징 (Kelly Criterion-Based Dynamic Sizing)

#### 🎯 목적
승률과 AI 확신도에 따라 투자 금액을 자동으로 조절합니다.
- **고확신 + 높은 승률**: 큰 금액 투자
- **저확신 + 낮은 승률**: 작은 금액 투자

#### 📊 작동 원리
```
1. Kelly Criterion 공식 계산
   f* = (p × b - q) / b
   (p: 승률, b: 평균수익/평균손실, q: 1-p)

2. Half-Kelly 적용 (안전 모드)
   kelly_fraction = f* × 0.5 (최대 25% 제한)

3. 최종 금액 = 잔액 × Kelly Fraction × AI 확신도
```

#### ⚙️ 사용 방법

**환경 변수 설정** (`.env` 파일):
```env
USE_DYNAMIC_SIZING=false  # 동적 포지션 사이징 (기본값: false)
```

**또는 웹 UI에서 설정** (✅ 구현 완료):
- Dashboard → Trading Settings → Advanced Settings → "🎯 Use Dynamic Sizing (Kelly Criterion)" 토글

#### 📋 효과
**시나리오 1**: 승률 70%, 확신도 80%
- 고정 모드: 10,000원 투자
- 동적 모드: 16,000원 투자 (Kelly × 확신도)

**시나리오 2**: 승률 40%, 확신도 50%
- 고정 모드: 10,000원 투자
- 동적 모드: 6,000원 투자 (최소 주문 금액)

#### ⚠️ 주의사항
- **최소 데이터 요구**: 30건 이상의 거래 기록 필요
- 데이터 부족 시 고정 금액으로 자동 전환
- 초보자는 비활성화 권장 (경험 후 활성화)

---

## 🛠 설정 가이드

### 기본 설정 (.env 파일)

```env
# ============================
# 🚀 Advanced Profit Logic
# ============================

# 순수익 계산 (수수료 포함)
USE_NET_PROFIT=true

# 동적 목표 수익률 (변동성 기반)
USE_DYNAMIC_TARGET=false

# 동적 포지션 사이징 (Kelly Criterion)
USE_DYNAMIC_SIZING=false

# 거래소 수수료 (편도, 업비트 기준)
# FEE_RATE는 코드에 하드코딩됨 (0.0005 = 0.05%)
```

### 추천 설정

#### 보수적 전략 (안정적)
```env
USE_NET_PROFIT=true
USE_DYNAMIC_TARGET=false
USE_DYNAMIC_SIZING=false
TARGET_PROFIT=0.02  # 고정 2%
TRADE_AMOUNT=10000  # 고정 금액
```

#### 공격적 전략 (변동성 추종)
```env
USE_NET_PROFIT=true
USE_DYNAMIC_TARGET=true
USE_DYNAMIC_SIZING=false
TARGET_PROFIT=0.02  # 기본 2%, 변동성에 따라 자동 조절
```

#### 전문가 전략 (완전 자동화)
```env
USE_NET_PROFIT=true
USE_DYNAMIC_TARGET=true
USE_DYNAMIC_SIZING=true
TARGET_PROFIT=0.02  # 기본값 (실제로는 ATR에 따라 자동 조절)
TRADE_AMOUNT=10000  # 기본값 (실제로는 Kelly Criterion으로 자동 조절)
```
⚠️ **주의**: 전문가 전략은 최소 30건 이상의 거래 기록이 필요합니다.

---

## 📊 로그 확인

봇 실행 중 터미널에 다음과 같이 표시됩니다:

### 순수익 모드 활성화 시
```bash
📊 [BTC] Price:50,000,000, Entry:49,000,000,
   Net Profit:1.98% (Target:>2.0%)
```

### 단순 수익 모드 시
```bash
📊 [BTC] Price:50,000,000, Entry:49,000,000,
   Simple Profit:2.04% (Target:>2.0%)
```

### 동적 목표 활성화 시
```bash
[BTC] Dynamic Target: 1.50% (ATR: 750,000, Volatility: 1.50%)
📊 [BTC] Price:50,000,000, Entry:49,000,000,
   Net Profit:1.98% (Target:>1.5%)  # 목표가 자동 조절됨!
```

---

## ⚠️ 주의사항

### 1. 순수익 계산 (USE_NET_PROFIT)
- ✅ **권장**: 항상 활성화
- 수수료를 고려하지 않으면 실제 손실 발생 가능
- 특히 스캘핑(단타) 전략 사용 시 필수

### 2. 동적 목표 (USE_DYNAMIC_TARGET)
- ⚠️ **주의**: 변동성이 극심한 장에서는 목표가 너무 높아질 수 있음
- 초보자는 `false`로 설정하고 고정 목표 사용 권장
- 경험이 쌓인 후 `true`로 변경하여 테스트

### 3. 수수료율 (FEE_RATE)
- 기본값: 0.0005 (0.05%, 업비트 기준)
- 빗썸 사용 시: 코드 수정 필요 (0.0025 = 0.25%)
- 위치: `backend/core/trading_bot.py:85`

### 4. 최소 수익률
- 순수익 모드에서는 **0.2% 이상** 권장
- 0.1% (수수료) + 0.1% (슬리피지) = 최소 0.2%

---

## 🔍 코드 위치

### Backend
- **TradingBot**: `backend/core/trading_bot.py`
  - Line 85: `self.fee_rate = 0.0005`
  - Line 86-87: `USE_NET_PROFIT`, `USE_DYNAMIC_TARGET` 설정
  - Line 714-736: `calculate_net_profit()` 메서드
  - Line 738-774: `calculate_dynamic_target()` 메서드
  - Line 800-815: 실제 적용 로직 (`_check_exit_conditions`)

- **Schemas**: `backend/models/schemas.py`
  - Line 33-34: BotStatus에 필드 추가
  - Line 95-96: UpdateConfigRequest에 필드 추가

- **Router**: `backend/routers/bot.py`
  - Line 195-200: Config 업데이트 엔드포인트

### Frontend (✅ 구현 완료)
- `frontend/src/components/TradingSettings.tsx`
  - Line 26-28: 고급 설정 상태 관리
  - Line 38-42: 상태 동기화 (서버에서 현재 설정 가져오기)
  - Line 51-60: API 업데이트 함수
  - Line 123-189: Advanced Settings UI (3개 토글 스위치)
- `frontend/src/styles/dashboard.css`
  - Line 878-990: 토글 스위치 스타일 (iOS-style)

---

## 📈 성능 비교

| 모드 | 목표 수익률 | 투자 금액 | 실제 수익률 | 계좌 증가 |
|------|------------|----------|------------|----------|
| 기본 (모두 OFF) | 고정 2% | 10,000원 | 2% - 0.1% = 1.9% | ✅ 기본 |
| 순수익 계산 ON | 고정 2% | 10,000원 | 2.1% - 0.1% = 2% | ✅ 안정적 |
| 순수익 + 동적목표 | 1~5% (ATR) | 10,000원 | 변동 | ✅✅ 시장 적응 |
| 모두 ON (전문가) | 1~5% (ATR) | 6K~25K (Kelly) | 변동 | ✅✅✅ 최적화 |

**권장 조합**:
- 🔰 **초보자**: 순수익 계산만 ON
- 🛡️ **중급자**: 순수익 + 동적 목표 ON
- 🚀 **전문가**: 모두 ON (데이터 30건+ 확보 후)

---

## 🎓 FAQ

**Q: 순수익 계산을 끄면 어떻게 되나요?**
A: 수수료를 고려하지 않은 단순 수익률로 계산합니다. 스캘핑 시 손실 가능성이 높습니다.

**Q: 동적 목표가 너무 높게 설정되면?**
A: 매도가 늦어져 수익 실현이 어려울 수 있습니다. 초보자는 비활성화 권장.

**Q: 빗썸에서 사용하려면?**
A: `backend/core/trading_bot.py:85`의 `self.fee_rate = 0.0025`로 변경 (0.25%).

**Q: 웹 UI에서 설정할 수 있나요?**
A: ✅ **가능합니다!** Dashboard → Trading Settings → Advanced Settings에서 3개의 토글 스위치로 실시간 설정 가능합니다.

**Q: 동적 포지션 사이징이 작동하지 않아요.**
A: 최소 30건의 거래 기록이 필요합니다. 데이터가 부족하면 자동으로 고정 금액으로 전환됩니다.

**Q: 모든 고급 설정을 활성화해도 되나요?**
A: 순수익 계산은 항상 권장하지만, 동적 목표와 동적 사이징은 경험이 쌓인 후 활성화하는 것이 좋습니다.

---

## 📝 업데이트 내역

- **2025-02-03 v2**: 웹 UI 추가 완료 ✅
  - Trading Settings에 Advanced Settings 섹션 추가
  - 3개 토글 스위치 구현 (순수익, 동적목표, 동적사이징)
  - iOS-style 토글 스위치 디자인
  - 실시간 설정 변경 및 서버 동기화

- **2025-02-03 v1**: 백엔드 구현 완료
  - 순수익 계산 기능 추가
  - ATR 기반 동적 목표 수익률 추가
  - Kelly Criterion 기반 동적 포지션 사이징 추가
  - 환경 변수 설정 지원

---

## 📞 문의

기능 개선 제안이나 버그 리포트는 GitHub Issues에 남겨주세요.
