import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? '';
const TOKEN_KEY = 'prodx_access_token';

type Product = { variant_id: string; sku: string; name: string; description: string; price: string; currency: string; stock: number };
type SaleResult = { order_id: string; payment_id: string; subtotal: string; discount: string; tax: string; total: string; currency: string };
type Shift = { shift_id: string; state: 'open' | 'closed'; opening_cash: string };

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = sessionStorage.getItem(TOKEN_KEY);
  const headers = new Headers(init.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${API}${path}`, { ...init, headers });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { const body = await response.json() as { detail?: string }; if (body.detail) detail = body.detail; } catch { /* keep status */ }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function Logo({ compact = false }: { compact?: boolean }) {
  return <div className={compact ? 'logo logo-compact' : 'logo'} aria-label="PRODX POS">
    <svg viewBox="0 0 52 52" role="img" aria-hidden="true"><path d="M8 38V14c0-5 3-8 8-8h12c9 0 15 5 15 13s-6 13-15 13H18v6H8Zm10-16h10c3 0 5-1 5-3s-2-3-5-3H18v6Z" /><path className="logo-cut" d="M8 38 20 25h10L18 38H8Z" /></svg>
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
      const data = await api<{ access_token: string }>('/v1/auth/login', { method: 'POST', body: JSON.stringify({ tenant_id: tenantId, username, password }) });
      sessionStorage.setItem(TOKEN_KEY, data.access_token); onLogin();
    } catch (err) { setError(err instanceof Error ? err.message : 'เข้าสู่ระบบไม่สำเร็จ'); }
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
        <label>Password<div className="password"><input required minLength={12} type={show ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" placeholder="รหัสผ่านอย่างน้อย 12 ตัวอักษร" /><button type="button" onClick={() => setShow(v => !v)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? 'ซ่อน' : 'แสดง'}</button></div></label>
        {error && <div className="error" role="alert">{error}</div>}
        <button className="submit" disabled={loading}>{loading ? 'กำลังเข้าสู่ระบบ…' : 'เข้าสู่ระบบ'}</button>
      </form>
      <div className="footer">DEVELOPED BY <strong>THODSAWAT</strong></div>
    </section>
  </main>;
}

function Sales({ onLogout }: { onLogout: () => void }) {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Record<string, number>>({});
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState<SaleResult | null>(null);
  const [shift, setShift] = useState<Shift | null>(null);

  async function loadCatalog() {
    setLoading(true); setError('');
    try {
      const [catalog, currentShift] = await Promise.all([
        api<{ items: Product[] }>('/v1/catalog/variants'),
        api<Shift | null>('/v1/shifts/current'),
      ]);
      setProducts(catalog.items.map(p => ({ ...p, stock: Number(p.stock) })));
      setShift(currentShift);
    } catch (err) { setError(err instanceof Error ? err.message : 'ไม่สามารถโหลดข้อมูลสินค้าได้'); }
    finally { setLoading(false); }
  }

  useEffect(() => { void loadCatalog(); }, []);

  const filtered = useMemo(() => products.filter(p => `${p.name} ${p.sku} ${p.description}`.toLowerCase().includes(query.toLowerCase())), [products, query]);
  const cartItems = products.filter(p => (cart[p.variant_id] ?? 0) > 0);
  const subtotal = cartItems.reduce((sum, p) => sum + Number(p.price) * (cart[p.variant_id] ?? 0), 0);
  const cartCount = Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);

  function addToCart(product: Product) {
    const quantity = cart[product.variant_id] ?? 0;
    if (quantity >= product.stock) return;
    setError(''); setCart(current => ({ ...current, [product.variant_id]: quantity + 1 }));
  }

  function removeFromCart(product: Product) {
    const quantity = cart[product.variant_id] ?? 0;
    setCart(current => ({ ...current, [product.variant_id]: Math.max(0, quantity - 1) }));
  }

  async function checkout() {
    if (!cartItems.length || checkoutLoading) return;
    setCheckoutLoading(true); setError(''); setSuccess(null);
    try {
      const items = cartItems.map(p => ({ variant_id: p.variant_id, quantity: cart[p.variant_id] }));
      const result = await api<SaleResult>('/v1/sales', {
        method: 'POST',
        headers: { 'Idempotency-Key': crypto.randomUUID() },
        body: JSON.stringify({ items, payment_method: paymentMethod, payment_reference: `POS-${crypto.randomUUID()}` }),
      });
      setSuccess(result); setCart({}); await loadCatalog();
    } catch (err) { setError(err instanceof Error ? err.message : 'ชำระเงินไม่สำเร็จ'); }
    finally { setCheckoutLoading(false); }
  }

  return <main className="dashboard"><header className="topbar"><Logo /><div className="top-actions"><span className={shift?.state === 'open' ? 'online' : 'error'}><i /> {shift?.state === 'open' ? 'Shift Open' : 'Shift Closed'}</span><span className="store" aria-label="Current store">Store</span><button onClick={onLogout}>ออกจากระบบ</button></div></header><div className="dashboard-layout"><aside className="sidebar"><nav aria-label="Primary navigation">{['⌂ Dashboard','▣ Sales','◈ Products','◫ Inventory','♙ Customers','⌁ Reports','◉ Cash & Shift','⚙ Settings'].map((label, i) => <span className={i === 1 ? 'nav-item nav-active' : 'nav-item nav-disabled'} aria-current={i === 1 ? 'page' : undefined} aria-disabled={i === 1 ? undefined : true} key={label}>{label}</span>)}</nav></aside><section className="dash-content sales-view"><div className="dash-head"><div><span className="eyebrow">SALES • POS COUNTER</span><h1>หน้าขาย</h1><p>เลือกสินค้าเพื่อเริ่มรายการ</p></div><div className="stat"><span>ยอดรายการนี้</span><strong>฿{subtotal.toFixed(2)}</strong></div></div>
    {loading && <div className="loading" role="status">กำลังโหลดสินค้า…</div>}
    {error && <div className="error" role="alert">{error}</div>}
    {success && <div className="success" role="status">ชำระเงินสำเร็จ · Order {success.order_id} · ฿{success.total}</div>}
    <div className="pos-grid"><section className="catalog"><div className="search-row"><input aria-label="ค้นหาสินค้า" placeholder="ค้นหาสินค้า…" value={query} onChange={e => setQuery(e.target.value)} /></div><div className="product-grid">{filtered.map(p => { const quantity = cart[p.variant_id] ?? 0; const remaining = p.stock - quantity; return <button className="product" key={p.variant_id} onClick={() => addToCart(p)} disabled={remaining <= 0} aria-label={`${p.name}, ราคา ${p.price} บาท, คงเหลือ ${remaining}`}><span className="product-icon">{p.name[0]}</span><strong>{p.name}</strong><small>{p.description || p.sku} • เหลือ {remaining}</small><b>฿{p.price}</b></button>; })}</div></section><aside className="cart"><div className="cart-head"><h2>ตะกร้า ({cartCount})</h2><span>รายการขาย</span></div>{!cartItems.length ? <div className="empty">ยังไม่มีสินค้า<br/><small>แตะสินค้าเพื่อเพิ่มลงรายการ</small></div> : <div className="cart-lines">{cartItems.map(p => <div className="cart-line" key={p.variant_id}><div><span>{p.name}</span><small>× {cart[p.variant_id]}</small></div><div><strong>฿{(Number(p.price) * cart[p.variant_id]).toFixed(2)}</strong><button type="button" onClick={() => removeFromCart(p)} aria-label={`ลด ${p.name}`}>−</button></div></div>)}</div>}<div className="payment-methods" aria-label="Payment method">{['cash','promptpay','card'].map(method => <button type="button" key={method} className={paymentMethod === method ? 'active' : ''} onClick={() => setPaymentMethod(method)}>{method === 'cash' ? 'เงินสด' : method === 'promptpay' ? 'PromptPay' : 'Card'}</button>)}</div><div className="cart-total"><span>รวมทั้งหมด</span><strong>฿{subtotal.toFixed(2)}</strong></div><button className="submit checkout" onClick={checkout} disabled={!cartItems.length || checkoutLoading}>{checkoutLoading ? 'กำลังดำเนินการ…' : `ชำระเงิน · ฿${subtotal.toFixed(2)}`}</button></aside></div></section></div></main>;
}

function App() { const [loggedIn, setLoggedIn] = useState(Boolean(sessionStorage.getItem(TOKEN_KEY))); return loggedIn ? <Sales onLogout={() => { sessionStorage.removeItem(TOKEN_KEY); setLoggedIn(false); }} /> : <Login onLogin={() => setLoggedIn(true)} />; }
createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
