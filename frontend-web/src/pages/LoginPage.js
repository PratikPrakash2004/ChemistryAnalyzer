/**
 * Login Page Component
 * 
 * This page handles user authentication - both logging in existing users
 * and registering new ones. It's the first page users see before they
 * can access the main application.
 * 
 * The component maintains its own local state for:
 * - Form mode (login vs register)
 * - Form field values
 * - Loading state
 * - Error messages
 */

import React, { useState } from 'react';
import { login, register } from '../services/api';

function LoginPage({ onLogin }) {
  // ===== State Management =====
  
  // Toggle between login and register modes
  const [isRegistering, setIsRegistering] = useState(false);
  
  // Form field values
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // ===== Form Submission Handler =====
  
  const handleSubmit = async (e) => {
    // Prevent the default form submission (page reload)
    e.preventDefault();
    
    // Clear any previous errors
    setError('');
    
    // Validate inputs
    if (!username || !password) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (isRegistering && !email) {
      setError('Please provide an email address');
      return;
    }
    
    // Start loading state
    setLoading(true);
    
    try {
      let response;
      
      if (isRegistering) {
        // Call register API
        response = await register(username, email, password);
      } else {
        // Call login API
        response = await login(username, password);
      }
      
      // Success! Call the parent's onLogin function with the received data
      // This will update the App's authentication state
      onLogin(response.user, response.token);
      
    } catch (err) {
      // Handle errors - extract message from API response if available
      if (err.response && err.response.data) {
        // API returned an error message
        const errorData = err.response.data;
        
        // The error might be in different formats depending on what went wrong
        if (errorData.error) {
          setError(errorData.error);
        } else if (errorData.username) {
          setError(`Username: ${errorData.username[0]}`);
        } else if (errorData.password) {
          setError(`Password: ${errorData.password[0]}`);
        } else {
          setError('An error occurred. Please try again.');
        }
      } else {
        // Network error or other issue
        setError('Unable to connect to server. Please try again.');
      }
    } finally {
      // Stop loading regardless of success or failure
      setLoading(false);
    }
  };
  
  // ===== Toggle Between Login and Register =====
  
  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setError(''); // Clear errors when switching modes
  };
  
  // ===== Render =====
  
  return (
    <div className="login-container">
      <div className="login-card">
        {/* App branding */}
        <h1 className="login-title">
          🧪 ChemEquipViz
        </h1>
        <p className="login-subtitle">
          Chemical Equipment Parameter Visualizer
        </p>
        
        {/* Error message display */}
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}
        
        {/* Login/Register Form */}
        <form onSubmit={handleSubmit}>
          {/* Username field */}
          <div className="form-group">
            <label className="form-label" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={loading}
            />
          </div>
          
          {/* Email field - only shown during registration */}
          {isRegistering && (
            <div className="form-group">
              <label className="form-label" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                disabled={loading}
              />
            </div>
          )}
          
          {/* Password field */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={loading}
            />
          </div>
          
          {/* Submit button */}
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem' }}
            disabled={loading}
          >
            {loading ? (
              // Show loading state
              <span>Please wait...</span>
            ) : (
              // Show appropriate text based on mode
              <span>{isRegistering ? 'Create Account' : 'Sign In'}</span>
            )}
          </button>
        </form>
        
        {/* Toggle between login and register */}
        <p className="text-center mt-2">
          {isRegistering ? (
            <>
              Already have an account?{' '}
              <button 
                onClick={toggleMode}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: 'var(--primary-600)',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Sign in
              </button>
            </>
          ) : (
            <>
              Don't have an account?{' '}
              <button 
                onClick={toggleMode}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: 'var(--primary-600)',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Register
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
