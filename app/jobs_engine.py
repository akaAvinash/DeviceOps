import asyncio
from datetime import datetime, timezone
from app.database import get_connection


async def simulate_job_progress(job_id: int, device_id: int):
    # Stage 1: pending -> in_progress
    await asyncio.sleep(5)
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "UPDATE ota_jobs SET status = ?, started_at = ? WHERE id = ?",
        ("in_progress", now, job_id)
    )
    conn.commit()
    conn.close()

    # Stage 2: in_progress -> completed
    await asyncio.sleep(5)
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "UPDATE ota_jobs SET status = ?, completed_at = ? WHERE id = ?",
        ("completed", now, job_id)
    )
    cursor.execute(
        "UPDATE devices SET status = ? WHERE id = ?",
        ("idle", device_id)
    )
    conn.commit()
    conn.close()