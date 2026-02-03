import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 5000, // 5초마다 자동 갱신
      staleTime: 3000,
    },
  },
});

function App() {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <div className="App">
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        </div>
      </QueryClientProvider>
    </AuthProvider>
  );
}

export default App;
