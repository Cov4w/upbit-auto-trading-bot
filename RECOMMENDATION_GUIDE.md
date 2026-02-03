# 🤖 AI 추천 시스템 작동 원리

## 📋 "Update Recommendations" 버튼을 누르면?

### 1️⃣ **시작** (즉시)
```
2026-02-03 10:45:00 - INFO - 🔄 Started async recommendation update...
```
→ 백그라운드 스레드 시작

---

### 2️⃣ **분석 프로세스 시작** (1-2초 후)
```
============================================================
🚀 AI COIN RECOMMENDATION ANALYSIS STARTED
============================================================
📊 This process will:
   1. Fetch OHLCV data for each coin
   2. Extract technical indicators (RSI, MACD, Bollinger Bands)
   3. Run AI model prediction
   4. Calculate composite score
   5. Rank and select top 5 coins
============================================================
```

---

### 3️⃣ **배치 스캔** (10-30초 소요)
```
🔍 Scanning Batch: 1~50 / 200 coins (50 items)
   Target coins: BTC, ETH, XRP, SOL, DOGE, ADA, AVAX, MATIC...

   [1/50] Analyzing BTC...
   ✅ BTC: Score=85.3, Conf=75.2%, RSI=45.8
   [2/50] Analyzing ETH...
   ✅ ETH: Score=78.1, Conf=68.5%, RSI=52.3
   ...
   [50/50] Analyzing MATIC...
   ⚠️ MATIC: No valid data

📊 Batch Analysis Complete: ✅ Success=42, ⚠️ Failed=8, Total=50
```

**배치 스캔 방식**:
- 한 번에 50개 코인 분석
- 각 코인당 0.15초 대기 (API Rate Limit 방지)
- **예상 소요 시간**: 50 × 0.15초 = **약 7.5초**

---

### 4️⃣ **결과 정리** (완료)
```
============================================================
✅ RECOMMENDATION UPDATE COMPLETE (8.2s)
📈 Found 5 recommended coins:
   #1 A: Score=87.5, Confidence=82.3%, RSI=35.2
   #2 ETH: Score=85.1, Confidence=75.8%, RSI=42.1
   #3 LAYER: Score=82.3, Confidence=71.5%, RSI=38.9
   #4 FF: Score=79.8, Confidence=68.2%, RSI=44.3
   #5 ETC: Score=77.2, Confidence=65.9%, RSI=47.8
============================================================
```

---

## 🔍 각 단계 설명

### 1. OHLCV 데이터 수집
```python
df = exchange.get_ohlcv(ticker, interval="day")
```
- 최근 캔들스틱 데이터 가져오기
- 최소 30개 데이터 필요

### 2. 기술적 지표 추출
```python
features = FeatureEngineer.extract_features(df)
```
추출되는 지표:
- **RSI** (Relative Strength Index): 과매수/과매도
- **MACD** (Moving Average Convergence Divergence): 추세
- **Bollinger Bands**: 변동성
- **볼륨**: 거래량 추세
- **EMA**: 지수 이동 평균

### 3. AI 모델 예측
```python
prediction, confidence = learner.predict(features_df)
```
- **XGBoost 모델** 사용
- **출력**: 수익 예측 클래스 + 확신도 (0~1)

### 4. 종합 점수 계산
```python
score = calculate_score(features, confidence, prediction)
```
점수 = AI 확신도 + 기술적 지표 강도 + 과거 승률

### 5. 상위 5개 선정
```python
analyses.sort(key=lambda x: x['score'], reverse=True)
return analyses[:5]
```

---

## 📊 프론트엔드에서 보이는 것

### 분석 중
```
🎯 AI Recommendations
   🔄 Analyzing...

🤖 AI is analyzing market conditions...
This may take 10-30 seconds. Check backend logs for details.
```

### 완료 후
```
#1  A       ⚠️ Hold
    Score: 87.5/100
    Confidence: 82.3%
    RSI: 35.2
    Price: 140 KRW
    [🚫 Remove] 버튼
```

---

## 🔄 배치 스캔 시스템

### 왜 한 번에 모든 코인을 분석하지 않나요?
- **API Rate Limit**: 거래소 API 호출 제한
- **성능**: 200개 코인 전체 분석 시 30초+ 소요
- **효율성**: 배치로 나눠서 순차 스캔

### 다음 스캔
```
🔜 Next Scan: 51~100
```
- 다음에 "Update Recommendations" 버튼을 누르면 51~100번 코인 분석
- 전체 스캔 완료 후 1번부터 다시 시작

---

## 💡 백엔드 로그 보는 방법

### Terminal에서 확인
```bash
# Backend 실행 중인 터미널에서 실시간 로그 확인
cd backend
uvicorn main:app --reload
```

### 상세 로그 레벨 변경 (선택사항)
`backend/core/coin_selector.py` 또는 `trading_bot.py`에서:
```python
logger.debug(...)  # 디버그 로그 (기본적으로 숨겨짐)
```

로깅 레벨을 DEBUG로 변경하려면:
```python
logging.basicConfig(level=logging.DEBUG)
```

---

## ⏱️ 예상 소요 시간

| 코인 수 | 배치 크기 | 소요 시간 |
|---------|-----------|-----------|
| 50개    | 50        | ~7.5초    |
| 100개   | 50        | ~15초     |
| 200개   | 50        | ~30초     |

**주의**: API Rate Limit으로 각 코인마다 0.15초 대기

---

## 🧪 테스트 방법

### 1. 백엔드 로그 확인하며 실행
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. 브라우저에서 버튼 클릭
1. http://localhost:3000 접속
2. "🔄 Update Recommendations" 버튼 클릭
3. Terminal 1에서 로그 확인

### 3. 예상 로그
```
🔄 Started async recommendation update...
============================================================
🚀 AI COIN RECOMMENDATION ANALYSIS STARTED
============================================================
🔍 Scanning Batch: 1~50 / 200 coins (50 items)
   [1/50] Analyzing BTC...
   ✅ BTC: Score=85.3, Conf=75.2%, RSI=45.8
   ...
📊 Batch Analysis Complete: ✅ Success=42, ⚠️ Failed=8
============================================================
✅ RECOMMENDATION UPDATE COMPLETE (8.2s)
📈 Found 5 recommended coins:
   #1 A: Score=87.5, Confidence=82.3%, RSI=35.2
============================================================
```

---

## 🤔 자주 묻는 질문

### Q: 학습은 언제 하나요?
A: 추천 업데이트 시에는 **학습하지 않습니다**. 기존 학습된 모델로 **예측**만 수행합니다.

학습은 다음 때 발생:
- 매매 완료 후 N건(기본 10건) 누적 시 자동 재학습
- "Retrain Model" 버튼 클릭 (수동 재학습)

### Q: 왜 이렇게 오래 걸리나요?
A: API Rate Limit 때문입니다. 각 코인마다:
1. OHLCV 데이터 조회 (API 호출)
2. 현재가 조회 (API 호출)
3. 0.15초 대기 (필수)

→ 50개 코인 = 최소 7.5초

### Q: 더 빠르게 할 수 없나요?
A: 가능하지만 API Rate Limit에 걸릴 위험이 있습니다.
`coin_selector.py`의 `time.sleep(0.15)` 값을 줄이면 빨라지지만,
거래소 API가 차단될 수 있습니다.

### Q: 프론트엔드에서 진행 상황을 볼 수 없나요?
A: 현재는 "Analyzing..." 표시만 있습니다.
WebSocket으로 실시간 진행 상황 전송 기능은 향후 추가 예정입니다.

---

**작성일**: 2026-02-03
**버전**: 2.1.0
