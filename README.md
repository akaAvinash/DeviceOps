# DeviceOps

A simulated OTA (over-the-air) firmware update system for a device fleet.

This project is modeled on real device-fleet testing work — the idea is to rebuild, in a simplified form, the kind of system that manages firmware updates across a bunch of connected devices: upload firmware, start an update job on a device, watch that job move through its stages, and handle the errors that come with it.

There's no real hardware here. Devices are just rows in a database, and the "update" is simulated by a background task that changes a job's status over time. That's intentional — the point of this project isn't to talk to real firmware, it's to build (and later test) a realistic backend around the same problem shape: uploads, jobs, polling, timeouts, and state.

## Status: Phase 1 (Backend) — complete

This is being built in phases. Right now, only the backend exists — no UI yet, no automated tests yet. Those come later. See `ARCHITECTURE.md` for the full plan and reasoning behind each piece.

## What's built so far

- A FastAPI backend with SQLite storage (no ORM — raw SQL, written by hand)
- Three tables: `devices`, `firmware_builds`, `ota_jobs`, connected with foreign keys
- Endpoints to register a device, list devices, upload a firmware build, start an update job, and check a job's status
- A background task that simulates a job moving through `pending → in_progress → completed` over time, so there's something real to poll against
- Error handling for the cases that actually matter: starting a job on a device that doesn't exist, starting a job on a device that's already mid-update, and checking the status of a job that was never created

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `POST` | `/devices` | Register a new device in the fleet |
| `GET` | `/devices` | List all devices |
| `POST` | `/firmware/upload` | Upload a new firmware build |
| `POST` | `/ota/jobs` | Start an update job for a device |
| `GET` | `/ota/jobs/{id}/status` | Check how a job is progressing |

## Tech stack (so far)

- Python
- FastAPI
- SQLite (raw SQL, no ORM)
- `asyncio` for the background job simulation

## Running it locally

```bash
# from the project root, with your virtual environment active
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` — FastAPI generates an interactive page there where you can try every endpoint directly in the browser.

## What's next

This is a full-stack project, not just a backend exercise. The plan from here:

1. A simple frontend UI
2. Playwright tests against that UI
3. API tests with pytest
4. Load testing with k6
5. Visual/OCR validation
6. CI/CD with GitHub Actions
7. An AI agent that looks at failed jobs and helps figure out why they failed

Each of those is a separate phase, and none of them are built yet. This README will get updated as they land.
