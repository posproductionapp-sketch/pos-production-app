import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? '';

type Product = { name: string; price: string; category: string };
const products: Product[] = [
  { name: 'Espresso', price: '65.00', category: 'เครื่องดื่ม' },
  { name: 'Americano', price: '75.00', category: 'เครื่องดื่ม' },
  { name: 'Latte', price: '85.00', category: 'เครื่องดื่ม' },
  { name: 'Croissant', price: '95.00', category: 'เบเกอรี่' },
];

function Login({ onLogin }: { onLogin: () => void }) {
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
      const res = await fetch(`${API}/v1/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tenant_id: tenantId, username, password }) });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json() as { access_token: string };
      sessionStorage.setItem('prodx_access_token', data.access_token);
      onLogin();
    } catch { setError('เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบข้อมูลแล้วลองอีกครั้ง'); }
    finally { setLoading(false); }
  }

  return <main className={dark ? 'app dark' : 'app'}>
    <button className="theme" onClick={() => setDark(v => !v)} aria-label="Toggle theme">{dark ? '☀' : '☾'}</button>
    <section className="brand-panel" aria-label="PRODX POS brand">
      <div className="mark">P</div><div className="wordmark">PRODX <span>POS</span></div>
      <p>Professional point of sale</p>
    </section>
    <section className="login-card">
      <div className="eyebrow">WELCOME BACK</div><h1>เข้าสู่ระบบ</h1><p className="sub">เข้าสู่ระบบเพื่อจัดการร้านของคุณอย่างมั่นใจ</p>
      <form onSubmit={submit}>
        <label>Tenant ID<input required value={tenantId} onChange={e => setTenantId(e.target.value)} autoComplete="organization" /></label>
        <label>Username<input required value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" /></label>
        <label>Password<div className="password"><input required minLength={12} type={show ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" /><button type="button" onClick={() => setShow(v => !v)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? 'ซ่อน' : 'แสดง'}</button></div></label>
        {error && <div className="error" role="alert">{error}</div>}
        <button className="submit" disabled={loading}>{loading ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'}</button>
      </form>
      <div className="footer">DEVERLOPED BY THODSAWAT</div>
    </section>
  </main>;
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [query, setQuery] = useState('');
  const [cart, setCart] = useState<Product[]>([]);
  const filtered = products.filter(p => `${p.name} ${p.category}`.toLowerCase().includes(query.toLowerCase()));
  const total = cart.reduce((sum, p) => sum + Number(p.price), 0);
  return <main className="dashboard">
    <header className="topbar"><div className="brand-inline"><span className="mark small">P</span><strong>PRODX POS</strong></div><div className="top-actions"><span className="shift">● Shift Open</span><button onClick={onLogout}>ออกจากระบบ</button></div></header>
    <section className="dash-content"><div className="dash-head"><div><span className="eyebrow">TODAY</span><h1>หน้าขาย</h1><p>พร้อมให้บริการ • เลือกสินค้าเพื่อเริ่มรายการ</p></div><div className="stat"><span>ยอดขายวันนี้</span><strong>฿12,450.00</strong></div></div>
      <div className="pos-grid"><section className="catalog"><div className="search-row"><input aria-label="ค้นหาสินค้า" placeholder="ค้นหาสินค้า…" value={query} onChange={e => setQuery(e.target.value)} /><div className="chips"><button className="active">ทั้งหมด</button><button>เครื่องดื่ม</button><button>เบเกอรี่</button></div></div><div className="product-grid">{filtered.map(p => <button className="product" key={p.name} onClick={() => setCart(c => [...c, p])}><span className="product-icon">{p.name[0]}</span><strong>{p.name}</strong><small>{p.category}</small><b>฿{p.price}</b></button>)}</div></section>
        <aside className="cart"><div className="cart-head"><h2>รายการขาย</h2><span>{cart.length} รายการ</span></div>{cart.length === 0 ? <div className="empty">ยังไม่มีสินค้า<br/><small>แตะสินค้าเพื่อเพิ่มลงรายการ</small></div> : <div className="cart-lines">{cart.map((p, i) => <div className="cart-line" key={`${p.name}-${i}`}><span>{p.name}</span><strong>฿{p.price}</strong></div>)}</div>}<div className="cart-total"><span>รวม</span><strong>฿{total.toFixed(2)}</strong></div><button className="submit checkout" disabled={!cart.length}>ชำระเงิน</button></aside>
      </div></section>
  </main>;
}

function App() { const [loggedIn, setLoggedIn] = useState(Boolean(sessionStorage.getItem('prodx_access_token'))); return loggedIn ? <Dashboard onLogout={() => { sessionStorage.removeItem('prodx_access_token'); setLoggedIn(false); }} /> : <Login onLogin={() => setLoggedIn(true)} />; }
createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
