"""
Backtesting Engine
==================
과거 데이터로 트레이딩 전략 시뮬레이션 및 성과 평가

Features:
- 업비트 API 기반 과거 데이터 수집
- AI 모델 기반 매매 시뮬레이션 (실제 트레이딩 로직과 동일)
- 성과 지표 계산 (승률, 손익비, MDD, Sharpe Ratio)
- 백그라운드 실행 지원
- 완료 시 자동 모델 재학습

🔧 v2.1 Updates:
- 매수/매도 조건 단순화 (과적합 방지)
- 진입: Mean Reversion OR MACD Momentum
- 청산: Target Profit / Stop Loss / BB Upper
- 수수료 반영, 멀티코인 포지션 분리
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import threading
import time
import pyupbit

logger = logging.getLogger(__name__)


class Backtester:
    """
    백테스팅 엔진

    과거 데이터로 현재 AI 전략의 성과를 시뮬레이션하고,
    결과가 좋으면 자동으로 모델을 재학습시킵니다.

    🔧 실제 트레이딩 로직과 완전히 동일한 조건 사용
    """

    def __init__(self, trading_bot, tickers: List[str] = None, days: int = 200):
        """
        Args:
            trading_bot: TradingBot 인스턴스
            tickers: 백테스팅할 코인 리스트 (None이면 실제 거래 내역에서 자동 선택)
            days: 테스트할 기간 (일)
        """
        self.bot = trading_bot
        self.tickers = tickers or self._get_traded_coins()
        self.days = days

        # 시뮬레이션 상태
        self.initial_capital = 1_000_000
        self.capital = self.initial_capital
        self.positions: Dict[str, Dict] = {}  # 🔧 멀티코인 포지션 지원
        self.trades = []
        self.capital_history = [self.initial_capital]

        # 🔧 수수료 설정 (실제와 동일)
        self.fee_rate = 0.0005  # 0.05% 편도

        # 🔧 일봉 백테스팅용 설정 (단순화)
        self.backtest_target_profit = 0.03  # 3% (일봉용)
        self.backtest_stop_loss = 0.03      # 3% (일봉용, 완화)

        # 🔧 BTC 필터 (하락장 매수 금지)
        self.btc_filter_enabled = True
        self.btc_decline_threshold = -0.03  # BTC 3% 하락 시 매수 금지
        self.btc_data = None  # BTC 데이터 캐시

        # 백테스팅 상태
        self.is_running = False
        self.thread = None
        self.progress = 0
        self.status = "idle"  # idle, running, completed, failed
        self.results = None
        self.current_ticker = None  # 현재 처리 중인 코인

    def _get_traded_coins(self) -> List[str]:
        """
        실제 거래 내역에서 코인 목록 가져오기 (거래량 상위 10개)
        """
        import sqlite3

        try:
            with sqlite3.connect(self.bot.memory.db_path) as conn:
                cursor = conn.execute("""
                    SELECT ticker, COUNT(*) as count
                    FROM trades
                    WHERE status = 'closed'
                    GROUP BY ticker
                    ORDER BY count DESC
                    LIMIT 10
                """)
                tickers = [row[0] for row in cursor.fetchall()]

            if not tickers:
                # 거래 내역이 없으면 기본 코인
                logger.warning("⚠️ No trade history found, using default coins")
                return ["BTC", "ETH", "XRP"]

            logger.info(f"📊 Selected {len(tickers)} coins from trade history: {', '.join(tickers)}")
            return tickers

        except Exception as e:
            logger.error(f"❌ Failed to get traded coins: {e}")
            return ["BTC", "ETH", "XRP"]

    def fetch_historical_data(self, ticker: str, days: int = 200) -> Optional[pd.DataFrame]:
        """
        업비트에서 과거 데이터 가져오기

        Args:
            ticker: 티커 (예: "BTC")
            days: 가져올 일수 (최대 200일)

        Returns:
            OHLCV 데이터프레임
        """
        try:
            logger.info(f"📊 Fetching {days} days of historical data for {ticker}...")

            # 업비트 API 호출 (최대 200일)
            df = pyupbit.get_ohlcv(f"KRW-{ticker}", interval="day", count=min(days, 200))

            if df is None or len(df) == 0:
                logger.error(f"❌ No data retrieved for {ticker}")
                return None

            logger.info(f"✅ Retrieved {len(df)} days of data ({df.index[0]} ~ {df.index[-1]})")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to fetch historical data: {e}")
            return None

    def calculate_net_profit(self, entry_price: float, current_price: float, amount: float) -> float:
        """
        수수료를 포함한 순수익률 계산 (실제 트레이딩과 동일)
        """
        buy_cost = (entry_price * amount) * (1 + self.fee_rate)
        sell_proceeds = (current_price * amount) * (1 - self.fee_rate)
        net_profit_rate = (sell_proceeds - buy_cost) / buy_cost
        return net_profit_rate

    def _check_entry_conditions(self, features: Dict, prediction: int, confidence: float,
                                 df: pd.DataFrame, i: int) -> tuple:
        """
        매수 조건 체크 (백테스팅용 - 일봉 데이터에 최적화)

        Returns:
            (should_buy, reason): 매수 여부와 사유
        """
        # 🔧 BTC 필터: BTC 하락장에서 알트코인 매수 금지 (5일로 민감도 증가)
        if self.btc_filter_enabled and self.btc_data is not None:
            current_date = df.index[i]
            if current_date in self.btc_data.index:
                btc_idx = self.btc_data.index.get_loc(current_date)
                if btc_idx >= 5:
                    btc_now = self.btc_data.iloc[btc_idx]['close']
                    btc_5d_ago = self.btc_data.iloc[btc_idx - 5]['close']
                    btc_trend = (btc_now - btc_5d_ago) / btc_5d_ago
                    if btc_trend < self.btc_decline_threshold:  # -3%
                        return False, f"BTC declining ({btc_trend*100:.1f}%)"

        # 🔥 단순화된 지표
        rsi = features.get('rsi', 50)
        bb_position = features.get('bb_position', 0.5)
        ema_9 = features.get('ema_9', 0)
        ema_21 = features.get('ema_21', 0)
        macd = features.get('macd', 0)
        macd_signal = features.get('macd_signal', 0)

        # 추세 확인
        trend_up = ema_9 > ema_21  # 상승 추세

        # 🔧 일봉용 급락 필터: 전일 대비 가격 변화
        daily_change = 0
        if i >= 1:
            prev_close = df.iloc[i-1]['close']
            curr_close = df.iloc[i]['close']
            if prev_close > 0:
                daily_change = (curr_close - prev_close) / prev_close
        not_crashing = daily_change > -0.05  # 전일 대비 -5% 이상 급락 아님

        # 과매도 조건: RSI < 35 OR BB < 0.25
        oversold = (rsi < 35) or (bb_position < 0.25)

        # MACD 골든크로스
        macd_golden_cross = macd > macd_signal

        # 최소 확신도
        min_confidence = confidence > 0.5

        # ========== 전략 1: Mean Reversion (과매도 + 급락 아님) ==========
        # 🔧 급락 중이 아니면 과매도 매수 허용
        if oversold and not_crashing and min_confidence:
            return True, "Mean Reversion"

        # ========== 전략 2: Momentum (MACD 골든크로스 + 상승 추세) ==========
        if macd_golden_cross and trend_up and min_confidence:
            return True, "MACD Momentum"

        return False, ""

    def _check_exit_conditions(self, position: Dict, current_price: float,
                                features: Dict, df: pd.DataFrame, i: int) -> tuple:
        """
        매도 조건 체크 (일봉 백테스팅용 - 완화된 설정)

        Returns:
            (should_sell, reason, profit_rate): 매도 여부, 사유, 수익률
        """
        entry_price = position['entry_price']
        amount = position['amount']

        # 🔧 수수료 포함 순수익률 계산
        profit_rate = self.calculate_net_profit(entry_price, current_price, amount)

        # 🔥 단순화된 청산 조건 (3가지)

        # 조건 1: 목표 수익률 (일봉용 3%)
        if profit_rate >= self.backtest_target_profit:
            return True, f"Target Profit ({self.backtest_target_profit*100:.1f}%)", profit_rate

        # 조건 2: 손절 (일봉용 3%, 완화)
        if profit_rate <= -self.backtest_stop_loss:
            return True, f"Stop Loss ({self.backtest_stop_loss*100:.1f}%)", profit_rate

        # 조건 3: 볼린저 밴드 상단 (과매수 청산)
        bb_position = features.get('bb_position', 0.5)
        if bb_position > 0.95:
            return True, "BB Upper (Overbought)", profit_rate

        return False, "", profit_rate

    def simulate_trade(self, df: pd.DataFrame, ticker: str = None):
        """
        과거 데이터로 매매 시뮬레이션 (실제 트레이딩 로직과 동일)

        Args:
            df: OHLCV 데이터프레임
            ticker: 현재 백테스팅 중인 코인
        """
        from .data_manager import FeatureEngineer

        if ticker is None:
            ticker = self.current_ticker or (self.tickers[0] if self.tickers else "BTC")

        logger.info(f"   💰 Current Capital: {self.capital:,.0f} KRW")
        logger.info(f"   📅 Period: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")

        for i in range(len(df)):
            current_date = df.index[i]
            current_price = df.iloc[i]['close']

            # 최소 데이터 필요 (기술적 지표 계산)
            if i < 30:
                continue

            # 특징 추출
            try:
                features = FeatureEngineer.extract_features(df.iloc[:i+1])
                if features is None:
                    continue
                features_df = FeatureEngineer.features_to_dataframe(features)
            except Exception as e:
                logger.debug(f"Feature extraction failed at {current_date}: {e}")
                continue

            # AI 예측
            prediction, confidence = self.bot.learner.predict(features_df)

            # 디버그: 예측 결과 샘플링 (10일마다)
            if i % 10 == 0:
                logger.debug(f"{current_date.strftime('%Y-%m-%d')} | Pred: {prediction}, Conf: {confidence:.2%}")

            # 🔧 포지션 체크 (해당 코인)
            position = self.positions.get(ticker)

            # ========== 매도 조건 체크 (포지션 있을 때) ==========
            if position is not None:
                should_sell, sell_reason, profit_rate = self._check_exit_conditions(
                    position, current_price, features, df, i
                )

                if should_sell:
                    # 🔧 수수료 반영 매도
                    exit_amount = position['amount'] * current_price * (1 - self.fee_rate)
                    entry_cost = position['trade_amount'] * (1 + self.fee_rate)
                    profit = exit_amount - entry_cost

                    self.capital += exit_amount
                    self.capital_history.append(self.capital)

                    self.trades.append({
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'profit_rate': profit_rate,
                        'profit': profit,
                        'confidence': position['confidence'],
                        'reason': sell_reason,
                        'ticker': ticker
                    })

                    logger.info(f"[매도] {current_date.strftime('%Y-%m-%d')} | {ticker} | {current_price:,.0f}원 | 수익률: {profit_rate*100:+.2f}% | {sell_reason}")

                    del self.positions[ticker]
                    continue

            # ========== 매수 조건 체크 (포지션 없을 때) ==========
            if position is None:
                should_buy, buy_reason = self._check_entry_conditions(
                    features, prediction, confidence, df, i
                )

                if should_buy:
                    trade_amount = min(self.bot.trade_amount, self.capital * 0.1)

                    if trade_amount >= 6000 and self.capital >= trade_amount:
                        # 🔧 수수료 반영 매수
                        actual_cost = trade_amount * (1 + self.fee_rate)
                        amount = trade_amount / current_price

                        self.positions[ticker] = {
                            'entry_date': current_date,
                            'entry_price': current_price,
                            'amount': amount,
                            'trade_amount': trade_amount,
                            'confidence': confidence
                        }

                        self.capital -= actual_cost
                        self.capital_history.append(self.capital)

                        logger.info(f"[매수] {current_date.strftime('%Y-%m-%d')} | {ticker} | {current_price:,.0f}원 | {buy_reason} | 확신도: {confidence:.2%}")

        # 🔧 시뮬레이션 종료 시 미청산 포지션 강제 청산
        if ticker in self.positions:
            position = self.positions[ticker]
            final_price = df.iloc[-1]['close']
            profit_rate = self.calculate_net_profit(position['entry_price'], final_price, position['amount'])

            exit_amount = position['amount'] * final_price * (1 - self.fee_rate)
            self.capital += exit_amount
            self.capital_history.append(self.capital)

            self.trades.append({
                'entry_date': position['entry_date'],
                'exit_date': df.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'profit_rate': profit_rate,
                'profit': exit_amount - position['trade_amount'] * (1 + self.fee_rate),
                'confidence': position['confidence'],
                'reason': 'End of Period',
                'ticker': ticker
            })

            logger.info(f"[강제청산] {ticker} | {final_price:,.0f}원 | 수익률: {profit_rate*100:+.2f}%")
            del self.positions[ticker]

        logger.info(f"✅ {ticker} Simulation Complete - Trades: {len([t for t in self.trades if t['ticker'] == ticker])}")

    def analyze_results(self) -> Dict:
        """
        백테스팅 결과 분석

        Returns:
            성과 지표 딕셔너리
        """
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'final_capital': self.capital,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_loss_ratio': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'wins': 0,
                'losses': 0,
                'tested_coins': self.tickers,
                'coin_count': len(self.tickers),
                'fee_rate': self.fee_rate,
                'message': '거래 없음 (매수 신호가 발생하지 않음)'
            }

        # 승률 (수수료 포함 순수익 기준)
        wins = sum(1 for t in self.trades if t['profit_rate'] > 0)
        win_rate = wins / len(self.trades)

        # 수익률
        total_return = (self.capital - self.initial_capital) / self.initial_capital

        # 평균 수익/손실
        profitable_trades = [t for t in self.trades if t['profit_rate'] > 0]
        losing_trades = [t for t in self.trades if t['profit_rate'] < 0]

        avg_profit = np.mean([t['profit_rate'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['profit_rate'] for t in losing_trades]) if losing_trades else 0

        # 손익비
        profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0

        # MDD (Maximum Drawdown)
        peak = self.initial_capital
        max_drawdown = 0

        for capital in self.capital_history:
            if capital > peak:
                peak = capital
            drawdown = (peak - capital) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Sharpe Ratio (간단 버전)
        returns = [t['profit_rate'] for t in self.trades]
        sharpe_ratio = (np.mean(returns) - 0) / np.std(returns) if len(returns) > 1 and np.std(returns) > 0 else 0

        # 🔧 코인별 통계
        coin_stats = {}
        for ticker in self.tickers:
            ticker_trades = [t for t in self.trades if t['ticker'] == ticker]
            if ticker_trades:
                ticker_wins = sum(1 for t in ticker_trades if t['profit_rate'] > 0)
                coin_stats[ticker] = {
                    'trades': len(ticker_trades),
                    'wins': ticker_wins,
                    'win_rate': ticker_wins / len(ticker_trades) if ticker_trades else 0,
                    'total_profit': sum(t['profit_rate'] for t in ticker_trades)
                }

        # 🔧 매도 사유별 통계
        reason_stats = {}
        for trade in self.trades:
            reason = trade['reason']
            if reason not in reason_stats:
                reason_stats[reason] = {'count': 0, 'total_profit': 0}
            reason_stats[reason]['count'] += 1
            reason_stats[reason]['total_profit'] += trade['profit_rate']

        results = {
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'final_capital': self.capital,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_loss_ratio': profit_loss_ratio,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'wins': wins,
            'losses': len(self.trades) - wins,
            'fee_rate': self.fee_rate,
            'coin_stats': coin_stats,
            'reason_stats': reason_stats
        }

        return results

    def print_results(self, results: Dict):
        """결과 출력"""
        logger.info("=" * 60)
        logger.info("📊 BACKTESTING RESULTS (수수료 반영)")
        logger.info("=" * 60)
        logger.info(f"총 거래 수: {results['total_trades']}건")
        logger.info(f"승: {results['wins']}건 / 패: {results['losses']}건")
        logger.info(f"승률: {results['win_rate']*100:.2f}%")
        logger.info(f"총 수익률: {results['total_return']*100:+.2f}%")
        logger.info(f"최종 자본: {results['final_capital']:,.0f}원 (초기: {self.initial_capital:,.0f}원)")
        logger.info(f"평균 수익: {results['avg_profit']*100:+.2f}%")
        logger.info(f"평균 손실: {results['avg_loss']*100:.2f}%")
        logger.info(f"손익비: {results['profit_loss_ratio']:.2f}")
        logger.info(f"최대 낙폭(MDD): {results['max_drawdown']*100:.2f}%")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"수수료율: {results.get('fee_rate', 0)*100:.2f}% (편도)")
        logger.info("=" * 60)

        # 🔧 코인별 통계 출력
        coin_stats = results.get('coin_stats', {})
        if coin_stats:
            logger.info("📈 코인별 성과:")
            for ticker, stats in coin_stats.items():
                logger.info(f"   {ticker}: {stats['trades']}건, 승률 {stats['win_rate']*100:.1f}%, 총수익 {stats['total_profit']*100:+.2f}%")

        # 🔧 매도 사유별 통계 출력
        reason_stats = results.get('reason_stats', {})
        if reason_stats:
            logger.info("📊 매도 사유별 통계:")
            for reason, stats in reason_stats.items():
                avg_profit = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
                logger.info(f"   {reason}: {stats['count']}건, 평균수익 {avg_profit*100:+.2f}%")

        logger.info("=" * 60)

        # 평가
        if results['win_rate'] >= 0.45 and results['profit_loss_ratio'] >= 1.5:
            logger.info("✅ 전략 검증 성공! 실전 투입 가능 수준입니다.")
            return True
        else:
            logger.warning("⚠️ 전략 개선 필요:")
            if results['win_rate'] < 0.45:
                logger.warning(f"   - 승률 {results['win_rate']*100:.1f}% < 목표 45%")
            if results['profit_loss_ratio'] < 1.5:
                logger.warning(f"   - 손익비 {results['profit_loss_ratio']:.2f} < 목표 1.5")
            return False

    def run(self):
        """백테스팅 실행 (동기) - 멀티 코인 지원"""
        try:
            self.status = "running"
            self.progress = 0

            # 🔧 상태 초기화 (재실행 시 필요)
            self.capital = self.initial_capital
            self.positions = {}
            self.trades = []
            self.capital_history = [self.initial_capital]

            logger.info("=" * 60)
            logger.info(f"🚀 Starting Multi-Coin Backtesting (v2.1 - Simplified)")
            logger.info(f"   Coins: {', '.join(self.tickers)} ({len(self.tickers)}개)")
            logger.info(f"   Period: {self.days} days")
            logger.info(f"   Fee Rate: {self.fee_rate*100:.2f}% (편도)")
            logger.info(f"   Target: +{self.backtest_target_profit*100:.0f}% / Stop: -{self.backtest_stop_loss*100:.0f}%")
            logger.info(f"   BTC Filter: {'ON' if self.btc_filter_enabled else 'OFF'}")
            logger.info("=" * 60)

            # 🔧 BTC 데이터 미리 로드 (필터용)
            if self.btc_filter_enabled:
                logger.info("📊 Loading BTC data for market filter...")
                self.btc_data = self.fetch_historical_data("BTC", self.days)
                if self.btc_data is not None:
                    logger.info(f"   ✅ BTC data loaded: {len(self.btc_data)} days")
                else:
                    logger.warning("   ⚠️ BTC data not available, disabling filter")
                    self.btc_filter_enabled = False

            # 각 코인마다 백테스팅 실행
            for idx, ticker in enumerate(self.tickers):
                self.current_ticker = ticker
                logger.info(f"\n[{idx+1}/{len(self.tickers)}] Testing {ticker}...")

                # 1. 데이터 수집
                df = self.fetch_historical_data(ticker, self.days)

                if df is None:
                    logger.warning(f"   ⚠️ Skipping {ticker}: No data available")
                    continue

                # 2. 시뮬레이션 (이 코인에 대해)
                self.simulate_trade(df, ticker)

                # 진행률 업데이트
                self.progress = int((idx + 1) / len(self.tickers) * 100)

            # 3. 전체 결과 분석
            logger.info("\n📊 Analyzing Overall Results...")
            results = self.analyze_results()
            self.results = results

            # 코인별 통계 추가
            results['tested_coins'] = self.tickers
            results['coin_count'] = len(self.tickers)

            # 4. 결과 출력
            is_good = self.print_results(results)

            # 5. 성과가 좋으면 모델 재학습
            if is_good and results['total_trades'] >= 30:
                logger.info("🎓 Strategy validated! Triggering model retraining...")
                self._retrain_with_backtest_data()

            self.status = "completed"
            return results

        except Exception as e:
            logger.error(f"❌ Backtesting failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status = "failed"
            return None

    def run_async(self):
        """백테스팅 비동기 실행 (백그라운드)"""
        if self.is_running:
            logger.warning("⚠️ Backtesting is already running")
            return False

        self.is_running = True
        self.thread = threading.Thread(target=self._run_background, daemon=True)
        self.thread.start()

        logger.info("🚀 Backtesting started in background")
        return True

    def _run_background(self):
        """백그라운드 실행 래퍼"""
        try:
            self.run()
        finally:
            self.is_running = False

    def _retrain_with_backtest_data(self):
        """
        백테스팅 결과를 학습 데이터에 추가하고 모델 재학습

        주의: 실제로는 백테스팅 결과를 DB에 저장하지 않고,
        현재 모델이 이미 실전 데이터로 학습되어 있으므로
        여기서는 단순히 재학습만 트리거합니다.
        """
        logger.info("🎓 Retraining model based on backtesting validation...")
        self.bot._retrain_model()

    def get_status(self) -> Dict:
        """백테스팅 상태 조회"""
        return {
            'is_running': self.is_running,
            'status': self.status,
            'progress': self.progress,
            'results': self.results
        }
