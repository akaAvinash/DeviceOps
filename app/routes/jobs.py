from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.models import OtaJobCreate, OtaJobResponse

router = APIRouter()


@router.post("/ota/jobs", response_model=OtaJobResponse)
def start_job(job: OtaJobCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Verify device exists
    cursor.execute("SELECT * FROM devices WHERE id = ?", (job.device_id,))
    device = cursor.fetchone()
    if device is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found")

    # 2. Verify build exists
    cursor.execute("SELECT * FROM firmware_builds WHERE id = ?", (job.build_id,))
    build = cursor.fetchone()
    if build is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Firmware build not found")

    # 3. Reject if device already mid-update
    if device["status"] == "updating":
        conn.close()
        raise HTTPException(status_code=409, detail="Device is already mid-update")

    # 4. Insert job, update device status
    cursor.execute(
        "INSERT INTO ota_jobs (device_id, build_id, status) VALUES (?, ?, ?)",
        (job.device_id, job.build_id, "pending")
    )
    new_job_id = cursor.lastrowid

    cursor.execute(
        "UPDATE devices SET status = ? WHERE id = ?",
        ("updating", job.device_id)
    )

    conn.commit()
    conn.close()

    return OtaJobResponse(
        id=new_job_id,
        device_id=job.device_id,
        build_id=job.build_id,
        status="pending",
        started_at=None,
        completed_at=None
    )