import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { SessionsPage } from './pages/Sessions';
import { SessionDetail } from './pages/SessionDetail';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/sessions" element={<SessionsPage />} />
            <Route path="/sessions/:sessionId" element={<SessionDetail />} />
            <Route path="/" element={<Navigate to="/sessions" replace />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

