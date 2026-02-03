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
      <h2>⚙️ Control Center</h2>

      {/* Balance Info */}
      {balance && (
        <div className="balance-info">
          <div className="balance-item">
            <span className="label">Available KRW</span>
            <span className="value">{balance.krw_balance?.toLocaleString() || 0} KRW</span>
          </div>
          <div className="balance-item">
            <span className="label">Total Value</span>
            <span className="value">{balance.total_value?.toLocaleString() || 0} KRW</span>
          </div>

          {/* Profit Display */}
          {balance.initial_balance && (
            <>
              <div className="balance-item">
                <span className="label">Initial Capital</span>
                <span className="value">{balance.initial_balance?.toLocaleString() || 0} KRW</span>
              </div>
              <div className="balance-item profit-item">
                <span className="label">Profit/Loss</span>
                <span className={`value ${balance.profit_rate >= 0 ? 'profit' : 'loss'}`}>
                  {balance.profit_rate >= 0 ? '+' : ''}{balance.profit_amount?.toLocaleString() || 0} KRW
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
          ▶️ Start Bot
        </button>

        <button
          className={`btn ${!isRunning ? 'btn-secondary' : 'btn-danger'}`}
          onClick={onStop}
          disabled={!isRunning}
        >
          ⏸️ Stop Bot
        </button>

        <button
          className="btn btn-info"
          onClick={onUpdateRecommendations}
        >
          🔄 Update Recommendations
        </button>

        <button
          className="btn btn-warning"
          onClick={onRetrain}
        >
          🎓 Retrain AI
        </button>
      </div>
    </div>
  );
}
