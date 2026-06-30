import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, Search, RefreshCw, Layers } from 'lucide-react'

export default function Dashboard({ session }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [jobs, setJobs] = useState([])
  const [fetching, setFetching] = useState(true)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_URL}/api/jobs`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      if (!response.ok) throw new Error('Failed to retrieve background tasks')
      const data = await response.json()
      setJobs(data)
    } catch (err) {
      console.error(err)
      setError('Connection to backend API failed. Make sure your FastAPI server is running.')
    } finally {
      setFetching(false)
    }
  }

  useEffect(() => {
    fetchJobs()
    // Poll active jobs every 5 seconds to keep dashboard state fresh
    const interval = setInterval(fetchJobs, 5000)
    return () => clearInterval(interval)
  }, [session])

  const handleStartJob = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_URL}/api/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ query: query.trim() })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to submit pipeline job')
      }

      const data = await response.json()
      setQuery('')
      // Immediately refresh jobs and redirect to the job's detail page
      fetchJobs()
      navigate(`/dataset/${data.job.id}`)
    } catch (err) {
      setError(err.message || 'Error triggering job')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const cleanStatus = status.toLowerCase()
    if (cleanStatus.includes("scraping") || cleanStatus.includes("searching") || cleanStatus.includes("saving")) {
      return <span className="badge badge-running">Processing ({status})</span>
    }
    switch (cleanStatus) {
      case 'completed': return <span className="badge badge-completed">Completed</span>
      case 'failed': return <span className="badge badge-failed">Failed</span>
      case 'pending': return <span className="badge badge-pending">Pending</span>
      default: return <span className="badge badge-running">{status}</span>
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2.25rem', marginBottom: '8px' }}>Model Curation Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Trigger crawling engines and CLIP classifiers to build evaluation datasets.</p>
      </div>

      {error && (
        <div style={{ color: 'var(--error-color)', fontSize: '0.9rem', marginBottom: '24px', padding: '12px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.15)', borderRadius: '8px' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '32px', marginBottom: '40px' }}>
        {/* Trigger Search Panel */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PlusCircle size={20} style={{ color: 'var(--accent-color)' }} />
            Create Labeled Dataset
          </h3>
          <form onSubmit={handleStartJob} style={{ display: 'flex', gap: '16px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={18} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="text"
                className="input-field"
                placeholder="Enter target dataset label (e.g. luxury car, golden retriever, cell biology diagram)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{ paddingLeft: '46px' }}
                disabled={loading}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading} style={{ minWidth: '160px' }}>
              {loading ? (
                <div className="spinner" style={{ width: '18px', height: '18px' }}></div>
              ) : (
                'Start Engine'
              )}
            </button>
          </form>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '10px' }}>
            This query will search Google, download matching images from page DOMs, and categorize them automatically via CLIP.
          </p>
        </div>

        {/* Live Tasks Panel */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'center', marginBottom: '20px', width: '100%', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={20} style={{ color: 'var(--accent-color)' }} />
              Running Pipelines
            </h3>
            <button onClick={fetchJobs} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
              <RefreshCw size={12} />
              Reload
            </button>
          </div>

          {fetching ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
              <div className="spinner"></div>
            </div>
          ) : jobs.filter(j => j.status !== 'completed' && j.status !== 'failed').length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-secondary)' }}>
              No active scraping tasks. Start a new run above to populate the queue!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {jobs.filter(j => j.status !== 'completed' && j.status !== 'failed').map((job) => (
                <div 
                  key={job.id} 
                  className="glass-panel" 
                  onClick={() => navigate(`/dataset/${job.id}`)}
                  style={{ padding: '20px', cursor: 'pointer', hover: 'background: rgba(255,255,255,0.02)' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div>
                      <strong style={{ fontSize: '1.05rem' }}>Query: "{job.query}"</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Job ID: {job.id}
                      </div>
                    </div>
                    {getStatusBadge(job.status)}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div className="progress-container" style={{ flex: 1 }}>
                      <div className="progress-fill" style={{ width: `${job.progress}%` }}></div>
                    </div>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-color)' }}>{job.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
