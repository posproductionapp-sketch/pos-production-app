# Configuration Foundation

Configuration is environment-driven and must be validated at application startup.

## Required rules

- No credentials or API keys are committed.
- The PRODX POS application must not require or invoke an external AI-provider API key.
- GPT/ChatGPT connector authentication is external to the application and must never be copied into runtime configuration.
- Runtime configuration is separated from business/domain logic.
- Production secrets must come from the deployment secret manager/environment when the application genuinely requires them.
- `.env.example` may document variable names and safe placeholders only.

## Development-plane rule

The connected GPT/GitHub workflow is the approved AI development interface. It operates outside the PRODX POS runtime and must not introduce an application dependency on an AI-provider credential.

Core builds, tests, CI, and POS runtime execution must continue when no AI-provider credential is present.

The concrete runtime configuration library and application-specific variables are selected with the implementation stack; this foundation deliberately avoids coupling the architecture to a framework or vendor.
