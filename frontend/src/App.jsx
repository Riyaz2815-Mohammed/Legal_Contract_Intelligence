import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LegalTeam from './pages/LegalTeam';
import Upload from './pages/Upload';
import ClientWorkspace from './pages/ClientWorkspace';
import InviteClient from './pages/InviteClient';
import TemplatesPage from './pages/TemplatesPage';
import DocumentAnalysis from './pages/DocumentAnalysis';
import TemplateAnalysis from './pages/TemplateAnalysis';
import ClauseReview from './pages/ClauseReview';
import { apiFetch } from './utils/api';
import './App.css';


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true); // true until /auth/me resolves

  // Bootstrap: ask the backend who is currently logged in (via SSO cookie or local JWT)
  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await apiFetch('/auth/me');
        if (res.ok) {
          const data = await res.json();
          setIsAuthenticated(true);
          setUser(data.user);
        } else {
          // 401 / 403 — not logged in
          setIsAuthenticated(false);
          setUser(null);
        }
      } catch {
        // network error — treat as not authenticated
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    };
    checkSession();
  }, []);

  // Called after a successful local login — userData comes from the login response
  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    // Clear any legacy localStorage items that may still exist
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <Router>
      <div className="app">
        <div className="bg-animation"></div>
        {/* Don't render routes until we know auth state */}
        {authLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <span style={{ color: '#a5b4fc', fontSize: '1rem' }}>Loading…</span>
          </div>
        ) : (
          <Routes>
            <Route
              path="/login"
            element={
              isAuthenticated ?
                <Navigate to="/dashboard" /> :
                <Login onLogin={handleLogin} />
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ?
                <Dashboard user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/workspace/:clientId"
            element={
              isAuthenticated && (user?.role === 'admin' || user?.role === 'legal_team') ?
                <ClientWorkspace user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/legal-team"
            element={
              isAuthenticated && (user?.role === 'admin' || user?.role === 'legal_team') ?
                <LegalTeam user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/upload"
            element={
              isAuthenticated ?
                <Upload user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/invite-client"
            element={
              isAuthenticated && (user?.role === 'admin' || user?.role === 'legal_team') ?
                <InviteClient user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/templates"
            element={
              isAuthenticated && (user?.role === 'admin' || user?.role === 'legal_team') ?
                <TemplatesPage user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/analysis/:documentId"
            element={
              isAuthenticated ?
                <DocumentAnalysis user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/template-analysis/:templateId"
            element={
              isAuthenticated && (user?.role === 'admin' || user?.role === 'legal_team') ?
                <TemplateAnalysis user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route
            path="/review/:documentId"
            element={
              isAuthenticated ?
                <ClauseReview user={user} onLogout={handleLogout} /> :
                <Navigate to="/login" />
            }
          />
          <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        )}
      </div>
    </Router>
  );
}

export default App;
