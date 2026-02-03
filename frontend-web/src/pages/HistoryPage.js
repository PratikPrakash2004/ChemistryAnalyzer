/**
 * History Page Component
 * 
 * This page displays the user's upload history - specifically the last
 * 5 datasets they've uploaded. For each dataset, users can:
 * 1. See basic info (filename, upload date, equipment count)
 * 2. View the full dataset details
 * 3. Download a PDF report
 * 
 * The "last 5 datasets" limit is enforced by the backend, so we
 * just display whatever the API returns.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDatasets, downloadPDFReport } from '../services/api';

function HistoryPage() {
  // ===== State Management =====
  
  // Store the list of datasets
  const [datasets, setDatasets] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);
  
  // Navigation hook for redirecting to detail page
  const navigate = useNavigate();
  
  // ===== Data Fetching =====
  
  /**
   * Fetch datasets when the component mounts
   * This is called once when the page first loads
   */
  useEffect(() => {
    fetchDatasets();
  }, []); // Empty dependency array = run once on mount
  
  /**
   * Fetch the list of datasets from the API
   */
  const fetchDatasets = async () => {
    setLoading(true);
    setError('');
    
    try {
      const data = await getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error('Error fetching datasets:', err);
      setError('Failed to load history. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // ===== Event Handlers =====
  
  /**
   * Navigate to the dataset detail page
   */
  const handleViewDetails = (datasetId) => {
    navigate(`/dataset/${datasetId}`);
  };
  
  /**
   * Download PDF report for a dataset
   */
  const handleDownloadPDF = async (dataset) => {
    setDownloadingId(dataset.id);
    
    try {
      await downloadPDFReport(dataset.id, `report_${dataset.filename}.pdf`);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloadingId(null);
    }
  };
  
  /**
   * Format date for display
   * Converts ISO date string to a readable format
   */
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  // ===== Render =====
  
  // Show loading state
  if (loading) {
    return (
      <div className="loading-container" style={{ minHeight: '400px' }}>
        <div className="spinner"></div>
        <p style={{ marginTop: '1rem' }}>Loading history...</p>
      </div>
    );
  }
  
  return (
    <div>
      {/* Page Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1.5rem'
      }}>
        <h2 style={{ color: 'var(--gray-800)' }}>
          Upload History
        </h2>
        <button className="btn btn-secondary" onClick={fetchDatasets}>
          🔄 Refresh
        </button>
      </div>
      
      {/* Info box */}
      <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
        📋 Showing your last 5 uploaded datasets. Older uploads are automatically removed.
      </div>
      
      {/* Error message */}
      {error && (
        <div className="alert alert-error">{error}</div>
      )}
      
      {/* Dataset List */}
      {datasets.length === 0 ? (
        // Empty state
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📂</div>
          <h3 style={{ color: 'var(--gray-700)', marginBottom: '0.5rem' }}>
            No uploads yet
          </h3>
          <p style={{ color: 'var(--gray-500)' }}>
            Upload a CSV file from the Dashboard to see it here.
          </p>
          <button 
            className="btn btn-primary" 
            style={{ marginTop: '1.5rem' }}
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </button>
        </div>
      ) : (
        // Dataset items
        <div>
          {datasets.map((dataset) => (
            <div key={dataset.id} className="history-item">
              {/* Dataset Info */}
              <div className="history-info">
                <h3>
                  📄 {dataset.filename}
                </h3>
                <p>
                  Uploaded: {formatDate(dataset.uploaded_at)} • 
                  {' '}{dataset.equipment_count} equipment records
                </p>
                
                {/* Quick summary stats */}
                {dataset.summary && (
                  <div style={{ 
                    marginTop: '0.75rem',
                    display: 'flex',
                    gap: '1rem',
                    flexWrap: 'wrap'
                  }}>
                    <span style={{ 
                      background: 'var(--primary-100)', 
                      color: 'var(--primary-700)',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}>
                      Avg Flow: {dataset.summary.avg_flowrate}
                    </span>
                    <span style={{ 
                      background: 'var(--gray-100)', 
                      color: 'var(--gray-700)',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}>
                      Avg Pressure: {dataset.summary.avg_pressure}
                    </span>
                    <span style={{ 
                      background: 'var(--gray-100)', 
                      color: 'var(--gray-700)',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '4px',
                      fontSize: '0.875rem'
                    }}>
                      Avg Temp: {dataset.summary.avg_temperature}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Action Buttons */}
              <div className="history-actions">
                <button 
                  className="btn btn-primary"
                  onClick={() => handleViewDetails(dataset.id)}
                >
                  View Details
                </button>
                <button 
                  className="btn btn-success"
                  onClick={() => handleDownloadPDF(dataset)}
                  disabled={downloadingId === dataset.id}
                >
                  {downloadingId === dataset.id ? (
                    'Downloading...'
                  ) : (
                    '📥 PDF Report'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default HistoryPage;
