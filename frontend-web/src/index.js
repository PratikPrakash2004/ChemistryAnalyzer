/**
 * React Application Entry Point
 * 
 * This is where our React application starts. Think of it like
 * the main() function in other programming languages - it's the
 * first code that runs when someone opens our web app.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Create a "root" where our React app will live in the HTML
// The 'root' element is defined in public/index.html
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render our main App component into that root
// StrictMode adds extra checks during development to help catch bugs
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
