const shell = document.querySelector('.login-shell');
const form = document.querySelector('#login-form');
const status = document.querySelector('#form-status');
const pin = document.querySelector('#pin');
const toggle = document.querySelector('#toggle-pin');
const employee = document.querySelector('#employee');
const signIn = document.querySelector('.sign-in');

const authConfig = window.POS_AUTH_CONFIG ?? {};
const tenantId = typeof authConfig.tenantId === 'string' ? authConfig.tenantId.trim() : '';
const authEndpoint = typeof authConfig.loginEndpoint === 'string' && authConfig.loginEndpoint.trim()
  ? authConfig.loginEndpoint.trim()
  : '/v1/auth/login';

if (toggle && pin) {
  toggle.addEventListener('click', () => {
    const visible = pin.type === 'text';
    pin.type = visible ? 'password' : 'text';
    toggle.setAttribute('aria-label', visible ? 'Show password' : 'Hide password');
  });
}

function setStatus(message) {
  if (status) status.textContent = message;
}

function setBusy(busy) {
  if (!signIn) return;
  signIn.disabled = busy;
  signIn.setAttribute('aria-busy', String(busy));
  signIn.textContent = busy ? 'SIGNING IN…' : 'SIGN IN';
}

async function authenticate(username, password) {
  if (!tenantId) {
    throw new Error('Store authentication is not configured.');
  }

  const response = await fetch(authEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ tenant_id: tenantId, username, password }),
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error('Invalid credentials.');
    if (response.status === 429) throw new Error('Too many attempts. Please try again later.');
    throw new Error('Unable to sign in right now.');
  }

  const payload = await response.json();
  if (!payload?.access_token || payload.token_type?.toLowerCase() !== 'bearer') {
    throw new Error('Authentication response was invalid.');
  }

  return payload;
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  setBusy(true);
  setStatus('Signing in…');

  try {
    const payload = await authenticate(employee.value.trim(), pin.value);
    // Keep the bearer token out of the URL and DOM. The production shell can
    // hand this value to its authenticated session/bootstrap layer.
    window.dispatchEvent(new CustomEvent('pos:authenticated', { detail: payload }));
    setStatus('Signed in successfully.');
  } catch (error) {
    setStatus(error instanceof Error ? error.message : 'Unable to sign in right now.');
  } finally {
    setBusy(false);
  }
});

// The production app can bind this to its persisted theme preference.
window.setLoginTheme = (theme) => {
  shell?.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
};
