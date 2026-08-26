"""Read-only store reporting API."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.domain.auth import Role
from src.infrastructure.database.reports import ReportRepository


def build_reports_router(principal_dependency, session_dependency) -> APIRouter:
    router = APIRouter(prefix="/v1/reports", tags=["reports"])

    def require_manager(current) -> None:
        try:
            current.require(Role.ADMIN, Role.MANAGER)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail="Insufficient role") from exc

    def parse_boundary(value: str, field: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid {field} timestamp") from exc
        if parsed.tzinfo is None:
            raise HTTPException(status_code=400, detail=f"{field} timestamp must include timezone")
        return parsed.astimezone(timezone.utc)

    def boundaries(start: str, end: str) -> tuple[datetime, datetime]:
        start_dt = parse_boundary(start, "start")
        end_dt = parse_boundary(end, "end")
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="end must be after start")
        return start_dt, end_dt

    @router.get("/sales")
    def sales_report(
        start: str = Query(min_length=1),
        end: str = Query(min_length=1),
        current=Depends(principal_dependency),
        session: Session = Depends(session_dependency),
    ):
        require_manager(current)
        start_dt, end_dt = boundaries(start, end)
        return ReportRepository(session, store_id=current.store_id).sales(start=start_dt, end=end_dt)

    @router.get("/inventory")
    def inventory_report(
        start: str = Query(min_length=1),
        end: str = Query(min_length=1),
        current=Depends(principal_dependency),
        session: Session = Depends(session_dependency),
    ):
        require_manager(current)
        start_dt, end_dt = boundaries(start, end)
        return ReportRepository(session, store_id=current.store_id).inventory(start=start_dt, end=end_dt)

    @router.get("/shifts")
    def shift_report(
        start: str = Query(min_length=1),
        end: str = Query(min_length=1),
        current=Depends(principal_dependency),
        session: Session = Depends(session_dependency),
    ):
        require_manager(current)
        start_dt, end_dt = boundaries(start, end)
        return {"start": start_dt.isoformat(), "end": end_dt.isoformat(), "shifts": ReportRepository(session, store_id=current.store_id).shifts(start=start_dt, end=end_dt)}

    return router
