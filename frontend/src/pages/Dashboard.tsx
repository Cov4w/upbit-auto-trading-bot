/**
 * Main Dashboard Page
 * 트레이딩 봇 대시보드 메인 페이지
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import api from '../api/client';
import StatusCard from '../components/StatusCard';
import ControlPanel from '../components/ControlPanel';
import TradeHistory from '../components/TradeHistory';
import RecommendationsList from '../components/RecommendationsList';
import ModelPerformance from '../components/ModelPerformance';
import CurrentPositions from '../components/CurrentPositions';
import TradingSettings from '../components/TradingSettings';
import '../styles/dashboard.css';

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [wsConnected, setWsConnected] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Queries
  const { data: statusData, refetch: refetchStatus } = useQuery({
    queryKey: ['botStatus'],
    queryFn: async () => {
      const res = await api.bot.getStatus();
      return res.data;
    },
  });

  const { data: balanceData } = useQuery({
    queryKey: ['balance'],
    queryFn: async () => {
      const res = await api.data.getBalance();
      return res.data;
    },
  });

  const { data: positionsData } = useQuery({
    queryKey: ['positions'],
    queryFn: async () => {
      const res = await api.data.getPositions();
      return res.data.data;
    },
  });

  const { data: recommendationsData } = useQuery({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const res = await api.data.getRecommendations();
      return res.data;
    },
  });

  // Mutations
  const startBotMutation = useMutation({
    mutationFn: () => api.bot.start(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['botStatus'] });
    },
  });

  const stopBotMutation = useMutation({
    mutationFn: () => api.bot.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['botStatus'] });
    },
  });

  const updateRecommendationsMutation = useMutation({
    mutationFn: () => api.bot.updateRecommendations(),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      }, 3000);
    },
  });

  // 실시간 시계 업데이트
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // WebSocket 연결
  useEffect(() => {
    const ws = api.ws.connectLive();

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'update') {
        // 실시간 업데이트 반영
        queryClient.invalidateQueries({ queryKey: ['botStatus'] });
        queryClient.invalidateQueries({ queryKey: ['positions'] });
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Ping 전송 (keep-alive)
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      ws.close();
    };
  }, [queryClient]);

  const handleStartBot = () => startBotMutation.mutate();
  const handleStopBot = () => stopBotMutation.mutate();
  const handleUpdateRecommendations = () => updateRecommendationsMutation.mutate();

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🤖 Self-Evolving Trading System</h1>
        <div className="header-status">
          <span className={wsConnected ? 'status-dot connected' : 'status-dot'}>
            {wsConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          <span className="timestamp">{currentTime.toLocaleTimeString('ko-KR')}</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Left Column - Controls & Status */}
        <div className="column left-column">
          <ControlPanel
            isRunning={statusData?.is_running || false}
            onStart={handleStartBot}
            onStop={handleStopBot}
            onUpdateRecommendations={handleUpdateRecommendations}
            balance={balanceData}
          />

          <TradingSettings />

          <StatusCard
            status={statusData}
            positions={positionsData?.positions || []}
          />
        </div>

        {/* Center Column - Performance & Positions */}
        <div className="column center-column">
          <ModelPerformance />

          <CurrentPositions />
        </div>

        {/* Right Column - Recommendations & History */}
        <div className="column right-column">
          <RecommendationsList
            recommendations={recommendationsData?.recommendations || []}
            activeTickers={statusData?.tickers || []}
            isUpdating={statusData?.is_updating_recommendations || false}
          />

          <TradeHistory />
        </div>
      </div>
    </div>
  );
}
