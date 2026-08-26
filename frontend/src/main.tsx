import { FormEvent, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [tenantId, setTenantId] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [authenticated, setAuthenticated] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenantId, username, password }),
      })
      if (!response.ok) throw new Error('Invalid credentials')
      await response.json()
      setAuthenticated(true)
    } catch {
      setError('เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบข้อมูลอีกครั้ง')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <section className="brand-panel">
        <div className="brand-mark">P</div>
        <p className="eyebrow">POS PRODUCTION</p>
        <h1>ขายง่าย<br />ควบคุมแม่นยำ</h1>
        <p className="brand-copy">ระบบหน้าร้านสำหรับยอดขาย สต็อก เงินสด และการทำงานแบบออฟไลน์ที่เชื่อถือได้</p>
        <div className="status-pill"><span /> ระบบพร้อมใช้งาน</div>
      </section>

      <section className="form-panel">
        <div className="form-card">
          <p className="eyebrow">WELCOME BACK</p>
          <h2>{authenticated ? 'เข้าสู่ระบบสำเร็จ' : 'เข้าสู่ระบบ'}</h2>
          <p className="muted">{authenticated ? 'Authentication boundary พร้อมใช้งานสำหรับขั้นตอนถัดไป' : 'ลงชื่อเข้าใช้เพื่อเริ่มงานที่หน้าร้าน'}</p>
          {!authenticated && <form onSubmit={submit}>
            <label>Tenant ID<input value={tenantId} onChange={(e) => setTenantId(e.target.value)} required autoComplete="organization" /></label>
            <label>ชื่อผู้ใช้<input value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username" /></label>
            <label>รหัสผ่าน<input type="password" minLength={12} value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" /></label>
            {error && <p className="error" role="alert">{error}</p>}
            <button disabled={loading}>{loading ? 'กำลังตรวจสอบ…' : 'เข้าสู่ระบบ'}</button>
          </form>}
          <p className="security-note">Token persistence จะถูกออกแบบพร้อม session/offline architecture โดยไม่เก็บ bearer token ใน localStorage</p>
        </div>
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
