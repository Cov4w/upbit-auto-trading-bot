/**
 * Trade History Component
 * 거래 내역 테이블
 */

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import api from '../api/client';

export default function TradeHistory() {
  const [page, setPage] = useState(1);

  const { data: historyData, isLoading } = useQuery({
    queryKey: ['tradeHistory', page],
    queryFn: async () => {
      const res = await api.data.getHistory(page, 10, 'closed');
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="card">
        <h2>📜 Trade History</h2>
        <p>Loading...</p>
      </div>
    );
  }

  const trades = historyData?.trades || [];
  const total = historyData?.total || 0;

  return (
    <div className="card trade-history">
      <h2>📜 Trade History</h2>

      {trades.length === 0 ? (
        <p className="empty-state">No trades yet. Start the bot to begin trading!</p>
      ) : (
        <>
          <div className="table-container">
            <table className="trade-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Entry</th>
                  <th>Exit</th>
                  <th>P/L</th>
                  <th>Conf</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade: any) => (
                  <tr key={trade.id}>
                    <td><strong>{trade.ticker}</strong></td>
                    <td>{trade.entry_price.toLocaleString()}</td>
                    <td>{trade.exit_price?.toLocaleString() || 'N/A'}</td>
                    <td className={trade.profit_rate && trade.profit_rate > 0 ? 'profit' : 'loss'}>
                      {trade.profit_rate
                        ? `${trade.profit_rate > 0 ? '+' : ''}${(trade.profit_rate * 100).toFixed(2)}%`
                        : 'N/A'}
                    </td>
                    <td>{(trade.model_confidence * 100).toFixed(0)}%</td>
                    <td>
                      {trade.is_profitable !== null ? (
                        <span className={`badge ${trade.is_profitable ? 'badge-success' : 'badge-danger'}`}>
                          {trade.is_profitable ? '✅ Win' : '❌ Loss'}
                        </span>
                      ) : (
                        <span className="badge badge-secondary">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              className="btn btn-sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              ← Prev
            </button>
            <span className="page-info">
              Page {page} of {Math.ceil(total / 10)}
            </span>
            <button
              className="btn btn-sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= Math.ceil(total / 10)}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
