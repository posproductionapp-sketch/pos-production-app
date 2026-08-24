# Configuration Foundation

Configuration is environment-driven and must be validated at application startup.

## Required rules

- No credentials or API keys are committed.
- OpenAI configuration is supplied through environment variables.
- Runtime configuration is separated from business/domain logic.
- Production secrets must come from the deployment secret manager/environment.
- `.env.example` may document variable names and safe placeholders only.

The concrete runtime configuration library and application-specific variables are selected with the implementation stack; this foundation deliberately avoids coupling the architecture to a framework or vendor.
