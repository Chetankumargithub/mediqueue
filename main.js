/**
 * main.js — MediQueue frontend
 * Fetches data from Flask API and renders charts, table, re-triage UI.
 */

"use strict";

// ── STATE ──────────────────────────────────────────────────────
let allPatients   = [];
let currentFilter = "All";
let barChart      = null;
let histChart     = null;

// ── INIT ───────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadPatients();
  loadTestCases();
});

// ── API CALLS ──────────────────────────────────────────────────

async function loadPatients() {
  try {
    const res  = await fetch("/api/patients");
    const data = await res.json();
    allPatients = data.patients;
    renderMetrics(data);
    renderCharts(data.patients);
    renderTable();
    populatePatientSelect();
  } catch (err) {
    console.error("Failed to load patients:", err);
    document.getElementById("tableBody").innerHTML =
      `<tr><td colspan="10" class="loading-row" style="color:#e24b4a">Error loading data. Is the Flask server running?</td></tr>`;
  }
}

async function resetPipeline() {
  try {
    const res  = await fetch("/api/reset", { method: "POST" });
    const data = await res.json();
    showFeedback("rtFeedback", `Pipeline reset — ${data.total} patients reloaded.`, "info");
    await loadPatients();
    await loadTestCases();
  } catch (err) {
    showFeedback("rtFeedback", "Reset failed.", "error");
  }
}

async function submitRetriage() {
  const pid  = document.getElementById("rtPatientId").value;
  const o2   = document.getElementById("rtO2").value;
  const hr   = document.getElementById("rtHr").value;
  const pain = document.getElementById("rtPain").value;

  if (!pid) { showFeedback("rtFeedback", "Please select a patient.", "error"); return; }
  if (!o2 && !hr && !pain) {
    showFeedback("rtFeedback", "Enter at least one vital to update.", "error"); return;
  }

  const body = { patient_id: pid };
  if (o2)   body.oxygen_sat   = parseInt(o2);
  if (hr)   body.heart_rate   = parseInt(hr);
  if (pain) body.pain_level   = parseInt(pain);

  try {
    const res  = await fetch("/api/retriage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) { showFeedback("rtFeedback", data.error || "Update failed.", "error"); return; }

    const arrow = data.old_level !== data.new_level
      ? ` | Level: ${data.old_level} → <strong>${data.new_level}</strong>` : "";
    showFeedback(
      "rtFeedback",
      `${pid} updated — Score: ${data.old_score} → ${data.new_score}${arrow} | New rank: #${data.new_rank}`,
      "success"
    );

    await loadPatients();

    // Clear inputs
    ["rtO2","rtHr","rtPain"].forEach(id => document.getElementById(id).value = "");
  } catch (err) {
    showFeedback("rtFeedback", "Request failed.", "error");
  }
}

async function applyWaitBoost() {
  try {
    const res  = await fetch("/api/waitboost", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ current_time: "16:00" }),
    });
    const data = await res.json();
    showFeedback("rtFeedback", `Wait-boost applied to ${data.boosted} stable patients (+15 score each).`, "info");
    await loadPatients();
  } catch (err) {
    showFeedback("rtFeedback", "Wait boost failed.", "error");
  }
}

async function loadTestCases() {
  try {
    const res  = await fetch("/api/testcases");
    const data = await res.json();
    renderTestCases(data);
  } catch (err) {
    document.getElementById("tcGrid").innerHTML =
      `<div class="loading-row" style="color:#e24b4a">Failed to load test cases.</div>`;
  }
}

// ── RENDER FUNCTIONS ───────────────────────────────────────────

function renderMetrics(data) {
  const { summary, total, wait_boosted } = data;
  document.getElementById("mTotal").textContent    = total;
  document.getElementById("mCritical").textContent = summary.Critical;
  document.getElementById("mModerate").textContent = summary.Moderate;
  document.getElementById("mStable").textContent   = summary.Stable;
  document.getElementById("mStableSub").textContent =
    `Score < 30 · ${wait_boosted} wait-boosted`;
}

function renderCharts(patients) {
  const crit  = patients.filter(p => p.priority_level === "Critical").length;
  const mod   = patients.filter(p => p.priority_level === "Moderate").length;
  const stab  = patients.filter(p => p.priority_level === "Stable").length;

  // ── Bar chart ──────────────────────────────────────────────
  const barCtx = document.getElementById("barChart").getContext("2d");
  if (barChart) barChart.destroy();
  barChart = new Chart(barCtx, {
    type: "bar",
    data: {
      labels: ["Critical", "Moderate", "Stable"],
      datasets: [{
        data: [crit, mod, stab],
        backgroundColor: ["#E24B4A", "#EF9F27", "#639922"],
        borderRadius: 7,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} patients` } },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 12 } },
        },
        y: {
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8", font: { size: 11 } },
          beginAtZero: true,
        },
      },
    },
  });

  document.getElementById("barLegend").innerHTML = [
    { c: "#E24B4A", l: `Critical — ${crit}` },
    { c: "#EF9F27", l: `Moderate — ${mod}` },
    { c: "#639922", l: `Stable — ${stab}` },
  ].map(x => `
    <span class="leg-item">
      <span class="leg-dot" style="background:${x.c}"></span>${x.l}
    </span>`).join("");

  // ── Histogram chart ────────────────────────────────────────
  const bins = new Array(10).fill(0);
  patients.forEach(p => {
    const b = Math.min(9, Math.floor(p.acuity_score / 10));
    bins[b]++;
  });
  const binLabels = ["0-9","10-19","20-29","30-39","40-49","50-59","60-69","70-79","80-89","90-100"];
  const binColors = bins.map((_, i) => i >= 6 ? "#E24B4A" : i >= 3 ? "#EF9F27" : "#639922");

  const histCtx = document.getElementById("histChart").getContext("2d");
  if (histChart) histChart.destroy();
  histChart = new Chart(histCtx, {
    type: "bar",
    data: {
      labels: binLabels,
      datasets: [{
        data: bins,
        backgroundColor: binColors,
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} patients` } },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: "#94a3b8",
            font: { size: 10 },
            autoSkip: false,
            maxRotation: 40,
          },
          title: {
            display: true,
            text: "Acuity score range",
            color: "#64748b",
            font: { size: 11 },
          },
        },
        y: {
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8", font: { size: 11 } },
          beginAtZero: true,
        },
      },
    },
  });
}

function renderTable() {
  const search  = (document.getElementById("searchInput").value || "").toLowerCase();
  const filtered = allPatients.filter(p => {
    const matchFilter = currentFilter === "All" || p.priority_level === currentFilter;
    const matchSearch = !search
      || p.patient_id.toLowerCase().includes(search)
      || p.priority_level.toLowerCase().includes(search);
    return matchFilter && matchSearch;
  });

  const tbody = document.getElementById("tableBody");

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" class="loading-row">No patients match your filter.</td></tr>`;
    document.getElementById("tableFooter").textContent = "";
    return;
  }

  tbody.innerHTML = filtered.map(p => `
    <tr>
      <td class="rank-cell">${p.triage_rank}</td>
      <td class="id-cell">${p.patient_id}</td>
      <td>${p.age}</td>
      <td>${p.heart_rate} bpm</td>
      <td>${p.oxygen_sat}%</td>
      <td>${p.pain_level}/10</td>
      <td>${p.arrival_time}</td>
      <td class="score-cell" style="color:${scoreColor(p.acuity_score)}">${p.acuity_score}</td>
      <td><span class="badge badge-${p.priority_level}">${p.priority_level}</span></td>
      <td>${p.wait_boost ? '<span class="boost-yes">+15 ✓</span>' : '<span style="color:#4a5568">—</span>'}</td>
    </tr>`).join("");

  document.getElementById("tableFooter").textContent =
    `Showing ${filtered.length} of ${allPatients.length} patients`;
}

function renderTestCases(tcs) {
  document.getElementById("tcGrid").innerHTML = tcs.map(tc => `
    <div class="tc-item ${tc.passed ? "" : "fail"}">
      <div class="tc-id">${tc.id}</div>
      <div class="tc-title">${tc.title}</div>
      <div class="tc-desc">${tc.description}</div>
      <div class="tc-result ${tc.passed ? "tc-pass" : "tc-fail"}">
        ${tc.passed ? "✓ PASS" : "✗ FAIL"} — ${tc.result}
      </div>
    </div>`).join("");
}

// ── HELPERS ────────────────────────────────────────────────────

function scoreColor(score) {
  if (score >= 60) return "#e24b4a";
  if (score >= 30) return "#ef9f27";
  return "#639922";
}

function showFeedback(elementId, message, type) {
  const el = document.getElementById(elementId);
  el.innerHTML = `<div class="feedback-box feedback-${type}">${message}</div>`;
  setTimeout(() => { el.innerHTML = ""; }, 5000);
}

function setFilter(filter, btn) {
  currentFilter = filter;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderTable();
}

function filterTable() {
  renderTable();
}

function populatePatientSelect() {
  const sel = document.getElementById("rtPatientId");
  sel.innerHTML = allPatients.map(p =>
    `<option value="${p.patient_id}">${p.patient_id} (${p.priority_level}, Score: ${p.acuity_score})</option>`
  ).join("");
}
