/**
 * Main Application Component (App.js)
 * 
 * This is the "root" component of our React application. Think of it as
 * the main container that holds everything else together.
 * 
 * Key responsibilities:
 * 1. Manage authentication state (is user logged in?)
 * 2. Set up page routing (which URL shows which page)
 * 3. Provide common layout (navbar appears on all pages)
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';

// Import our page components
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import DatasetDetailPage from './pages/DatasetDetailPage';

// Import API service for logout
import { logout } from './services/api';

/**
 * Navbar Component
 * 
 * The navigation bar that appears at the top of every page (when logged in).
 * Shows app title, navigation links, and user info with logout button.
 */
function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      {/* App branding */}
      <h1>
        {/* Simple beaker icon using CSS */}
        <span role="img" aria-label="beaker">🧪</span>
        ChemEquipViz
      </h1>
      
      {/* Navigation links */}
      <div className="navbar-links">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/history">History</Link>
      </div>
      
      {/* User info and logout */}
      <div className="navbar-user">
        <span>Welcome, {user?.username}</span>
        <button className="btn btn-secondary" onClick={onLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

/**
 * ProtectedRoute Component
 * 
 * A wrapper that protects routes that require authentication.
 * If the user is not logged in, they get redirected to the login page.
 * This prevents unauthorized access to the dashboard, history, etc.
 */
function ProtectedRoute({ children, isAuthenticated }) {
  // If not authenticated, redirect to login page
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // If authenticated, show the requested page
  return children;
}

/**
 * Main App Component
 * 
 * The heart of our application. It manages:
 * - Authentication state (isAuthenticated, user)
 * - Routing (which URL shows which component)
 * - Layout (navbar + main content area)
 */
function App() {
  // ===== State Management =====
  
  // Track if user is logged in - check localStorage on initial load
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('authToken');
  });
  
  // Store user information
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  
  // ===== Event Handlers =====
  
  /**
   * Called when user successfully logs in
   * Saves auth data to localStorage and updates state
   */
  const handleLogin = (userData, token) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };
  
  /**
   * Called when user clicks logout
   * Clears auth data and redirects to login
   */
  const handleLogout = async () => {
    try {
      // Tell the server to invalidate the token
      await logout();
    } catch (error) {
      // Even if server call fails, still log out locally
      console.error('Logout error:', error);
    }
    
    // Clear local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    // Update state
    setIsAuthenticated(false);
    setUser(null);
  };
  
  // ===== Render =====
  
  return (
    <Router>
      <div className="app-container">
        {/* Only show navbar when logged in */}
        {isAuthenticated && (
          <Navbar user={user} onLogout={handleLogout} />
        )}
        
        {/* Main content area where pages render */}
        <main className={isAuthenticated ? 'main-content' : ''}>
          <Routes>
            {/* Login page - accessible when not logged in */}
            <Route 
              path="/login" 
              element={
                isAuthenticated 
                  ? <Navigate to="/dashboard" replace />
                  : <LoginPage onLogin={handleLogin} />
              } 
            />
            
            {/* Dashboard - protected, requires login */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <DashboardPage />
                </ProtectedRoute>
              } 
            />
            
            {/* History page - protected */}
            <Route 
              path="/history" 
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <HistoryPage />
                </ProtectedRoute>
              } 
            />
            
            {/* Dataset detail page - protected */}
            <Route 
              path="/dataset/:id" 
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <DatasetDetailPage />
                </ProtectedRoute>
              } 
            />
            
            {/* Default redirect - go to dashboard if logged in, login if not */}
            <Route 
              path="*" 
              element={
                <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
