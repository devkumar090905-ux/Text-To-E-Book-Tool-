import React, { useState } from 'react';
import { Upload, Settings, CheckCircle, FileText, Download, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [file, setFile] = useState(null);
  const [fontSize, setFontSize] = useState(12);
  const [margin, setMargin] = useState(25);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, success, error
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleFormat = async (mode = 'full') => {
    if (!file) return;

    setStatus('processing');
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('font_size', fontSize);
    formData.append('margin', margin);
    formData.append('mode', mode);

    const apiUrl = '/api/format';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const prefix = mode === 'index' ? 'index_' : 'formatted_';
        a.download = `${prefix}${file.name.split('.')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setStatus('success');
      } else {
        const errData = await response.json();
        throw new Error(errData.error || 'Formatting failed');
      }
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="glass-container">
      <header>
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Automate Formatting
        </motion.h1>
        <p className="subtitle">Premium AI Book Formatter for Hindi & English</p>
      </header>

      <main className="main-layout">
        <section className="upload-section">
          <div className={`drop-zone ${file ? 'active' : ''}`} onClick={() => document.getElementById('fileInput').click()}>
            <input 
              type="file" 
              id="fileInput" 
              hidden 
              onChange={handleFileChange} 
              accept=".md,.docx,.txt"
            />
            {file ? (
              <div className="file-info">
                <FileText className="icon" size={48} color="#8b5cf6" style={{ margin: '0 auto 16px' }} />
                <h3>{file.name}</h3>
                <p>{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            ) : (
              <div className="upload-prompt">
                <Upload className="icon" size={48} color="rgba(255,255,255,0.2)" style={{ margin: '0 auto 16px' }} />
                <h3>Upload Your Book</h3>
                <p>Drag and drop or click to browse</p>
                <p style={{ fontSize: '0.8rem', marginTop: '8px' }}>Supports .md, .docx, .txt</p>
              </div>
            )}
          </div>

          <AnimatePresence>
            {status === 'success' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="status-card"
              >
                <CheckCircle size={20} />
                Successfully generated! Downloading PDF...
              </motion.div>
            )}
            {status === 'error' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="status-card" 
                style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444' }}
              >
                Error: {error}
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        <section className="settings-section">
          <div className="setting-header" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Settings size={20} color="#8b5cf6" />
            <h3 style={{ fontSize: '1.2rem' }}>Style Settings</h3>
          </div>

          <div className="setting-item">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <label>Body Font Size</label>
              <span style={{ fontSize: '0.9rem', color: '#8b5cf6' }}>{fontSize}px</span>
            </div>
            <input 
              type="range" 
              min="10" 
              max="24" 
              value={fontSize} 
              onChange={(e) => setFontSize(parseInt(e.target.value))} 
            />
          </div>

          <div className="setting-item">
             <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <label>Page Margins</label>
              <span style={{ fontSize: '0.9rem', color: '#8b5cf6' }}>{margin}mm</span>
            </div>
            <input 
              type="range" 
              min="10" 
              max="50" 
              value={margin} 
              onChange={(e) => setMargin(parseInt(e.target.value))} 
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', flexDirection: 'column' }}>
            <button 
              className="primary-btn" 
              disabled={!file || status === 'processing'}
              onClick={() => handleFormat('full')}
            >
              {status === 'processing' ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <Loader2 className="spinner" size={20} />
                  Processing PDF...
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <Download size={20} />
                  Generate & Download PDF
                </div>
              )}
            </button>

            <button 
              className="secondary-btn" 
              disabled={!file || status === 'processing'}
              onClick={() => handleFormat('index')}
            >
               <FileText size={20} color="#8b5cf6" />
               Generate Book Index
            </button>
          </div>
        </section>
      </main>

      <footer style={{ marginTop: '40px', textAlign: 'center', color: 'rgba(255,255,255,0.1)', fontSize: '0.8rem' }}>
        &copy; 2026 Automate Formatting Engine. All rights reserved.
      </footer>

      <style>{`
        .spinner {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
