"""HTTP API boundary; business decisions remain in application/domain layers."""

import time
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.body_limit import RequestBodyLimitMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.api.pos import build_pos_router
from src.api.reports import build_reports_router
from src.config.settings import load_settings
from src.domain.auth import Role
from src.infrastructure.database.auth import AuthService, AuthenticationError
from src.infrastructure.database.session import create_engine_from_env, session_factory
from src.infrastructure.database.sync import SqlAlchemySyncRepository, SyncCommandConflict
from src.observability import metrics

_settings = load_settings()
if _settings.environment == "production":
    _settings.validate_runtime()
_docs_enabled = _settings.environment != "production"

app = FastAPI(docs_url="/docs" if _docs_enabled else None, redoc_url="/redoc" if _docs_enabled else None)


class LoginRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=36)
    username: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=200)


class LoginResponse(BaseModel):
    access_token: str


class SyncRequest(BaseModel):
    command_id: str = Field(min_length=1, max_length=100)
    operation: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def principal(request: Request, session: Session = Depends(get_session)):
    from src.infrastructure.database.auth import Principal
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        return Principal.from_token(authorization.removeprefix("Bearer ").strip(), _settings.auth_secret, session)
    except (AuthenticationError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


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
    repository = SqlAlchemySyncRepository(session, tenant_id=current.tenant_id, store_id=current.store_id, actor_id=current.user_id)
    try:
        command = repository.record_received(command_id=request.command_id, operation=request.operation, payload=request.payload)
        session.commit()
    except SyncCommandConflict as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"command_id": command.command_id, "state": command.state, "duplicate": command.result_json is not None}


app.include_router(build_pos_router(principal, get_session))
app.include_router(build_reports_router(principal, get_session))
