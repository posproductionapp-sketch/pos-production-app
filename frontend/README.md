# POS Production Web Client

React + TypeScript + Vite client for the POS Production API.

## Current scope

- Modern responsive POS login screen.
- API integration with `POST /v1/auth/login`.
- No bearer-token persistence in `localStorage`.
- API base URL configured with `VITE_API_BASE_URL`.

## Development

```bash
npm install
npm run dev
```

The authentication/session persistence strategy will be implemented together with the offline/session architecture so that browser storage does not become an accidental security boundary.
