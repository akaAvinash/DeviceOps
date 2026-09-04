from fastapi import APIRouter
from app.database import get_connection
from app.models import FirmwareBuildCreate, FirmwareBuildResponse

router = APIRouter()

@router.post("/firmware/upload", response_model=FirmwareBuildResponse)
def upload_firmware(build: FirmwareBuildCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO firmware_builds (version, upload_status) VALUES (?, ?)",
        (build.version, "uploaded")
    )
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return FirmwareBuildResponse(
        id=new_id,
        version=build.version,
        upload_status="uploaded"
    )

@router.get("/firmware", response_model=list[FirmwareBuildResponse])
def list_firmware():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM firmware_builds")
    rows = cursor.fetchall()
    conn.close()

    return [
        FirmwareBuildResponse(
            id=row["id"],
            version=row["version"],
            upload_status=row["upload_status"]
        )
        for row in rows
    ]