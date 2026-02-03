/**
 * Status Card Component
 * 봇 상태 및 주요 메트릭 표시
 */

interface StatusCardProps {
  status: any;
  positions: any[];
}

export default function StatusCard({ status, positions }: StatusCardProps) {
  if (!status) {
    return <div className="card">Loading...</div>;
  }

  return (
    <div className="card status-card">
      <h2>📊 봇 상태</h2>

      <div className="metrics-grid">
        <div className="metric">
          <span className="label">상태</span>
          <span className={`value ${status.is_running ? 'running' : 'stopped'}`}>
            {status.is_running ? '🟢 실행중' : '🔴 중지됨'}
          </span>
        </div>

        <div className="metric">
          <span className="label">모델 정확도</span>
          <span className="value">{(status.model_accuracy * 100).toFixed(1)}%</span>
        </div>

        <div className="metric">
          <span className="label">총 거래 수</span>
          <span className="value">{status.total_trades}</span>
        </div>

        <div className="metric">
          <span className="label">승률</span>
          <span className="value">{status.win_rate.toFixed(1)}%</span>
        </div>

        <div className="metric">
          <span className="label">평균 수익률</span>
          <span className="value">{status.avg_profit_pct.toFixed(2)}%</span>
        </div>

        <div className="metric">
          <span className="label">학습 데이터</span>
          <span className="value">{status.total_learning_samples}</span>
        </div>
      </div>

      {/* Active Positions */}
      {positions && positions.length > 0 && (
        <div className="positions">
          <h3>💼 현재 포지션 ({positions.length})</h3>
          {positions.map((pos: any) => (
            <div key={pos.ticker} className="position-item">
              <div className="position-header">
                <strong>{pos.ticker}</strong>
                <span className={pos.profit_rate > 0 ? 'profit' : 'loss'}>
                  {pos.profit_pct > 0 ? '+' : ''}{pos.profit_pct.toFixed(2)}%
                </span>
              </div>
              <div className="position-details">
                <span>진입가: {pos.entry_price.toLocaleString()} 원</span>
                <span>현재가: {pos.current_price?.toLocaleString() || 'N/A'} 원</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Active Tickers */}
      <div className="active-tickers">
        <h3>🎯 감시 중</h3>
        <div className="ticker-list">
          {status.tickers.map((ticker: string) => (
            <span key={ticker} className="ticker-badge">{ticker}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
