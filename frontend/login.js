const shell = document.querySelector('.login-shell');
const form = document.querySelector('#login-form');
const status = document.querySelector('#form-status');
const pin = document.querySelector('#pin');
const toggle = document.querySelector('#toggle-pin');

if (toggle && pin) {
  toggle.addEventListener('click', () => {
    const visible = pin.type === 'text';
    pin.type = visible ? 'password' : 'text';
    toggle.setAttribute('aria-label', visible ? 'Show password' : 'Hide password');
  });
}

form?.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  status.textContent = 'Credentials captured — connect this action to the authentication API.';
});

// The production app can bind this to its persisted theme preference.
window.setLoginTheme = (theme) => {
  shell?.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
};
