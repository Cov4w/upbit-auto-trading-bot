/**
 * API Client
 * FastAPI 백엔드와 통신하는 클라이언트
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Methods
export const api = {
  // Bot Control
  bot: {
    getStatus: () => apiClient.get('/api/bot/status'),
    start: (tickers?: string[]) => apiClient.post('/api/bot/start', { tickers }),
    stop: () => apiClient.post('/api/bot/stop'),
    retrain: () => apiClient.post('/api/bot/retrain'),
    updateRecommendations: () => apiClient.post('/api/bot/update-recommendations'),
    updateConfig: (config: any) => apiClient.post('/api/bot/config', config),
    toggleTicker: (ticker: string) => apiClient.post('/api/bot/ticker/toggle', { ticker }),
  },

  // Data
  data: {
    getBalance: () => apiClient.get('/api/data/balance'),
    getHistory: (page = 1, pageSize = 20, status?: string) =>
      apiClient.get('/api/data/history', { params: { page, page_size: pageSize, status } }),
    getRecommendations: () => apiClient.get('/api/data/recommendations'),
    getOHLCV: (ticker: string, interval = 'day') =>
      apiClient.get(`/api/data/ohlcv/${ticker}`, { params: { interval } }),
    getStatistics: () => apiClient.get('/api/data/statistics'),
    getPositions: () => apiClient.get('/api/data/positions'),
  },

  // WebSocket
  ws: {
    connectLive: () => {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/live';
      return new WebSocket(wsUrl);
    },
    connectLogs: () => {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/logs';
      return new WebSocket(wsUrl);
    },
  },
};

export default api;
