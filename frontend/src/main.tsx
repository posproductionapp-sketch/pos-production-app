import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? '';

function App() {
  const [tenantId, setTenantId] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dark, setDark] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const res = await fetch(`${API}/v1/auth/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({tenant_id:tenantId, username, password}) });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json() as { access_token: string };
      sessionStorage.setItem('prodx_access_token', data.access_token);
      window.location.reload();
    } catch { setError('เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบข้อมูลแล้วลองอีกครั้ง'); }
    finally { setLoading(false); }
  }

  return <main className={dark ? 'app dark' : 'app'}>
    <button className="theme" onClick={() => setDark(v=>!v)} aria-label="Toggle theme">{dark ? '☀' : '☾'}</button>
    <section className="brand-panel" aria-label="PRODX POS brand">
      <div className="mark">P</div><div className="wordmark">PRODX <span>POS</span></div>
      <p>Professional point of sale</p>
    </section>
    <section className="login-card">
      <div className="eyebrow">WELCOME BACK</div><h1>เข้าสู่ระบบ</h1><p className="sub">เข้าสู่ระบบเพื่อจัดการร้านของคุณอย่างมั่นใจ</p>
      <form onSubmit={submit}>
        <label>Tenant ID<input required value={tenantId} onChange={e=>setTenantId(e.target.value)} autoComplete="organization" /></label>
        <label>Username<input required value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username" /></label>
        <label>Password><div className="password"><input required minLength={12} type={show?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} autoComplete="current-password" /><button type="button" onClick={()=>setShow(v=>!v)} aria-label={show?'Hide password':'Show password'}>{show?'ซ่อน':'แสดง'}</button></div></label>
        {error && <div className="error" role="alert">{error}</div>}
        <button className="submit" disabled={loading}>{loading ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'}</button>
      </form>
      <div className="footer">DEVERLOPED BY THODSAWAT</div>
    </section>
  </main>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
