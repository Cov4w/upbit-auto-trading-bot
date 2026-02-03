/**
 * Control Panel Component
 * 봇 제어
 */

interface ControlPanelProps {
  isRunning: boolean;
  onStart: () => void;
  onStop: () => void;
  onUpdateRecommendations: () => void;
  onRetrain: () => void;
  balance: any;
}

export default function ControlPanel({
  isRunning,
  onStart,
  onStop,
  onUpdateRecommendations,
  onRetrain,
  balance,
}: ControlPanelProps) {
  return (
    <div className="card control-panel">
      <h2>⚙️ 제어 센터</h2>

      {/* Balance Info */}
      {balance && (
        <div className="balance-info">
          <div className="balance-item">
            <span className="label">사용 가능 KRW</span>
            <span className="value">{balance.krw_balance?.toLocaleString() || 0} 원</span>
          </div>
          <div className="balance-item">
            <span className="label">총 자산</span>
            <span className="value">{balance.total_value?.toLocaleString() || 0} 원</span>
          </div>

          {/* Profit Display */}
          {balance.initial_balance && (
            <>
              <div className="balance-item">
                <span className="label">원금</span>
                <span className="value">{balance.initial_balance?.toLocaleString() || 0} 원</span>
              </div>
              <div className="balance-item profit-item">
                <span className="label">수익/손실</span>
                <span className={`value ${balance.profit_rate >= 0 ? 'profit' : 'loss'}`}>
                  {balance.profit_rate >= 0 ? '+' : ''}{balance.profit_amount?.toLocaleString() || 0} 원
                  <span className="profit-rate">
                    ({balance.profit_rate >= 0 ? '+' : ''}{balance.profit_rate?.toFixed(2) || 0}%)
                  </span>
                </span>
              </div>
            </>
          )}
        </div>
      )}

      {/* Control Buttons */}
      <div className="control-buttons">
        <button
          className={`btn ${isRunning ? 'btn-secondary' : 'btn-primary'}`}
          onClick={onStart}
          disabled={isRunning}
        >
          ▶️ 봇 시작
        </button>

        <button
          className={`btn ${!isRunning ? 'btn-secondary' : 'btn-danger'}`}
          onClick={onStop}
          disabled={!isRunning}
        >
          ⏸️ 봇 중지
        </button>

        <button
          className="btn btn-info"
          onClick={onUpdateRecommendations}
        >
          🔄 추천 업데이트
        </button>

        <button
          className="btn btn-warning"
          onClick={onRetrain}
        >
          🎓 AI 재학습
        </button>
      </div>
    </div>
  );
}
