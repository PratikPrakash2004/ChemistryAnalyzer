/**
 * Dashboard Page Component
 * 
 * This is the main working area of our application. Users come here to:
 * 1. Upload CSV files containing chemical equipment data
 * 2. View summary statistics (averages, counts, etc.)
 * 3. See visual charts of the data
 * 4. Browse the equipment data in a table
 * 
 * The page uses Chart.js (via react-chartjs-2) for data visualization.
 * Chart.js is a popular, easy-to-use charting library that creates
 * beautiful, responsive charts with minimal configuration.
 */

import React, { useState, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { uploadCSV } from '../services/api';

// Register Chart.js components
// This is required for Chart.js v3+ to work properly
ChartJS.register(
  CategoryScale,  // For x-axis labels (categories)
  LinearScale,    // For y-axis numbers
  BarElement,     // For bar charts
  ArcElement,     // For pie charts
  Title,          // For chart titles
  Tooltip,        // For hover tooltips
  Legend          // For chart legends
);

function DashboardPage() {
  // ===== State Management =====
  
  // Store the uploaded data and summary
  const [uploadedData, setUploadedData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [equipment, setEquipment] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragOver, setDragOver] = useState(false);
  
  // Reference to the hidden file input
  const fileInputRef = useRef(null);
  
  // ===== File Upload Handlers =====
  
  /**
   * Handle file selection (from click or drop)
   * Validates the file and uploads it to the backend
   */
  const handleFileSelect = async (file) => {
    // Clear previous messages
    setError('');
    setSuccess('');
    
    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }
    
    setLoading(true);
    
    try {
      // Upload the file to our Django backend
      const response = await uploadCSV(file);
      
      // Store the response data
      setUploadedData(response);
      setSummary(response.summary);
      
      // The summary contains the data, but we need to reconstruct equipment list
      // for the table. We'll create it from the summary data structure
      // In a real app, you'd fetch the full dataset from /api/datasets/{id}/
      
      setSuccess(`Successfully uploaded ${response.filename}`);
      
      // Fetch the detailed dataset to get equipment list
      const token = localStorage.getItem('authToken');
      const detailResponse = await fetch(
        `http://localhost:8000/api/datasets/${response.dataset_id}/`,
        {
          headers: {
            'Authorization': `Token ${token}`
          }
        }
      );
      const detailData = await detailResponse.json();
      setEquipment(detailData.equipment || []);
      
    } catch (err) {
      console.error('Upload error:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to upload file. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Handle file input change (user clicked and selected file)
   */
  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };
  
  /**
   * Handle drag and drop events
   */
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };
  
  // ===== Chart Configuration =====
  
  // Blue theme colors for charts (Version A)
  const chartColors = {
    primary: 'rgba(37, 99, 235, 0.8)',      // Blue
    secondary: 'rgba(16, 185, 129, 0.8)',   // Green
    tertiary: 'rgba(245, 158, 11, 0.8)',    // Orange
    quaternary: 'rgba(239, 68, 68, 0.8)',   // Red
    quinary: 'rgba(139, 92, 246, 0.8)',     // Purple
    senary: 'rgba(6, 182, 212, 0.8)',       // Cyan
  };
  
  // Pie chart data for equipment type distribution
  const pieChartData = summary ? {
    labels: Object.keys(summary.type_distribution),
    datasets: [{
      data: Object.values(summary.type_distribution),
      backgroundColor: [
        chartColors.primary,
        chartColors.secondary,
        chartColors.tertiary,
        chartColors.quaternary,
        chartColors.quinary,
        chartColors.senary,
      ],
      borderColor: 'white',
      borderWidth: 2,
    }]
  } : null;
  
  // Bar chart data for average values by type
  const barChartData = summary && summary.avg_by_type ? {
    labels: Object.keys(summary.avg_by_type.Flowrate),
    datasets: [
      {
        label: 'Avg Flowrate',
        data: Object.values(summary.avg_by_type.Flowrate),
        backgroundColor: chartColors.primary,
      },
      {
        label: 'Avg Pressure',
        data: Object.values(summary.avg_by_type.Pressure),
        backgroundColor: chartColors.secondary,
      },
      {
        label: 'Avg Temperature',
        data: Object.values(summary.avg_by_type.Temperature),
        backgroundColor: chartColors.tertiary,
      },
    ]
  } : null;
  
  // Chart options
  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Average Parameters by Equipment Type',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      }
    }
  };
  
  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
      },
    },
  };
  
  // ===== Render =====
  
  return (
    <div>
      {/* Page Header */}
      <h2 style={{ marginBottom: '1.5rem', color: 'var(--gray-800)' }}>
        Dashboard
      </h2>
      
      {/* File Upload Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Upload CSV File</h3>
        </div>
        
        {/* Error/Success Messages */}
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        {/* Drag and Drop Zone */}
        <div
          className={`file-upload ${dragOver ? 'dragover' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p style={{ marginTop: '1rem' }}>Processing file...</p>
            </div>
          ) : (
            <>
              <div className="file-upload-icon">📁</div>
              <p style={{ fontSize: '1.1rem', color: 'var(--gray-700)' }}>
                Drag and drop your CSV file here
              </p>
              <p style={{ color: 'var(--gray-500)', marginTop: '0.5rem' }}>
                or click to browse
              </p>
              <p style={{ 
                color: 'var(--gray-400)', 
                fontSize: '0.875rem', 
                marginTop: '1rem' 
              }}>
                Supported format: CSV with columns (Equipment Name, Type, Flowrate, Pressure, Temperature)
              </p>
            </>
          )}
          
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleInputChange}
            style={{ display: 'none' }}
          />
        </div>
      </div>
      
      {/* Only show data sections if we have data */}
      {summary && (
        <>
          {/* Summary Statistics Cards */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{summary.total_count}</div>
              <div className="stat-label">Total Equipment</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value">{summary.avg_flowrate}</div>
              <div className="stat-label">Avg Flowrate</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value">{summary.avg_pressure}</div>
              <div className="stat-label">Avg Pressure</div>
            </div>
            <div className="stat-card error">
              <div className="stat-value">{summary.avg_temperature}</div>
              <div className="stat-label">Avg Temperature</div>
            </div>
          </div>
          
          {/* Charts Section */}
          <div className="charts-grid">
            {/* Bar Chart - Average values by type */}
            {barChartData && (
              <div className="chart-container">
                <Bar data={barChartData} options={barChartOptions} />
              </div>
            )}
            
            {/* Pie Chart - Type distribution */}
            {pieChartData && (
              <div className="chart-container">
                <Pie data={pieChartData} options={pieChartOptions} />
              </div>
            )}
          </div>
          
          {/* Equipment Data Table */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Equipment Data</h3>
            </div>
            
            {equipment.length > 0 ? (
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Equipment Name</th>
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {equipment.map((eq, index) => (
                      <tr key={eq.id || index}>
                        <td>{eq.name}</td>
                        <td>
                          <span style={{
                            background: 'var(--primary-100)',
                            color: 'var(--primary-700)',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            fontSize: '0.875rem',
                          }}>
                            {eq.equipment_type}
                          </span>
                        </td>
                        <td>{eq.flowrate}</td>
                        <td>{eq.pressure}</td>
                        <td>{eq.temperature}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p style={{ color: 'var(--gray-500)', textAlign: 'center', padding: '2rem' }}>
                Equipment data will appear here after upload
              </p>
            )}
          </div>
        </>
      )}
      
      {/* Empty state when no data uploaded yet */}
      {!summary && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--gray-500)', fontSize: '1.1rem' }}>
            Upload a CSV file to see summary statistics and visualizations
          </p>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;
