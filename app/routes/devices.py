from fastapi import APIRouter
from app.database import get_connection
from app.models import DeviceCreate, DeviceResponse

router = APIRouter()

@router.post("/devices", response_model=DeviceResponse)
def create_device(device: DeviceCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO devices (name, profile, status, current_version) VALUES (?, ?, ?, ?)",
        (device.name, device.profile, "idle", device.current_version)
    )
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return DeviceResponse(
        id=new_id,
        name=device.name,
        profile=device.profile,
        status="idle",
        current_version=device.current_version
    )


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM devices")
    rows = cursor.fetchall()
    conn.close()

    return [
        DeviceResponse(
            id=row["id"],
            name=row["name"],
            profile=row["profile"],
            status=row["status"],
            current_version=row["current_version"]
        )
        for row in rows
    ]