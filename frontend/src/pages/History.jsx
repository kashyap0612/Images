import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, Eye, FileText, LayoutList } from 'lucide-react'

export default function History({ session }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch(`${API_URL}/api/jobs`, {
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        })
        if (!response.ok) throw new Error('Could not fetch jobs list')
        const data = await response.json()
        setJobs(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchJobs()
  }, [session])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status) => {
    const cleanStatus = status.toLowerCase()
    if (cleanStatus.includes("scraping") || cleanStatus.includes("searching") || cleanStatus.includes("saving")) {
      return <span className="badge badge-running">Processing</span>
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
        <h1 style={{ fontSize: '2.25rem', marginBottom: '8px' }}>Pipeline History Logs</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Review all past dataset execution runs, status metrics, and image tallies.</p>
      </div>

      {error && (
        <div style={{ color: 'var(--error-color)', fontSize: '0.9rem', marginBottom: '24px', padding: '12px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '8px' }}>
          {error}
        </div>
      )}

      <div className="glass-panel" style={{ padding: '32px' }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <LayoutList size={20} style={{ color: 'var(--accent-color)' }} />
          Execution Log
        </h3>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
            <div className="spinner"></div>
          </div>
        ) : jobs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)' }}>
            No execution logs found. Create your first dataset run in the dashboard!
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Target Query</th>
                  <th>Created Date</th>
                  <th>Job ID</th>
                  <th>Status</th>
                  <th>Relevant Count</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/dataset/${job.id}`)}>
                    <td style={{ fontWeight: 600 }}>"{job.query}"</td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
                        <Calendar size={14} />
                        {formatDate(job.created_at)}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {job.id.substring(0, 8)}...
                    </td>
                    <td>{getStatusBadge(job.status)}</td>
                    <td style={{ fontWeight: 600, color: job.total_images > 0 ? 'var(--success-color)' : 'var(--text-muted)' }}>
                      {job.total_images} files
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                        <Eye size={12} />
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
