# DeviceOps

A simulated OTA (over-the-air) firmware update system for a device fleet.

This project is modeled on real device-fleet testing work — the idea is to rebuild, in a simplified form, the kind of system that manages firmware updates across a bunch of connected devices: upload firmware, start an update job on a device, watch that job move through its stages, and handle the errors that come with it.

There's no real hardware here. Devices are just rows in a database, and the "update" is simulated by a background task that changes a job's status over time. That's intentional — the point of this project isn't to talk to real firmware, it's to build (and later test) a realistic backend and UI around the same problem shape: uploads, jobs, polling, timeouts, and state.

## Status: Phase 1 (Backend) and Phase 2 (UI) — complete

This is being built in phases. The backend and a working frontend both exist and are connected end to end. No automated tests yet — that's next. See `ARCHITECTURE.md` for the full plan and the reasoning behind each piece.

## What's built so far

**Backend**
- A FastAPI backend with SQLite storage (no ORM — raw SQL, written by hand)
- Three tables: `devices`, `firmware_builds`, `ota_jobs`, connected with foreign keys
- Endpoints to register a device, list devices, upload a firmware build, list firmware builds, start an update job, and check a job's status
- A background task that simulates a job moving through `pending → in_progress → completed` over time, so there's something real to poll against
- Error handling for the cases that actually matter: starting a job on a device that doesn't exist, starting a job on a device that's already mid-update, and checking the status of a job that was never created

**Frontend**
- A plain HTML/CSS/JS single page, served directly by FastAPI (no separate frontend server, no build step)
- A fleet table showing every device and its live status
- A form to register new devices
- A form to upload firmware, with a list of available builds shown underneath
- A form to start an update job by picking a device and a build from dropdowns
- A live status panel that polls the job's status every couple of seconds and updates on its own — no page refresh — until the job finishes
- Errors from the backend (like trying to update a device that's already busy) are shown directly in the UI, not just logged to the console

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `POST` | `/devices` | Register a new device in the fleet |
| `GET` | `/devices` | List all devices |
| `POST` | `/firmware/upload` | Upload a new firmware build |
| `GET` | `/firmware` | List all firmware builds |
| `POST` | `/ota/jobs` | Start an update job for a device |
| `GET` | `/ota/jobs/{id}/status` | Check how a job is progressing |

## Tech stack (so far)

- Python, FastAPI
- SQLite (raw SQL, no ORM)
- `asyncio` for the background job simulation
- Plain HTML, CSS, and JavaScript for the frontend (no framework)

## Running it locally

```bash
# from the project root, with your virtual environment active
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/` for the UI, or `http://127.0.0.1:8000/docs` for the raw API (FastAPI's interactive Swagger page).

## What's next

This is a full-stack project, not just a backend exercise. The plan from here:

1. Playwright tests against the UI
2. API tests with pytest
3. Load testing with k6
4. Visual/OCR validation
5. CI/CD with GitHub Actions
6. An AI agent that looks at failed jobs and helps figure out why they failed

Each of those is a separate phase, and none of them are built yet. This README will get updated as they land.
