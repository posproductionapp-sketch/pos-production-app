"""HTTP API boundary; business decisions remain in application/domain layers."""

import time
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.settings import load_settings
from src.domain.auth import Role
from src.infrastructure.database.auth import AuthService, AuthenticationError
from src.infrastructure.database.session import create_engine_from_env, session_factory
from src.infrastructure.database.sync import SqlAlchemySyncRepository
from src.api.pos import build_pos_router
from src.observability import metrics

_settings = load_settings()
_docs_enabled = _settings.environment != "production"
app = FastAPI(
    title="POS Production API",
    version="0.3.0",
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
_engine = None
_SessionLocal = None


@app.middleware("http")
async def production_headers(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    started = time.perf_counter()
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - started) * 1000
        metrics.observe(method=request.method, path=request.url.path, status=500, duration_ms=duration_ms)
        raise
    duration_ms = (time.perf_counter() - started) * 1000
    metrics.observe(method=request.method, path=request.url.path, status=response.status_code, duration_ms=duration_ms)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/v1/") else "no-cache"
    if request.url.scheme == "https" or _settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


def get_session():
    global _engine, _SessionLocal
    _settings.validate_runtime()
    if _SessionLocal is None:
        _engine = create_engine_from_env()
        _SessionLocal = session_factory(_engine)
    with _SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            if session.in_transaction():
                session.rollback()


class LoginRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=36)
    username: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=200)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SyncRequest(BaseModel):
    command_id: str = Field(min_length=1, max_length=100)
    operation: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


def principal(authorization: str = Header(default=""), session: Session = Depends(get_session)):
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        return AuthService(session, load_settings().auth_secret).authenticate(authorization[7:].strip())
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication") from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(session: Session = Depends(get_session)) -> dict[str, str]:
    session.execute(text("select 1"))
    return {"status": "ready"}


@app.get("/metrics")
def metrics_endpoint() -> dict[str, object]:
    return metrics.snapshot()


@app.post("/v1/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)) -> LoginResponse:
    try:
        token = AuthService(session, load_settings().auth_secret).login(tenant_id=request.tenant_id, username=request.username, password=request.password)
        session.commit()
        return LoginResponse(access_token=token)
    except (AuthenticationError, ValueError) as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc


@app.get("/v1/me")
def me(current=Depends(principal)) -> dict:
    return {"user_id": current.user_id, "tenant_id": current.tenant_id, "store_id": current.store_id, "roles": sorted(r.value for r in current.roles)}


@app.post("/v1/sync/commands")
def sync_command(request: SyncRequest, current=Depends(principal), session: Session = Depends(get_session)) -> dict:
    current.require(Role.CASHIER, Role.MANAGER, Role.ADMIN)
    repository = SqlAlchemySyncRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
    command = repository.record_received(command_id=request.command_id, operation=request.operation, payload=request.payload)
    session.commit()
    return {"command_id": command.command_id, "state": command.state, "duplicate": command.result_json is not None}


app.include_router(build_pos_router(principal, get_session))
