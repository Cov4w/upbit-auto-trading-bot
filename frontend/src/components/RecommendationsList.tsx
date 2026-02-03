/**
 * Recommendations List Component
 * AI 추천 코인 목록
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';

interface RecommendationsListProps {
  recommendations: any[];
  activeTickers: string[];
  isUpdating?: boolean;
}

export default function RecommendationsList({
  recommendations,
  activeTickers,
  isUpdating = false,
}: RecommendationsListProps) {
  const queryClient = useQueryClient();

  const toggleTickerMutation = useMutation({
    mutationFn: (ticker: string) => api.bot.toggleTicker(ticker),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['botStatus'] });
    },
  });

  const handleToggle = (ticker: string) => {
    toggleTickerMutation.mutate(ticker);
  };

  return (
    <div className="card recommendations-list">
      <div className="card-header-with-status">
        <h2>🎯 AI Recommendations</h2>
        {isUpdating && (
          <div className="updating-badge">
            <span className="spinner"></span>
            <span>Analyzing...</span>
          </div>
        )}
      </div>

      {isUpdating ? (
        <div className="updating-state">
          <div className="spinner-large"></div>
          <p>🤖 AI is analyzing market conditions...</p>
          <p className="hint">This may take 10-30 seconds. Check backend logs for details.</p>
        </div>
      ) : recommendations.length === 0 ? (
        <p className="empty-state">No recommendations yet. Click "Update Recommendations" to analyze coins.</p>
      ) : (
        <div className="recommendations-grid">
          {recommendations.map((rec: any, idx: number) => {
            const isActive = activeTickers.includes(rec.ticker);

            return (
              <div key={rec.ticker} className={`recommendation-item ${isActive ? 'active' : ''}`}>
                <div className="rec-header">
                  <span className="rank">#{idx + 1}</span>
                  <strong>{rec.ticker}</strong>
                  <span className={`badge ${rec.recommendation ? 'badge-success' : 'badge-warning'}`}>
                    {rec.recommendation ? '✅ Buy' : '⚠️ Hold'}
                  </span>
                </div>

                <div className="rec-metrics">
                  <div className="metric-item">
                    <span className="label">Score</span>
                    <span className="value">{rec.score.toFixed(1)}/100</span>
                  </div>
                  <div className="metric-item">
                    <span className="label">Confidence</span>
                    <span className="value">{(rec.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="metric-item">
                    <span className="label">RSI</span>
                    <span className="value">{rec.features.rsi.toFixed(1)}</span>
                  </div>
                </div>

                {rec.current_price && (
                  <div className="rec-price">
                    <span className="label">Price</span>
                    <span className="value">{rec.current_price.toLocaleString()} KRW</span>
                  </div>
                )}

                <button
                  className={`btn btn-sm ${isActive ? 'btn-danger' : 'btn-primary'}`}
                  onClick={() => handleToggle(rec.ticker)}
                >
                  {isActive ? '🚫 Remove' : '➕ Add'}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
