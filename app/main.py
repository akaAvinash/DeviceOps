from fastapi import FastAPI
from app.database import init_db
from app.routes import firmware, jobs, devices

app = FastAPI(title="DeviceOps")

init_db()

app.include_router(firmware.router)
app.include_router(firmware.router)
app.include_router(jobs.router)
app.include_router(devices.router)