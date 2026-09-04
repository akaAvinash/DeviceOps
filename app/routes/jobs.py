import asyncio
from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.models import OtaJobCreate, OtaJobResponse
from app.jobs_engine import simulate_job_progress

router = APIRouter()

@router.post("/ota/jobs", response_model=OtaJobResponse)
async def start_job(job: OtaJobCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM devices WHERE id = ?", (job.device_id,))
    device = cursor.fetchone()
    if device is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found")

    cursor.execute("SELECT * FROM firmware_builds WHERE id = ?", (job.build_id,))
    build = cursor.fetchone()
    if build is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Firmware build not found")

    if device["status"] == "updating":
        conn.close()
        raise HTTPException(status_code=409, detail="Device is already mid-update")

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

    asyncio.create_task(simulate_job_progress(new_job_id, job.device_id))

    return OtaJobResponse(
        id=new_job_id,
        device_id=job.device_id,
        build_id=job.build_id,
        status="pending",
        started_at=None,
        completed_at=None
    )


@router.get("/ota/jobs/{job_id}/status", response_model=OtaJobResponse)
def get_job_status(job_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ota_jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return OtaJobResponse(
        id=row["id"],
        device_id=row["device_id"],
        build_id=row["build_id"],
        status=row["status"],
        started_at=row["started_at"],
        completed_at=row["completed_at"]
    )