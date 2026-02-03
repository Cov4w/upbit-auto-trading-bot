/**
 * Current Positions Component
 * 현재 보유 포지션 상세 정보
 */

import { useQuery } from '@tanstack/react-query';
import api from '../api/client';

export default function CurrentPositions() {
  const { data: positionsData } = useQuery({
    queryKey: ['positions'],
    queryFn: async () => {
      const res = await api.data.getPositions();
      return res.data.data;
    },
    refetchInterval: 5000,
  });

  const positions = positionsData?.positions || [];

  return (
    <div className="card current-positions">
      <h2>💼 Current Positions</h2>

      {positions.length === 0 ? (
        <div className="empty-state">
          <p>✅ No open positions</p>
          <p className="hint">The bot will automatically open positions when it finds good opportunities.</p>
        </div>
      ) : (
        <div className="positions-grid">
          {positions.map((pos: any) => {
            const profitClass = pos.profit_rate > 0 ? 'profit' : 'loss';
            const entryTime = new Date(pos.entry_time);
            const duration = Math.floor((Date.now() - entryTime.getTime()) / 1000 / 60);

            return (
              <div key={pos.ticker} className={`position-card ${profitClass}`}>
                <div className="position-header">
                  <h3>{pos.ticker}</h3>
                  <span className={`profit-badge ${profitClass}`}>
                    {pos.profit_pct > 0 ? '+' : ''}{pos.profit_pct.toFixed(2)}%
                  </span>
                </div>

                <div className="position-details">
                  <div className="detail-row">
                    <span className="label">Entry Price</span>
                    <span className="value">{pos.entry_price.toLocaleString()} KRW</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Current Price</span>
                    <span className="value">{pos.current_price?.toLocaleString() || 'N/A'} KRW</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Amount</span>
                    <span className="value">{pos.amount.toFixed(6)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Holding Time</span>
                    <span className="value">
                      {duration < 60 ? `${duration}m` : `${Math.floor(duration / 60)}h ${duration % 60}m`}
                    </span>
                  </div>
                </div>

                <div className="position-progress">
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${profitClass}`}
                      style={{ width: `${Math.min(Math.abs(pos.profit_pct) * 5, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
