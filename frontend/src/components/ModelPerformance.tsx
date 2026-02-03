/**
 * Model Performance Chart Component
 * 모델 성능 및 수익률 그래프
 */

import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api/client';

export default function ModelPerformance() {
  const { data: historyData } = useQuery({
    queryKey: ['tradeHistory'],
    queryFn: async () => {
      const res = await api.data.getHistory(1, 50, 'closed');
      return res.data;
    },
  });

  const { data: statusData } = useQuery({
    queryKey: ['botStatus'],
    queryFn: async () => {
      const res = await api.bot.getStatus();
      return res.data;
    },
  });

  if (!historyData || !historyData.trades || historyData.trades.length === 0) {
    return (
      <div className="card model-performance">
        <h2>📈 Model Performance</h2>
        <p className="empty-state">No trading data yet. Start the bot to see performance metrics.</p>
      </div>
    );
  }

  // 누적 수익률 계산
  const chartData = historyData.trades
    .slice()
    .reverse()
    .map((trade: any, index: number) => {
      const cumulativeReturn = historyData.trades
        .slice(0, index + 1)
        .reduce((acc: number, t: any) => acc * (1 + (t.profit_rate || 0)), 1) - 1;

      return {
        id: index + 1,
        timestamp: new Date(trade.timestamp).toLocaleDateString(),
        profit: (trade.profit_rate || 0) * 100,
        cumulative: cumulativeReturn * 100,
        confidence: (trade.model_confidence || 0) * 100,
      };
    });

  return (
    <div className="card model-performance">
      <h2>📈 Model Performance & Returns</h2>

      {/* 성능 요약 */}
      <div className="performance-summary">
        <div className="summary-item">
          <span className="label">Accuracy</span>
          <span className="value">{statusData ? (statusData.model_accuracy * 100).toFixed(1) : 0}%</span>
        </div>
        <div className="summary-item">
          <span className="label">Win Rate</span>
          <span className="value">{statusData ? statusData.win_rate.toFixed(1) : 0}%</span>
        </div>
        <div className="summary-item">
          <span className="label">Avg Profit</span>
          <span className="value">{statusData ? statusData.avg_profit_pct.toFixed(2) : 0}%</span>
        </div>
        <div className="summary-item">
          <span className="label">Total Trades</span>
          <span className="value">{statusData ? statusData.total_trades : 0}</span>
        </div>
      </div>

      {/* 누적 수익률 차트 */}
      <div className="chart-container">
        <h3>Cumulative Returns</h3>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorReturn" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              dataKey="id"
              stroke="#888"
              label={{ value: 'Trade #', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              stroke="#888"
              label={{ value: 'Return (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #00d4ff' }}
              labelStyle={{ color: '#00d4ff' }}
            />
            <Area
              type="monotone"
              dataKey="cumulative"
              stroke="#00d4ff"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorReturn)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 모델 신뢰도 차트 */}
      <div className="chart-container">
        <h3>Model Confidence Over Time</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="id" stroke="#888" />
            <YAxis stroke="#888" domain={[0, 100]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #7b2ff7' }}
            />
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#7b2ff7"
              strokeWidth={2}
              dot={{ fill: '#7b2ff7', r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
