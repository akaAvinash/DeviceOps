// frontend/app.js

const API_BASE = ""; // same origin, since FastAPI is serving this page too

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

loadDevices(); // initial load when the page opens