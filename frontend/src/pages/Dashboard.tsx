/**
 * Main Dashboard Page
 * 트레이딩 봇 대시보드 메인 페이지
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';
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
  const { user, logout } = useAuth();
  const [wsConnected, setWsConnected] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Queries with optimized settings
  const { data: statusData } = useQuery({
    queryKey: ['botStatus'],
    queryFn: async () => {
      const res = await api.bot.getStatus();
      return res.data;
    },
    refetchInterval: 10000, // 10초마다 자동 갱신
    refetchOnWindowFocus: false, // 창 포커스 시 자동 refetch 비활성화
    staleTime: 5000, // 5초간 fresh 상태 유지
  });

  const { data: balanceData } = useQuery({
    queryKey: ['balance'],
    queryFn: async () => {
      const res = await api.data.getBalance();
      return res.data;
    },
    refetchInterval: 15000, // 15초마다 자동 갱신
    refetchOnWindowFocus: false,
    staleTime: 10000,
  });

  const { data: positionsData } = useQuery({
    queryKey: ['positions'],
    queryFn: async () => {
      const res = await api.data.getPositions();
      return res.data.data;
    },
    refetchInterval: 10000,
    refetchOnWindowFocus: false,
    staleTime: 5000,
  });

  const { data: recommendationsData } = useQuery({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const res = await api.data.getRecommendations();
      return res.data;
    },
    refetchInterval: 30000, // 30초마다 (추천은 덜 빈번하게)
    refetchOnWindowFocus: false,
    staleTime: 20000,
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

  const retrainMutation = useMutation({
    mutationFn: () => api.bot.retrain(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['botStatus'] });
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
    let ws: WebSocket | null = null;
    let pingInterval: NodeJS.Timeout | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let isUnmounting = false;

    const connect = () => {
      if (isUnmounting) return;

      try {
        ws = api.ws.connectLive();

        ws.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            if (message.type === 'update') {
              // 실시간 업데이트 반영 (throttled)
              queryClient.invalidateQueries({
                queryKey: ['botStatus'],
                refetchType: 'none' // 자동 refetch 방지
              });
              queryClient.invalidateQueries({
                queryKey: ['positions'],
                refetchType: 'none'
              });
            }
          } catch (e) {
            console.error('WebSocket message parse error:', e);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);

          // 재연결 시도 (5초 후, unmount되지 않은 경우만)
          if (!isUnmounting) {
            reconnectTimeout = setTimeout(() => {
              console.log('Attempting to reconnect...');
              connect();
            }, 5000);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          ws?.close();
        };

        // Ping 전송 (keep-alive)
        pingInterval = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setWsConnected(false);
      }
    };

    connect();

    return () => {
      isUnmounting = true;
      if (pingInterval) clearInterval(pingInterval);
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) {
        ws.close();
        ws = null;
      }
    };
  }, [queryClient]);

  const handleStartBot = () => startBotMutation.mutate();
  const handleStopBot = () => stopBotMutation.mutate();
  const handleUpdateRecommendations = () => updateRecommendationsMutation.mutate();
  const handleRetrain = () => retrainMutation.mutate();

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🤖 Self-Evolving Trading System</h1>
        <div className="header-status">
          <span className="user-info">
            👤 {user?.username || user?.email}
          </span>
          <button onClick={logout} className="logout-button">
            Logout
          </button>
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
            onRetrain={handleRetrain}
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
