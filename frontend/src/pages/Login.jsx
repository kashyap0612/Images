import React, { useState } from 'react'
import { supabase } from '../supabase'
import { KeyRound, Mail, Sparkles } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [useOtp, setUseOtp] = useState(false) // Toggle between Password and OTP Mode

  const handleAuth = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')

    try {
      if (useOtp) {
        // Send a magic link / OTP login email
        const { error } = await supabase.auth.signInWithOtp({ 
          email,
          options: {
            emailRedirectTo: window.location.origin
          }
        })
        if (error) throw error
        setMessage('Check your email inbox for the login link!')
      } else {
        // Standard password authentication
        // Attempt log in first
        let { error: signInError } = await supabase.auth.signInWithPassword({ email, password })
        
        if (signInError) {
          // If user doesn't exist, automatically sign them up (dev helper shortcut)
          if (signInError.message.includes("Invalid login credentials")) {
            const { error: signUpError } = await supabase.auth.signUp({ email, password })
            if (signUpError) throw signUpError
            setMessage('Account registered! You are now logged in.')
          } else {
            throw signInError
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card glass-panel">
        <div className="auth-header">
          <h2 style={{ fontSize: '1.75rem', marginBottom: '8px' }}>AutoDataset</h2>
          <p>Sign in to start curating machine learning training data</p>
        </div>

        {error && (
          <div style={{ color: 'var(--error-color)', fontSize: '0.9rem', marginBottom: '16px', padding: '10px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '6px' }}>
            {error}
          </div>
        )}

        {message && (
          <div style={{ color: 'var(--success-color)', fontSize: '0.9rem', marginBottom: '16px', padding: '10px', background: 'rgba(16, 185, 129, 0.08)', borderRadius: '6px' }}>
            {message}
          </div>
        )}

        <form onSubmit={handleAuth}>
          <div className="auth-form-group">
            <label className="auth-label">Email Address</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="email" 
                className="input-field" 
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '38px' }}
                required
              />
            </div>
          </div>

          {!useOtp && (
            <div className="auth-form-group">
              <label className="auth-label">Password</label>
              <div style={{ position: 'relative' }}>
                <KeyRound size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input 
                  type="password" 
                  className="input-field" 
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ paddingLeft: '38px' }}
                  required={!useOtp}
                />
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                If you don't have an account, entering a password will register one automatically.
              </p>
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '12px', marginTop: '10px' }}
            disabled={loading}
          >
            {loading ? (
              <div className="spinner" style={{ width: '18px', height: '18px' }}></div>
            ) : useOtp ? (
              <>
                <Sparkles size={16} />
                Send Magic OTP Link
              </>
            ) : (
              'Sign In / Register'
            )}
          </button>
        </form>

        <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
          <button 
            onClick={() => { setUseOtp(!useOtp); setError(''); setMessage(''); }} 
            className="btn btn-secondary" 
            style={{ width: '100%', fontSize: '0.85rem' }}
          >
            {useOtp ? 'Use Password Sign In' : 'Use Passwordless Email OTP'}
          </button>
        </div>
      </div>
    </div>
  )
}
