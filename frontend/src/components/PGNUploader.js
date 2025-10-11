import React, { useState } from 'react';
import axios from 'axios';
import './PGNUploader.css';

const PGNUploader = () => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setAnalysis(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a PGN file first');
      return;
    }

    const formData = new FormData();
    formData.append('pgn_file', file);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/analyze-pgn',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setAnalysis(response.data);
      console.log('Analysis result:', response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error analyzing PGN file. Please try again.'
      );
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setAnalysis(null);
    setError(null);
  };

  return (
    <div className="pgn-uploader">
      <div className="container">
        <h1>♟️ Chess Game Analyzer</h1>
        <p className="subtitle">Upload your PGN file to get detailed game analysis</p>

        <div className="upload-section">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="pgn-file"
              accept=".pgn"
              onChange={handleFileChange}
              disabled={loading}
            />
            <label htmlFor="pgn-file" className="file-label">
              {file ? `📁 ${file.name}` : '📂 Choose PGN File'}
            </label>
          </div>

          <button 
            onClick={handleUpload} 
            disabled={loading || !file}
            className="analyze-button"
          >
            {loading ? '⏳ Analyzing...' : '🔍 Analyze Game'}
          </button>

          {(file || analysis) && (
            <button 
              onClick={handleReset} 
              className="reset-button"
              disabled={loading}
            >
              🔄 Reset
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {analysis && (
          <div className="analysis-result">
            <h2>✅ {analysis.game_summary}</h2>
            
            <div className="result-section">
              <h3>📊 Analysis Details:</h3>
              <pre className="json-output">
                {JSON.stringify(analysis, null, 2)}
              </pre>
            </div>

            {analysis.pgn_content && (
              <div className="result-section">
                <h3>📋 PGN Content:</h3>
                <pre className="pgn-content">
                  {analysis.pgn_content}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PGNUploader;