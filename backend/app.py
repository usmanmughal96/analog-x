from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import DateTime, Float, Index, JSON, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "agents" / "candidate_catalog.json"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analogx_records.db")
WRITE_API_KEY = os.getenv("WRITE_API_KEY", "")
ALLOWED_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class FieldRecord(Base):
    __tablename__ = "field_records"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(100), index=True)
    station_id: Mapped[str] = mapped_column(String(160), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


Index("ix_field_records_site_observed", FieldRecord.site_id, FieldRecord.observed_at)


class RecordIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1, max_length=80)
    site_id: str = Field(min_length=1, max_length=100)
    station_id: str = Field(min_length=1, max_length=160)
    observed_at: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    observation_type: str = Field(default="Other field note", max_length=100)
    value: float | None = None
    value_text: str = Field(default="", max_length=5000)
    unit: str = Field(default="", max_length=60)
    method: str = Field(default="", max_length=4000)
    notes: str = Field(default="", max_length=12000)
    sync_status: str = Field(default="synced", max_length=40)

    @field_validator("observed_at")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class BulkIn(BaseModel):
    records: list[dict[str, Any]] = Field(min_length=1, max_length=500)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_write_access(authorization: str | None = Header(default=None)):
    if not WRITE_API_KEY:
        return True
    expected = f"Bearer {WRITE_API_KEY}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid backend bearer token required")
    return True


def normalise_payload(record: RecordIn) -> dict[str, Any]:
    payload = record.model_dump(mode="json")
    payload.pop("photo", None)
    payload.pop("photo_data_url", None)
    payload["sync_status"] = "synced"
    return payload


app = FastAPI(
    title="ANALOG-X Field Evidence API",
    version="1.0.0",
    description="Self-hosted storage for user-recorded field observations. It does not fetch or invent NASA measurements.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOWED_ORIGINS != ["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"ok": True, "database": "connected", "storage": "PostgreSQL" if engine.dialect.name == "postgresql" else "SQLite"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {type(exc).__name__}") from exc


@app.get("/api/v1/catalog")
def catalog():
    if not CATALOG_PATH.exists():
        raise HTTPException(status_code=503, detail="Bundled candidate catalog not found on this server")
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


@app.get("/api/v1/field-records")
def list_records(
    site_id: str | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(FieldRecord).order_by(FieldRecord.observed_at.desc()).limit(limit).offset(offset)
    if site_id:
        query = query.where(FieldRecord.site_id == site_id)
    rows = db.scalars(query).all()
    return {"count": len(rows), "limit": limit, "offset": offset, "records": [row.payload for row in rows]}


@app.post("/api/v1/field-records", dependencies=[Depends(require_write_access)])
def create_record(record_data: dict[str, Any], db: Session = Depends(get_db)):
    try:
        record = RecordIn.model_validate(record_data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    row = FieldRecord(
        id=record.id,
        site_id=record.site_id,
        station_id=record.station_id,
        observed_at=record.observed_at,
        latitude=record.latitude,
        longitude=record.longitude,
        payload=normalise_payload(record),
    )
    db.merge(row)
    db.commit()
    return {"ok": True, "record_id": record.id, "sync_status": "synced"}


@app.post("/api/v1/field-records/bulk", dependencies=[Depends(require_write_access)])
def bulk_records(body: BulkIn, db: Session = Depends(get_db)):
    accepted = 0
    rejected: list[dict[str, Any]] = []
    for index, raw in enumerate(body.records):
        try:
            record = RecordIn.model_validate(raw)
            row = FieldRecord(
                id=record.id,
                site_id=record.site_id,
                station_id=record.station_id,
                observed_at=record.observed_at,
                latitude=record.latitude,
                longitude=record.longitude,
                payload=normalise_payload(record),
            )
            db.merge(row)
            accepted += 1
        except ValidationError as exc:
            rejected.append({"index": index, "errors": exc.errors()})
    db.commit()
    return {"ok": True, "accepted": accepted, "rejected": rejected}


@app.delete("/api/v1/field-records/{record_id}", dependencies=[Depends(require_write_access)])
def delete_record(record_id: str, db: Session = Depends(get_db)):
    row = db.get(FieldRecord, record_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Field record not found")
    db.delete(row)
    db.commit()
    return {"ok": True, "deleted": record_id}
