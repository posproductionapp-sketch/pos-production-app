"""HTTP API boundary; business decisions remain in application/domain layers."""

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.config.settings import load_settings
from src.domain.auth import Role
from src.infrastructure.database.auth import AuthService, AuthenticationError
from src.infrastructure.database.session import create_engine_from_env, session_factory
from src.infrastructure.database.sync import SqlAlchemySyncRepository

app = FastAPI(title="POS Production API", version="0.2.0")
_engine = None
_SessionLocal = None


def get_session():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = create_engine_from_env()
        _SessionLocal = session_factory(_engine)
    with _SessionLocal() as session:
        yield session


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


@app.post("/v1/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)) -> LoginResponse:
    try:
        token = AuthService(session, load_settings().auth_secret).login(tenant_id=request.tenant_id, username=request.username, password=request.password)
        return LoginResponse(access_token=token)
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc


@app.get("/v1/me")
def me(current=Depends(principal)) -> dict:
    return {"user_id": current.user_id, "tenant_id": current.tenant_id, "store_id": current.store_id, "roles": sorted(r.value for r in current.roles)}


@app.post("/v1/sync/commands")
def sync_command(request: SyncRequest, current=Depends(principal), session: Session = Depends(get_session)) -> dict:
    current.require(Role.CASHIER, Role.MANAGER, Role.ADMIN)
    repository = SqlAlchemySyncRepository(session, tenant_id=current.tenant_id, store_id=current.store_id)
    with session.begin():
        command = repository.record_received(command_id=request.command_id, operation=request.operation, payload=request.payload)
    return {"command_id": command.command_id, "state": command.state, "duplicate": command.result_json is not None}
