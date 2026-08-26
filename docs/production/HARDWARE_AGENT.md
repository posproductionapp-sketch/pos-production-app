# Hardware Agent

The POS hardware boundary is a local Electron process. The backend/application layers never import printer, cash-drawer, USB, serial, or vendor SDKs.

## Runtime boundary

- Bind only to `127.0.0.1`.
- Require `HARDWARE_AGENT_TOKEN` with at least 32 characters.
- Expose only `/health`, `/v1/print`, and `/v1/cash-drawer/open`.
- Treat `command_id` as the idempotency key for a hardware action.
- Reject oversized receipt payloads.
- Fail closed when a real hardware driver is not configured.
- Keep vendor-specific drivers inside the hardware agent process.

## Driver contract

A production deployment injects a printer driver and cash-drawer driver into `HardwareAgent`. The repository intentionally does not ship a vendor-specific implementation because the target printer/drawer model has not been selected. The unconfigured drivers fail closed instead of pretending a device action succeeded.

## Security

The agent is a local privileged boundary. It must not listen on `0.0.0.0`, expose permissive CORS, accept unauthenticated commands, or persist production credentials in source control.

## Verification

Run:

```bash
cd hardware-agent
npm install
npm test
npm start
```

The Node test suite verifies command idempotency, input validation, and fail-closed behavior. Device-specific integration tests belong in the adapter package for the selected hardware.
