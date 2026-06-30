import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, XCircle, Download, FileJson, Image as ImageIcon, ShieldAlert } from 'lucide-react'

export default function DatasetView({ session }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('relevant') // 'relevant' or 'noise'
  const [selectedImage, setSelectedImage] = useState(null) // Lightbox view
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`${API_URL}/api/jobs/${id}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (!response.ok) {
        if (response.status === 404) throw new Error('Job run not found')
        if (response.status === 403) throw new Error('You do not have permission to view this job')
        throw new Error('Failed to retrieve run details')
      }
      
      const data = await response.json()
      setJob(data.job)
      setImages(data.images)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobDetails()
    
    // Poll details every 3 seconds if job is not completed/failed
    let interval
    if (job && job.status !== 'completed' && job.status !== 'failed') {
      interval = setInterval(fetchJobDetails, 3000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [id, session, job?.status])

  const handleDownloadMetadata = () => {
    const targetImages = images.filter(img => activeTab === 'relevant' ? img.is_relevant : !img.is_relevant)
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(targetImages, null, 2)
    )}`
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', jsonString)
    downloadAnchor.setAttribute('download', `dataset_${job.query.replace(/\s+/g, '_')}_${activeTab}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '100px 0' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
        <ShieldAlert size={48} style={{ color: 'var(--error-color)', marginBottom: '16px' }} />
        <h3 style={{ marginBottom: '12px' }}>Execution Error</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>{error}</p>
        <Link to="/" className="btn btn-primary">
          <ArrowLeft size={16} /> Return to Dashboard
        </Link>
      </div>
    )
  }

  const relevantImages = images.filter(img => img.is_relevant)
  const noiseImages = images.filter(img => !img.is_relevant)
  const displayImages = activeTab === 'relevant' ? relevantImages : noiseImages

  return (
    <div>
      {/* Header breadcrumb */}
      <div style={{ marginBottom: '24px' }}>
        <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px' }}>
          <ArrowLeft size={14} /> Back to Dashboard
        </Link>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Dataset: "{job.query}"</h1>
            <p style={{ color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.85rem' }}>Job ID: {job.id}</p>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={handleDownloadMetadata} className="btn btn-secondary" disabled={displayImages.length === 0}>
              <FileJson size={16} /> Export Links JSON
            </button>
          </div>
        </div>
      </div>

      {/* Progress status card if active */}
      {job.status !== 'completed' && job.status !== 'failed' && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px', borderLeft: '4px solid var(--accent-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.95rem' }}>
            <span>Pipeline is running: <strong>{job.status}...</strong></span>
            <span style={{ fontWeight: 600, color: 'var(--accent-color)' }}>{job.progress}%</span>
          </div>
          <div className="progress-container">
            <div className="progress-fill" style={{ width: `${job.progress}%` }}></div>
          </div>
        </div>
      )}

      {/* Run metrics overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>Status</div>
          <strong style={{ fontSize: '1.25rem' }}>{job.status.toUpperCase()}</strong>
        </div>
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>Scraped Candidate Images</div>
          <strong style={{ fontSize: '1.25rem' }}>{images.length} files</strong>
        </div>
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>CLIP Relevant Matches</div>
          <strong style={{ fontSize: '1.25rem', color: 'var(--success-color)' }}>{relevantImages.length} files</strong>
        </div>
      </div>

      {/* Tab Selectors */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px', gap: '8px' }}>
        <button 
          onClick={() => setActiveTab('relevant')} 
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            color: activeTab === 'relevant' ? 'var(--text-primary)' : 'var(--text-secondary)',
            borderBottom: activeTab === 'relevant' ? '2px solid var(--accent-color)' : 'none',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <CheckCircle2 size={16} style={{ color: 'var(--success-color)' }} />
          Curated Dataset ({relevantImages.length})
        </button>
        
        <button 
          onClick={() => setActiveTab('noise')} 
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            color: activeTab === 'noise' ? 'var(--text-primary)' : 'var(--text-secondary)',
            borderBottom: activeTab === 'noise' ? '2px solid var(--accent-color)' : 'none',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <XCircle size={16} style={{ color: 'var(--error-color)' }} />
          Excluded Noise ({noiseImages.length})
        </button>
      </div>

      {/* Image Gallery Grid */}
      {displayImages.length === 0 ? (
        <div className="glass-panel" style={{ padding: '80px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <ImageIcon size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <p>No images found in this segment.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
          gap: '24px'
        }}>
          {displayImages.map((img) => (
            <div 
              key={img.id} 
              className="glass-panel" 
              style={{ overflow: 'hidden', cursor: 'zoom-in', position: 'relative' }}
              onClick={() => setSelectedImage(img)}
            >
              {/* Image Aspect Box */}
              <div style={{ width: '100%', paddingBottom: '75%', position: 'relative', background: 'rgba(0,0,0,0.2)' }}>
                <img 
                  src={img.image_url} 
                  alt={job.query} 
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    transition: 'transform 0.3s ease'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                  onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                />
              </div>
              
              {/* Confidence Badge */}
              <div style={{
                padding: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '0.8rem',
                borderTop: '1px solid var(--border-color)'
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>CLIP Match</span>
                <strong style={{ color: img.is_relevant ? 'var(--success-color)' : 'var(--error-color)' }}>
                  {(img.confidence * 100).toFixed(1)}%
                </strong>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Lightbox / Zoom modal */}
      {selectedImage && (
        <div 
          onClick={() => setSelectedImage(null)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(4, 6, 10, 0.9)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            cursor: 'zoom-out',
            padding: '40px'
          }}
        >
          <div style={{ position: 'relative', maxWidth: '90%', maxHeight: '90%' }} onClick={(e) => e.stopPropagation()}>
            <img 
              src={selectedImage.image_url} 
              alt={job.query}
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
              }}
            />
            <div style={{ marginTop: '16px', display: 'flex', justify: 'between', alignItems: 'center', color: '#ffffff', width: '100%', justifyContent: 'space-between' }}>
              <div>
                <strong>Label: "{job.query}"</strong>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Confidence score: {(selectedImage.confidence * 100).toFixed(2)}%
                </div>
              </div>
              <a 
                href={selectedImage.image_url} 
                target="_blank" 
                rel="noreferrer" 
                className="btn btn-primary"
                style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              >
                <Download size={14} /> Open Original URL
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
