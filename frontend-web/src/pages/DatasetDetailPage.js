/**
 * Dataset Detail Page Component
 * 
 * This page shows the complete details of a single dataset.
 * Users arrive here by clicking "View Details" on a history item.
 * 
 * It displays:
 * 1. Dataset metadata (filename, upload date)
 * 2. Summary statistics
 * 3. Visual charts (same as Dashboard)
 * 4. Full equipment table
 * 5. Option to download PDF report
 * 
 * The dataset ID comes from the URL parameter (e.g., /dataset/5)
 * We use React Router's useParams hook to extract it.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
import { getDatasetDetail, downloadPDFReport } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function DatasetDetailPage() {
  // ===== Hooks =====
  
  // Get the dataset ID from the URL
  const { id } = useParams();
  
  // Navigation hook for back button
  const navigate = useNavigate();
  
  // ===== State Management =====
  
  // Store the dataset data
  const [dataset, setDataset] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);
  
  // ===== Data Fetching =====
  
  /**
   * Fetch the dataset details when the page loads or ID changes
   */
  useEffect(() => {
    fetchDatasetDetail();
  }, [id]); // Re-fetch if ID changes
  
  const fetchDatasetDetail = async () => {
    setLoading(true);
    setError('');
    
    try {
      const data = await getDatasetDetail(id);
      setDataset(data);
    } catch (err) {
      console.error('Error fetching dataset:', err);
      if (err.response && err.response.status === 404) {
        setError('Dataset not found. It may have been deleted.');
      } else {
        setError('Failed to load dataset details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // ===== Event Handlers =====
  
  /**
   * Download PDF report
   */
  const handleDownloadPDF = async () => {
    setDownloading(true);
    
    try {
      await downloadPDFReport(id, `report_${dataset.filename}.pdf`);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };
  
  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  // ===== Chart Configuration =====
  
  // Blue theme colors (Version A)
  const chartColors = {
    primary: 'rgba(37, 99, 235, 0.8)',
    secondary: 'rgba(16, 185, 129, 0.8)',
    tertiary: 'rgba(245, 158, 11, 0.8)',
    quaternary: 'rgba(239, 68, 68, 0.8)',
    quinary: 'rgba(139, 92, 246, 0.8)',
    senary: 'rgba(6, 182, 212, 0.8)',
  };
  
  // Prepare chart data only if we have a dataset
  const summary = dataset?.summary;
  
  const pieChartData = summary ? {
    labels: Object.keys(summary.type_distribution || {}),
    datasets: [{
      data: Object.values(summary.type_distribution || {}),
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
  
  const barChartData = summary && summary.avg_by_type ? {
    labels: Object.keys(summary.avg_by_type.Flowrate || {}),
    datasets: [
      {
        label: 'Avg Flowrate',
        data: Object.values(summary.avg_by_type.Flowrate || {}),
        backgroundColor: chartColors.primary,
      },
      {
        label: 'Avg Pressure',
        data: Object.values(summary.avg_by_type.Pressure || {}),
        backgroundColor: chartColors.secondary,
      },
      {
        label: 'Avg Temperature',
        data: Object.values(summary.avg_by_type.Temperature || {}),
        backgroundColor: chartColors.tertiary,
      },
    ]
  } : null;
  
  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Average Parameters by Equipment Type' },
    },
    scales: {
      y: { beginAtZero: true }
    }
  };
  
  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'right' },
      title: { display: true, text: 'Equipment Type Distribution' },
    },
  };
  
  // ===== Render =====
  
  // Show loading state
  if (loading) {
    return (
      <div className="loading-container" style={{ minHeight: '400px' }}>
        <div className="spinner"></div>
        <p style={{ marginTop: '1rem' }}>Loading dataset...</p>
      </div>
    );
  }
  
  // Show error state
  if (error) {
    return (
      <div>
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-secondary" onClick={() => navigate('/history')}>
          ← Back to History
        </button>
      </div>
    );
  }
  
  // Main content
  return (
    <div>
      {/* Page Header with Back Button */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <button 
            className="btn btn-secondary" 
            onClick={() => navigate('/history')}
            style={{ marginBottom: '0.5rem' }}
          >
            ← Back to History
          </button>
          <h2 style={{ color: 'var(--gray-800)', marginTop: '0.5rem' }}>
            📄 {dataset.filename}
          </h2>
          <p style={{ color: 'var(--gray-500)' }}>
            Uploaded: {formatDate(dataset.uploaded_at)}
          </p>
        </div>
        
        <button 
          className="btn btn-success"
          onClick={handleDownloadPDF}
          disabled={downloading}
        >
          {downloading ? 'Generating PDF...' : '📥 Download PDF Report'}
        </button>
      </div>
      
      {/* Summary Statistics Cards */}
      {summary && (
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
      )}
      
      {/* Min/Max Statistics */}
      {summary && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Parameter Ranges</h3>
          </div>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}>
            <div>
              <strong style={{ color: 'var(--gray-700)' }}>Flowrate</strong>
              <p style={{ color: 'var(--gray-500)' }}>
                Min: {summary.min_flowrate} • Max: {summary.max_flowrate}
              </p>
            </div>
            <div>
              <strong style={{ color: 'var(--gray-700)' }}>Pressure</strong>
              <p style={{ color: 'var(--gray-500)' }}>
                Min: {summary.min_pressure} • Max: {summary.max_pressure}
              </p>
            </div>
            <div>
              <strong style={{ color: 'var(--gray-700)' }}>Temperature</strong>
              <p style={{ color: 'var(--gray-500)' }}>
                Min: {summary.min_temperature} • Max: {summary.max_temperature}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Charts Section */}
      <div className="charts-grid">
        {barChartData && (
          <div className="chart-container">
            <Bar data={barChartData} options={barChartOptions} />
          </div>
        )}
        
        {pieChartData && (
          <div className="chart-container">
            <Pie data={pieChartData} options={pieChartOptions} />
          </div>
        )}
      </div>
      
      {/* Equipment Data Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            Equipment Data ({dataset.equipment?.length || 0} records)
          </h3>
        </div>
        
        {dataset.equipment && dataset.equipment.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Equipment Name</th>
                  <th>Type</th>
                  <th>Flowrate</th>
                  <th>Pressure</th>
                  <th>Temperature</th>
                </tr>
              </thead>
              <tbody>
                {dataset.equipment.map((eq, index) => (
                  <tr key={eq.id || index}>
                    <td style={{ color: 'var(--gray-400)' }}>{index + 1}</td>
                    <td><strong>{eq.name}</strong></td>
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
            No equipment data available
          </p>
        )}
      </div>
    </div>
  );
}

export default DatasetDetailPage;
