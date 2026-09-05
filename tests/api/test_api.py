import requests


def test_get_devices_empty(live_server):
    response = requests.get(f"{live_server}/devices")

    assert response.status_code == 200
    assert response.json() == []


def test_create_device_defaults_to_idle(live_server):
    payload = {"name": "API Device", "profile": "profile-api", "current_version": "1.0.0"}
    response = requests.post(f"{live_server}/devices", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "API Device"
    assert body["status"] == "idle"
    assert "id" in body


def test_created_device_appears_in_list(live_server):
    requests.post(
        f"{live_server}/devices",
        json={"name": "Listed Device", "profile": "profile-list"},
    )

    response = requests.get(f"{live_server}/devices")

    names = [device["name"] for device in response.json()]
    assert "Listed Device" in names


def test_upload_firmware_sets_uploaded_status(live_server):
    response = requests.post(
        f"{live_server}/firmware/upload", json={"version": "9.9.9"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "9.9.9"
    assert body["upload_status"] == "uploaded"


def test_uploaded_firmware_appears_in_list(live_server):
    requests.post(f"{live_server}/firmware/upload", json={"version": "8.8.8"})

    response = requests.get(f"{live_server}/firmware")

    versions = [build["version"] for build in response.json()]
    assert "8.8.8" in versions


def test_start_job_success_sets_device_updating(live_server):
    device = requests.post(
        f"{live_server}/devices",
        json={"name": "Job API Device", "profile": "profile-job-api"},
    ).json()
    build = requests.post(
        f"{live_server}/firmware/upload", json={"version": "1.1.1"}
    ).json()

    response = requests.post(
        f"{live_server}/ota/jobs",
        json={"device_id": device["id"], "build_id": build["id"]},
    )

    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "pending"

    device_check = requests.get(f"{live_server}/devices").json()
    updated_device = next(d for d in device_check if d["id"] == device["id"])
    assert updated_device["status"] == "updating"


def test_start_job_nonexistent_device_returns_404(live_server):
    build = requests.post(
        f"{live_server}/firmware/upload", json={"version": "2.2.2"}
    ).json()

    response = requests.post(
        f"{live_server}/ota/jobs",
        json={"device_id": 999999, "build_id": build["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"


def test_start_job_nonexistent_build_returns_404(live_server):
    device = requests.post(
        f"{live_server}/devices",
        json={"name": "No Build Device", "profile": "profile-nb"},
    ).json()

    response = requests.post(
        f"{live_server}/ota/jobs",
        json={"device_id": device["id"], "build_id": 999999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Firmware build not found"


def test_start_job_on_busy_device_returns_409(live_server):
    device = requests.post(
        f"{live_server}/devices",
        json={"name": "Busy API Device", "profile": "profile-busy-api"},
    ).json()
    build = requests.post(
        f"{live_server}/firmware/upload", json={"version": "3.3.3"}
    ).json()

    # first job succeeds and marks the device as updating
    requests.post(
        f"{live_server}/ota/jobs",
        json={"device_id": device["id"], "build_id": build["id"]},
    )

    # second job on the same device should be rejected
    response = requests.post(
        f"{live_server}/ota/jobs",
        json={"device_id": device["id"], "build_id": build["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Device is already mid-update"


def test_get_job_status_nonexistent_job_returns_404(live_server):
    response = requests.get(f"{live_server}/ota/jobs/999999/status")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"