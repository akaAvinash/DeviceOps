# app/models.py

from pydantic import BaseModel
from typing import Literal, Optional


# ---------- Devices ----------

class DeviceCreate(BaseModel):
    name: str
    profile: str
    current_version: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    name: str
    profile: str
    status: Literal["idle", "updating", "failed"]
    current_version: Optional[str] = None


# ---------- Firmware Builds ----------

class FirmwareBuildCreate(BaseModel):
    version: str


class FirmwareBuildResponse(BaseModel):
    id: int
    version: str
    upload_status: Literal["uploaded", "failed"]


# ---------- OTA Jobs ----------

class OtaJobCreate(BaseModel):
    device_id: int
    build_id: int


class OtaJobResponse(BaseModel):
    id: int
    device_id: int
    build_id: int
    status: Literal["pending", "in_progress", "completed", "failed"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None