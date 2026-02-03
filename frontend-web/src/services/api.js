/**
 * API Service Module
 * 
 * This file centralizes all communication with our Django backend.
 * Think of it as a "translator" between our React frontend and the 
 * Python backend - it handles all the HTTP requests and responses.
 * 
 * Why centralize API calls?
 * 1. Easier to maintain - change the API URL in one place
 * 2. Consistent error handling across the app
 * 3. Automatic authentication token attachment
 * 4. Cleaner component code - components just call these functions
 */

import axios from 'axios';

// Base URL for our Django backend
// During development, Django runs on port 8000
const API_BASE_URL = 'http://localhost:8000/api';

// Create an Axios instance with default configuration
// Axios is a popular library for making HTTP requests
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * 
 * This runs BEFORE every API request is sent.
 * We use it to automatically attach the authentication token
 * to every request, so we don't have to do it manually each time.
 */
api.interceptors.request.use(
  (config) => {
    // Get the token from browser's localStorage
    const token = localStorage.getItem('authToken');
    
    // If we have a token, add it to the request headers
    // The format "Token xxx" is what Django REST Framework expects
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    return config;
  },
  (error) => {
    // If something goes wrong before the request is sent
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * 
 * This runs AFTER every API response is received.
 * We use it for consistent error handling, especially
 * for authentication errors (401 = unauthorized).
 */
api.interceptors.response.use(
  (response) => {
    // If the request was successful, just return the response
    return response;
  },
  (error) => {
    // If we get a 401 (Unauthorized) error, the token might be invalid
    // We should log the user out and redirect to login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ========== Authentication API Calls ==========

/**
 * Register a new user
 * @param {string} username - Desired username
 * @param {string} email - User's email
 * @param {string} password - Desired password
 * @returns {Promise} - Contains user data and auth token
 */
export const register = async (username, email, password) => {
  const response = await api.post('/auth/register/', {
    username,
    email,
    password,
  });
  return response.data;
};

/**
 * Login an existing user
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise} - Contains user data and auth token
 */
export const login = async (username, password) => {
  const response = await api.post('/auth/login/', {
    username,
    password,
  });
  return response.data;
};

/**
 * Logout the current user
 * Invalidates the auth token on the server
 * @returns {Promise}
 */
export const logout = async () => {
  const response = await api.post('/auth/logout/');
  return response.data;
};

// ========== Dataset/Upload API Calls ==========

/**
 * Upload a CSV file to the backend
 * 
 * This is special because we're sending a file, not JSON.
 * We use FormData which is the standard way to send files over HTTP.
 * 
 * @param {File} file - The CSV file object from file input
 * @returns {Promise} - Contains upload result and summary statistics
 */
export const uploadCSV = async (file) => {
  // FormData is like a virtual form that we can attach files to
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload/', formData, {
    headers: {
      // Override the default JSON content type
      // multipart/form-data is required for file uploads
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get list of all datasets (last 5) for the current user
 * @returns {Promise} - Array of dataset objects with summaries
 */
export const getDatasets = async () => {
  const response = await api.get('/datasets/');
  return response.data;
};

/**
 * Get detailed information about a specific dataset
 * Includes all equipment records
 * @param {number} id - Dataset ID
 * @returns {Promise} - Full dataset with equipment array
 */
export const getDatasetDetail = async (id) => {
  const response = await api.get(`/datasets/${id}/`);
  return response.data;
};

/**
 * Download PDF report for a dataset
 * 
 * This is special because we're downloading a file, not JSON.
 * We need to handle the binary response and trigger a download.
 * 
 * @param {number} id - Dataset ID
 * @param {string} filename - Suggested filename for download
 */
export const downloadPDFReport = async (id, filename) => {
  const response = await api.get(`/datasets/${id}/report/`, {
    // Tell axios to expect binary data (blob = Binary Large Object)
    responseType: 'blob',
  });
  
  // Create a temporary URL for the PDF blob
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  
  // Create a temporary link element and click it to trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `report_${id}.pdf`;
  document.body.appendChild(link);
  link.click();
  
  // Clean up - remove the link and revoke the URL
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Export the api instance in case components need direct access
export default api;
