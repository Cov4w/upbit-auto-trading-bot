/**
 * Trading Settings Component
 * 매매 설정 조절 UI
 */

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import api from '../api/client';

export default function TradingSettings() {
  const queryClient = useQueryClient();

  // 현재 설정 가져오기
  const { data: statusData } = useQuery({
    queryKey: ['botStatus'],
    queryFn: async () => {
      const res = await api.bot.getStatus();
      return res.data;
    },
  });

  // 로컬 상태
  const [tradeAmount, setTradeAmount] = useState(10000);
  const [targetProfit, setTargetProfit] = useState(2.0);
  const [stopLoss, setStopLoss] = useState(2.0);
  const [rebuyThreshold, setRebuyThreshold] = useState(1.5);
  const [isDirty, setIsDirty] = useState(false); // 사용자 수정 여부

  // 상태 동기화 (사용자가 수정 중이 아닐 때만)
  useEffect(() => {
    if (statusData && !isDirty) {
      setTradeAmount(statusData.trade_amount || 10000);
      setTargetProfit((statusData.target_profit || 0.02) * 100);
      setStopLoss((statusData.stop_loss || 0.02) * 100);
      setRebuyThreshold((statusData.rebuy_threshold || 0.015) * 100);
    }
  }, [statusData, isDirty]);

  // 설정 업데이트 mutation
  const updateConfigMutation = useMutation({
    mutationFn: (config: any) => api.bot.updateConfig(config),
    onSuccess: async () => {
      // 1. 먼저 최신 데이터를 서버에서 가져옵니다 (동기화 대기)
      await queryClient.invalidateQueries({ queryKey: ['botStatus'] });
      // 2. 데이터 갱신이 완료된 후 수정 모드 해제 (최신 값으로 자연스럽게 전환)
      setIsDirty(false);
    },
  });

  const handleApplySettings = () => {
    updateConfigMutation.mutate({
      trade_amount: tradeAmount,
      target_profit: targetProfit / 100, // % to decimal
      stop_loss: stopLoss / 100,
      rebuy_threshold: rebuyThreshold / 100,
    });
  };

  // 값 변경 핸들러
  const handleChange = (setter: (val: number) => void, val: number) => {
    setter(val);
    setIsDirty(true);
  };

  // 프리셋 전략
  const applyPreset = (preset: 'scalping' | 'swing' | 'bull') => {
    setIsDirty(true);
    switch (preset) {
      case 'scalping':
        setTargetProfit(0.8);
        setStopLoss(1.5);
        setRebuyThreshold(1.0);
        break;
      case 'swing':
        setTargetProfit(3.0);
        setStopLoss(5.0);
        setRebuyThreshold(2.0);
        break;
      case 'bull':
        setTargetProfit(10.0);
        setStopLoss(10.0);
        setRebuyThreshold(5.0);
        break;
    }
  };

  return (
    <div className="card trading-settings">
      <h2>⚙️ Trading Settings</h2>

      {/* 프리셋 전략 */}
      <div className="settings-presets">
        <h3>Quick Presets</h3>
        <div className="preset-buttons">
          <button
            className="btn btn-sm btn-preset"
            onClick={() => applyPreset('scalping')}
            title="Target: 0.8% / Stop: 1.5%"
          >
            ⚡ Scalping
          </button>
          <button
            className="btn btn-sm btn-preset"
            onClick={() => applyPreset('swing')}
            title="Target: 3% / Stop: 5%"
          >
            🛡️ Swing
          </button>
          <button
            className="btn btn-sm btn-preset"
            onClick={() => applyPreset('bull')}
            title="Target: 10% / Stop: 10%"
          >
            🚀 Bull Market
          </button>
        </div>
      </div>

      {/* 설정 슬라이더 */}
      <div className="settings-controls">
        {/* 매수 금액 */}
        <div className="setting-item">
          <div className="setting-header">
            <label>💰 Trade Amount</label>
            <div className="value-input-group">
              <input
                type="number"
                min="5000"
                max="100000"
                step="1000"
                value={tradeAmount}
                onChange={(e) => handleChange(setTradeAmount, Math.min(100000, Math.max(5000, Number(e.target.value))))}
                className="value-input"
              />
              <span className="unit">KRW</span>
            </div>
          </div>
          <input
            type="range"
            min="5000"
            max="100000"
            step="1000"
            value={tradeAmount}
            onChange={(e) => handleChange(setTradeAmount, Number(e.target.value))}
            className="slider"
          />
          <div className="range-labels">
            <span>5K</span>
            <span>50K</span>
            <span>100K</span>
          </div>
        </div>

        {/* 목표 수익률 */}
        <div className="setting-item">
          <div className="setting-header">
            <label>🎯 Target Profit</label>
            <div className="value-input-group">
              <input
                type="number"
                min="0.5"
                max="20"
                step="0.1"
                value={targetProfit}
                onChange={(e) => handleChange(setTargetProfit, Math.min(20, Math.max(0.5, Number(e.target.value))))}
                className="value-input profit"
              />
              <span className="unit">%</span>
            </div>
          </div>
          <input
            type="range"
            min="0.5"
            max="20"
            step="0.1"
            value={targetProfit}
            onChange={(e) => handleChange(setTargetProfit, Number(e.target.value))}
            className="slider slider-profit"
          />
          <div className="range-labels">
            <span>0.5%</span>
            <span>10%</span>
            <span>20%</span>
          </div>
        </div>

        {/* 손절률 */}
        <div className="setting-item">
          <div className="setting-header">
            <label>🛑 Stop Loss</label>
            <div className="value-input-group">
              <input
                type="number"
                min="0.3"
                max="20"
                step="0.1"
                value={stopLoss}
                onChange={(e) => handleChange(setStopLoss, Math.min(20, Math.max(0.3, Number(e.target.value))))}
                className="value-input loss"
              />
              <span className="unit">%</span>
            </div>
          </div>
          <input
            type="range"
            min="0.3"
            max="20"
            step="0.1"
            value={stopLoss}
            onChange={(e) => handleChange(setStopLoss, Number(e.target.value))}
            className="slider slider-loss"
          />
          <div className="range-labels">
            <span>0.3%</span>
            <span>10%</span>
            <span>20%</span>
          </div>
        </div>

        {/* 재매수 하락폭 */}
        <div className="setting-item">
          <div className="setting-header">
            <label>🔄 Rebuy Threshold</label>
            <div className="value-input-group">
              <input
                type="number"
                min="0"
                max="10"
                step="0.1"
                value={rebuyThreshold}
                onChange={(e) => handleChange(setRebuyThreshold, Math.min(10, Math.max(0, Number(e.target.value))))}
                className="value-input"
              />
              <span className="unit">%</span>
            </div>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="0.1"
            value={rebuyThreshold}
            onChange={(e) => handleChange(setRebuyThreshold, Number(e.target.value))}
            className="slider"
          />
          <div className="range-labels">
            <span>0%</span>
            <span>5%</span>
            <span>10%</span>
          </div>
        </div>
      </div>

      {/* 적용 버튼 */}
      <button
        className="btn btn-primary btn-apply"
        onClick={handleApplySettings}
        disabled={updateConfigMutation.isPending}
      >
        {updateConfigMutation.isPending ? '⏳ Applying...' : '✅ Apply Settings'}
      </button>

      {updateConfigMutation.isSuccess && (
        <p className="success-message">✅ Settings updated successfully!</p>
      )}
    </div>
  );
}
