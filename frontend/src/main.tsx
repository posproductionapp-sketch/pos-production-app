import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? '';

type Product = { name: string; price: string; category: string; stock: number };

const products: Product[] = [
  { name: 'น้ำดื่ม 600ml', price: '10.00', category: 'เครื่องดื่ม', stock: 120 },
  { name: 'กาแฟพร้อมดื่ม', price: '35.00', category: 'เครื่องดื่ม', stock: 45 },
  { name: 'ขนมปัง', price: '20.00', category: 'เบเกอรี่', stock: 60 },
  { name: 'น้ำอัดลม 325ml', price: '15.00', category: 'เครื่องดื่ม', stock: 100 },
  { name: 'นม UHT 1L', price: '35.00', category: 'เครื่องดื่ม', stock: 80 },
  { name: 'ขนมปังไส้สตรอว์เบอร์รี่', price: '25.00', category: 'เบเกอรี่', stock: 60 },
];

function Logo({ compact = false }: { compact?: boolean }) {
  return <div className={compact ? 'logo logo-compact' : 'logo'} aria-label="PRODX POS">
    <svg viewBox="0 0 52 52" role="img" aria-hidden="true">
      <path d="M8 38V14c0-5 3-8 8-8h12c9 0 15 5 15 13s-6 13-15 13H18v6H8Zm10-16h10c3 0 5-1 5-3s-2-3-5-3H18v6Z" />
      <path className="logo-cut" d="M8 38 20 25h10L18 38H8Z" />
    </svg>
    {!compact && <span><strong>PROD<span>X</span></strong><small>POS</small></span>}
  </div>;
}

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
      const res = await fetch(`${API}/v1/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenantId, username, password }),
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json() as { access_token: string };
      sessionStorage.setItem('prodx_access_token', data.access_token);
      onLogin();
    } catch { setError('เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบข้อมูลแล้วลองอีกครั้ง'); }
    finally { setLoading(false); }
  }

  return <main className={dark ? 'app dark' : 'app'}>
    <button className="theme" onClick={() => setDark(v => !v)} aria-label="Toggle theme">{dark ? '☀' : '☾'}</button>
    <section className="brand-panel">
      <div className="brand-copy"><Logo /><span className="brand-kicker">PROFESSIONAL POS SYSTEM</span><p>Modern <i /> Premium <i /> Reliable</p></div>
      <div className="brand-visual" aria-hidden="true"><div className="terminal"><div className="terminal-screen">PRODX POS<div className="terminal-lines"><b /><b /><b /></div></div><div className="terminal-base" /></div><div className="glow-orb" /></div>
      <div className="brand-features"><span>◉ Secure</span><span>◉ Offline Ready</span><span>◉ Multi-store</span></div>
    </section>
    <section className="login-card">
      <div className="eyebrow">WELCOME BACK</div><h1>เข้าสู่ระบบ</h1><p className="sub">เข้าสู่ระบบเพื่อจัดการร้านของคุณอย่างมั่นใจ</p>
      <form onSubmit={submit}>
        <label>Tenant ID<input required value={tenantId} onChange={e => setTenantId(e.target.value)} autoComplete="organization" placeholder="รหัสร้าน / องค์กร" /></label>
        <label>Username<input required value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" placeholder="ชื่อผู้ใช้งาน" /></label>
        <label>Password><div className="password"><input required minLength={12} type={show ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" placeholder="รหัสผ่านอย่างน้อย 12 ตัวอักษร" /><button type="button" onClick={() => setShow(v => !v)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? 'ซ่อน' : 'แสดง'}</button></div></label>
        <div className="login-meta"><label className="check"><input type="checkbox" /> <span>จดจำอุปกรณ์</span></label><button type="button" className="link">ลืมรหัสผ่าน?</button></div>
        {error && <div className="error" role="alert">{error}</div>}
        <button className="submit" disabled={loading}>{loading ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'}</button>
      </form>
      <div className="alt-login"><span>หรือเข้าสู่ระบบด้วย</span><div><button type="button">◉ Fingerprint</button><button type="button">⌘ PIN</button></div></div>
      <div className="footer">DEVELOPED BY <strong>THODSAWAT</strong></div>
    </section>
  </main>;
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [query, setQuery] = useState('');
  const [cart, setCart] = useState<Product[]>([]);
  const filtered = products.filter(p => `${p.name} ${p.category}`.toLowerCase().includes(query.toLowerCase()));
  const total = cart.reduce((sum, p) => sum + Number(p.price), 0);

  return <main className="dashboard">
    <header className="topbar"><Logo /><div className="top-actions"><span className="online"><i /> Shift Open</span><span className="store">Store A ▾</span><button onClick={onLogout}>ออกจากระบบ</button></div></header>
    <div className="dashboard-layout">
      <aside className="sidebar"><nav>{[['⌂','Dashboard'],['▣','Sales'],['◈','Products'],['◫','Inventory'],['♙','Customers'],['⌁','Reports'],['◉','Cash & Shift'],['⚙','Settings']].map(([icon, label], i) => <button className={i === 0 ? 'nav-active' : ''} key={label}><span>{icon}</span>{label}</button>)}</nav><div className="profile"><span className="avatar">A</span><div><b>Admin</b><small>Store A</small></div><span>•••</span></div></aside>
      <section className="dash-content"><div className="dash-head"><div><span className="eyebrow">OVERVIEW</span><h1>สวัสดี, Admin 👋</h1><p>ภาพรวมร้านของคุณสำหรับวันนี้</p></div><div className="date-card"><small>วันนี้</small><b>28 Aug 2026</b></div></div>
        <div className="metrics"><div><span>ยอดขายวันนี้</span><strong>฿28,540.00</strong><em>↗ 12.5%</em></div><div><span>รายการขาย</span><strong>128</strong><em>↗ 8.2%</em></div><div><span>สินค้าออก</span><strong>1,250</strong><em>↗ 120</em></div><div><span>ลูกค้าใหม่</span><strong>18</strong><em>↗ 4</em></div></div>
        <div className="dashboard-panels"><section className="chart-card"><div className="panel-head"><div><b>Sales Overview</b><small>ยอดขาย 7 วันล่าสุด</small></div><button>สัปดาห์นี้ ▾</button></div><div className="chart"><svg viewBox="0 0 600 180" preserveAspectRatio="none"><polyline points="0,145 85,125 165,138 245,90 330,112 410,58 500,78 600,25" fill="none" /></svg><div className="chart-labels"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div></div></section><section className="recent-card"><div className="panel-head"><div><b>รายการล่าสุด</b><small>Recent transactions</small></div><button>ดูทั้งหมด</button></div>{['INV-000125','INV-000124','INV-000123','INV-000122'].map((id, i) => <div className="transaction" key={id}><span className="tx-icon">฿</span><div><b>{id}</b><small>{['10:30 AM','10:15 AM','10:05 AM','09:45 AM'][i]} • Cash</small></div><strong>฿{['1,250.00','650.00','820.00','1,350.00'][i]}</strong></div>)}</section></div>
      </section>
    </div>
    <section className="quick-strip"><span>▣ Responsive</span><span>⌁ Offline Ready</span><span>◇ Secure & Reliable</span><span>↻ Real-time Sync</span><span>▤ Audit Trail</span><span>◎ Multi-store</span></section>
  </main>;
}

function Sales({ onLogout }: { onLogout: () => void }) {
  const [query, setQuery] = useState('');
  const [cart, setCart] = useState<Product[]>([]);
  const filtered = products.filter(p => `${p.name} ${p.category}`.toLowerCase().includes(query.toLowerCase()));
  const total = cart.reduce((sum, p) => sum + Number(p.price), 0);
  return <main className="dashboard"><header className="topbar"><Logo /><div className="top-actions"><span className="online"><i /> Shift Open</span><span className="store">Store A ▾</span><button onClick={onLogout}>ออกจากระบบ</button></div></header><div className="dashboard-layout"><aside className="sidebar"><nav>{['⌂ Dashboard','▣ Sales','◈ Products','◫ Inventory','♙ Customers','⌁ Reports','◉ Cash & Shift','⚙ Settings'].map((label, i) => <button className={i === 1 ? 'nav-active' : ''} key={label}>{label}</button>)}</nav></aside><section className="dash-content sales-view"><div className="dash-head"><div><span className="eyebrow">SALES • POS COUNTER</span><h1>หน้าขาย</h1><p>เลือกสินค้าเพื่อเริ่มรายการ</p></div><div className="stat"><span>ยอดขายวันนี้</span><strong>฿28,540.00</strong></div></div><div className="pos-grid"><section className="catalog"><div className="search-row"><input aria-label="ค้นหาสินค้า" placeholder="ค้นหาสินค้า…" value={query} onChange={e => setQuery(e.target.value)} /><div className="chips"><button className="active">ทั้งหมด</button><button>เครื่องดื่ม</button><button>เบเกอรี่</button></div></div><div className="product-grid">{filtered.map(p => <button className="product" key={p.name} onClick={() => setCart(c => [...c, p])}><span className="product-icon">{p.name[0]}</span><strong>{p.name}</strong><small>{p.category} • เหลือ {p.stock}</small><b>฿{p.price}</b></button>)}</div></section><aside className="cart"><div className="cart-head"><h2>ตะกร้า ({cart.length})</h2><span>รายการขาย</span></div>{cart.length === 0 ? <div className="empty">ยังไม่มีสินค้า<br/><small>แตะสินค้าเพื่อเพิ่มลงรายการ</small></div> : <div className="cart-lines">{cart.map((p, i) => <div className="cart-line" key={`${p.name}-${i}`}><span>{p.name}</span><strong>฿{p.price}</strong></div>)}</div>}<div className="cart-total"><span>รวมทั้งหมด</span><strong>฿{total.toFixed(2)}</strong></div><button className="submit checkout" disabled={!cart.length}>ชำระเงิน</button></aside></div></section></div></main>;
}

function App() {
  const [loggedIn, setLoggedIn] = useState(Boolean(sessionStorage.getItem('prodx_access_token')));
  return loggedIn ? <Sales onLogout={() => { sessionStorage.removeItem('prodx_access_token'); setLoggedIn(false); }} /> : <Login onLogin={() => setLoggedIn(true)} />;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
