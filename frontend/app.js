const API_BASE = ""; // same origin, since FastAPI is serving this page too

// ---------- Devices ----------

async function loadDevices() {
    const response = await fetch(`${API_BASE}/devices`);
    const devices = await response.json();

    const tbody = document.getElementById("device-table-body");
    tbody.innerHTML = ""; // clear existing rows before re-rendering

    devices.forEach((device) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.name}</td>
            <td>${device.profile}</td>
            <td class="status-${device.status}">${device.status}</td>
            <td>${device.current_version ?? "—"}</td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById("fleet-count").textContent =
        `${devices.length} device${devices.length === 1 ? "" : "s"}`;

    populateDeviceDropdown(devices);
}

async function registerDevice(event) {
    event.preventDefault(); // stop the form from doing a full page reload

    const name = document.getElementById("device-name").value;
    const profile = document.getElementById("device-profile").value;
    const version = document.getElementById("device-version").value;

    const payload = {
        name: name,
        profile: profile,
        current_version: version || null
    };

    const response = await fetch(`${API_BASE}/devices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        alert("Failed to register device");
        return;
    }

    document.getElementById("device-form").reset();
    await loadDevices(); // refresh the table to show the new device
}

document.getElementById("device-form").addEventListener("submit", registerDevice);

// ---------- Firmware ----------

async function loadFirmwareBuilds() {
    const response = await fetch(`${API_BASE}/firmware`);
    const builds = await response.json();

    const list = document.getElementById("firmware-list");
    list.innerHTML = "";

    builds.forEach((build) => {
        const item = document.createElement("li");
        item.textContent = `v${build.version}`;
        item.dataset.buildId = build.id;
        list.appendChild(item);
    });

    populateBuildDropdown(builds);
}

async function uploadFirmware(event) {
    event.preventDefault(); // stop the form from doing a full page reload

    const version = document.getElementById("firmware-version").value;

    const response = await fetch(`${API_BASE}/firmware/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: version })
    });

    if (!response.ok) {
        alert("Failed to upload firmware");
        return;
    }

    document.getElementById("firmware-form").reset();
    await loadFirmwareBuilds(); // refresh list instead of alert
}

document.getElementById("firmware-form").addEventListener("submit", uploadFirmware);

// ---------- Job dropdowns ----------

function populateDeviceDropdown(devices) {
    const select = document.getElementById("job-device");
    const previousValue = select.value;
    select.innerHTML = "";
    devices.forEach((device) => {
        const option = document.createElement("option");
        option.value = device.id;
        option.textContent = `${device.name} (${device.status})`;
        select.appendChild(option);
    });
    if (previousValue) select.value = previousValue;
}

function populateBuildDropdown(builds) {
    const select = document.getElementById("job-build");
    const previousValue = select.value;
    select.innerHTML = "";
    builds.forEach((build) => {
        const option = document.createElement("option");
        option.value = build.id;
        option.textContent = `v${build.version}`;
        select.appendChild(option);
    });
    if (previousValue) select.value = previousValue;
}

// ---------- Job trigger + polling ----------

async function startJob(event) {
    event.preventDefault();

    const deviceId = document.getElementById("job-device").value;
    const buildId = document.getElementById("job-build").value;
    const statusBox = document.getElementById("job-status");

    const response = await fetch(`${API_BASE}/ota/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_id: Number(deviceId), build_id: Number(buildId) })
    });

    if (!response.ok) {
        const error = await response.json();
        statusBox.textContent = `Error: ${error.detail}`;
        statusBox.className = "job-status status-failed";
        return;
    }

    const job = await response.json();
    statusBox.className = "job-status";
    pollJobStatus(job.id, statusBox);

    // refresh fleet + dropdown so the device shows "updating" right away
    await loadDevices();
}

async function pollJobStatus(jobId, statusBox) {
    const response = await fetch(`${API_BASE}/ota/jobs/${jobId}/status`);
    const job = await response.json();

    statusBox.textContent = `Job #${job.id}: ${job.status}`;
    statusBox.className = `job-status status-${job.status}`;

    if (job.status === "completed" || job.status === "failed") {
        await loadDevices(); // device is idle again — refresh the fleet table
        return;
    }

    setTimeout(() => pollJobStatus(jobId, statusBox), 2000); // poll again in 2s
}

document.getElementById("job-form").addEventListener("submit", startJob);

// ---------- Initial load ----------

loadDevices();
loadFirmwareBuilds();