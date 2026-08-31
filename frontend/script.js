/* ═══════════════════════════════════════════════
   VERIBORDER AI — FRONTEND SCRIPT
   Consumes the existing FastAPI backend at
   POST /analyze-document
   ═══════════════════════════════════════════════ */

// ── CONFIG ──────────────────────────────────────
const API_BASE_URL = "http://127.0.0.1:8000";
// ─────────────────────────────────────────────────

// ── DOM REFS ────────────────────────────────────
const views = {
  upload:  document.getElementById("upload-view"),
  loading: document.getElementById("loading-view"),
  results: document.getElementById("results-view"),
  error:   document.getElementById("error-view"),
};

const dropZone      = document.getElementById("drop-zone");
const fileInput     = document.getElementById("file-input");
const browseBtn     = document.getElementById("browse-btn");
const fileInfo      = document.getElementById("file-info");
const fileNameEl    = document.getElementById("file-name");
const fileRemoveBtn = document.getElementById("file-remove");
const analyzeBtn    = document.getElementById("analyze-btn");
const resetBtn      = document.getElementById("reset-btn");
const errorRetryBtn = document.getElementById("error-retry-btn");
const errorMsgEl    = document.getElementById("error-message");
const resultsContainer = document.getElementById("results-container");

const STEPS = ["step-upload", "step-ocr", "step-mrz", "step-image", "step-risk"];

let selectedFile = null;

// ── VIEW SWITCHING ──────────────────────────────
function showView(name) {
  Object.values(views).forEach(v => v.classList.remove("active"));
  views[name].classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── FILE SELECTION ──────────────────────────────
function setFile(file) {
  if (!file) return;

  const allowed = [
    "image/jpeg", "image/png", "image/jpg", "application/pdf",
  ];
  if (!allowed.includes(file.type)) {
    showError("Unsupported file type. Please upload a JPG, PNG, or PDF document.");
    return;
  }

  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileInfo.classList.remove("hidden");
  analyzeBtn.disabled = false;
}

function clearFile() {
  selectedFile = null;
  fileInput.value = "";
  fileInfo.classList.add("hidden");
  analyzeBtn.disabled = true;
}

// Browse button
browseBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.click();
});

// Drop zone click
dropZone.addEventListener("click", () => fileInput.click());

// Keyboard accessibility
dropZone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
});

// File input change
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) setFile(fileInput.files[0]);
});

// Remove selected file
fileRemoveBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  clearFile();
});

// Drag & drop
dropZone.addEventListener("dragover",  (e) => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", ()  => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  if (e.dataTransfer.files.length > 0) setFile(e.dataTransfer.files[0]);
});

// ── LOADING STEP ANIMATION ──────────────────────
function resetSteps() {
  STEPS.forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove("active", "done");
    el.querySelector(".step-icon").textContent = "◌";
  });
}

function completeStep(id) {
  const el = document.getElementById(id);
  el.classList.remove("active");
  el.classList.add("done");
  el.querySelector(".step-icon").textContent = "";
}

function activateStep(id) {
  const el = document.getElementById(id);
  el.classList.add("active");
}

async function animateLoading() {
  resetSteps();
  // Step 1: upload — already active in HTML
  activateStep(STEPS[0]);
  await delay(400);
  completeStep(STEPS[0]);

  activateStep(STEPS[1]);
  await delay(500);
  completeStep(STEPS[1]);

  activateStep(STEPS[2]);
  await delay(400);
  // Steps 3–5 stay pending until API returns
}

function finishLoadingSteps() {
  STEPS.forEach(id => {
    completeStep(id);
  });
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ── ANALYZE ─────────────────────────────────────
analyzeBtn.addEventListener("click", analyze);

async function analyze() {
  if (!selectedFile) return;

  showView("loading");
  animateLoading();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze-document`, {
      method: "POST",
      body: formData,
    });

    finishLoadingSteps();
    await delay(300);

    if (!response.ok) {
      let detail = `Server returned ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson.detail) detail = errJson.detail;
      } catch (_) {}
      showError(detail);
      return;
    }

    const data = await response.json();

    if (!data || typeof data !== "object") {
      showError("The server returned an invalid response.");
      return;
    }

    renderResults(data);
    showView("results");

  } catch (err) {
    console.error("Analysis error:", err);

    if (err.name === "TypeError" && err.message === "Failed to fetch") {
      showError(
        "Unable to reach the VeriBorder backend. " +
        "Please make sure the server is running at " + API_BASE_URL
      );
    } else {
      showError(err.message || "An unexpected error occurred during analysis.");
    }
  }
}

// ── ERROR ───────────────────────────────────────
function showError(message) {
  errorMsgEl.textContent = message;
  showView("error");
}

// ── RESET ───────────────────────────────────────
resetBtn.addEventListener("click", resetToUpload);
errorRetryBtn.addEventListener("click", resetToUpload);

function resetToUpload() {
  clearFile();
  resultsContainer.innerHTML = "";
  resetSteps();
  showView("upload");
}

// ═══════════════════════════════════════════════
// RESULTS RENDERING
// ═══════════════════════════════════════════════

function renderResults(data) {
  resultsContainer.innerHTML = "";

  // 1 — Risk Assessment Banner
  resultsContainer.appendChild(renderRiskBanner(data.risk_assessment));

  // 2 — Document Information
  resultsContainer.appendChild(renderDocumentInfo(data.visual_data));

  // 3 — OCR ↔ MRZ Validation
  resultsContainer.appendChild(renderValidation(data.validation));

  // 4 — Image & Tampering Analysis
  resultsContainer.appendChild(
    renderImageAnalysis(data.image_analysis, data.face_detection, data.tampering_analysis)
  );

  // 5 — Reasons / Flags
  resultsContainer.appendChild(renderFlags(data.risk_assessment));
}

// ── SECTION 1: RISK BANNER ──────────────────────
function renderRiskBanner(risk) {
  const level = (risk.risk_level || "LOW").toUpperCase();
  const label = risk.label || risk.risk_level || "UNKNOWN";
  const score = risk.risk_score ?? 0;

  const levelClass = level === "HIGH" ? "risk-high"
                   : level === "MEDIUM" ? "risk-medium"
                   : "risk-low";

  const summaryText = level === "LOW"
    ? "No significant inconsistencies detected"
    : level === "MEDIUM"
    ? "Some indicators require further review"
    : "High-risk indicators detected — document requires further review";

  const section = document.createElement("div");
  section.className = `risk-banner ${levelClass}`;
  section.innerHTML = `
    <div class="risk-banner-label">Document Assessment</div>
    <div class="risk-badge"><span class="risk-dot"></span> ${esc(label)}</div>
    <div class="risk-score">Risk Score: ${score} / 100</div>
    <div class="risk-summary">${esc(summaryText)}</div>
  `;
  return section;
}

// ── SECTION 2: DOCUMENT INFORMATION ─────────────
function renderDocumentInfo(visual) {
  const fields = [
    ["Document Type",   visual.document_type],
    ["Passport Number", visual.passport_number],
    ["Surname",         visual.surname],
    ["Given Name(s)",   visual.given_names],
    ["Nationality",     visual.nationality],
    ["Date of Birth",   visual.date_of_birth],
    ["Sex",             visual.sex],
    ["Place of Birth",  visual.place_of_birth],
    ["Date of Issue",   visual.date_of_issue],
    ["Date of Expiry",  visual.date_of_expiry],
  ];

  let rows = fields.map(([label, value]) => `
    <tr>
      <td class="label-cell">${esc(label)}</td>
      <td>${value != null ? esc(String(value)) : '<span style="color:var(--color-text-muted)">Not detected</span>'}</td>
    </tr>
  `).join("");

  const section = createSection(
    "Document Information",
    `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`
  );
  section.innerHTML += `<table class="data-table">${rows}</table>`;
  return section;
}

// ── SECTION 3: VALIDATION ───────────────────────
function renderValidation(validation) {
  const fieldLabels = {
    passport_number: "Passport Number",
    surname:         "Surname",
    given_names:     "Given Names",
    nationality:     "Nationality",
    date_of_birth:   "Date of Birth",
    date_of_expiry:  "Date of Expiry",
  };

  let rows = "";
  for (const [key, entry] of Object.entries(validation)) {
    const label  = fieldLabels[key] || key;
    const status = (entry.status || "").toUpperCase();
    const badgeClass = status === "MATCH"     ? "status-match"
                     : status === "MISMATCH"  ? "status-mismatch"
                     : "status-uncertain";
    const badgeIcon  = status === "MATCH" ? "✓" : status === "MISMATCH" ? "✗" : "?";

    rows += `
      <tr>
        <td class="label-cell">${esc(label)}</td>
        <td>${esc(entry.visual ?? "—")}</td>
        <td>${esc(entry.mrz ?? "—")}</td>
        <td><span class="status-badge ${badgeClass}">${badgeIcon} ${esc(status)}</span></td>
      </tr>
    `;
  }

  const section = createSection(
    "OCR ↔ MRZ Validation",
    `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`
  );
  section.innerHTML += `
    <table class="data-table">
      <thead><tr>
        <th>Field</th><th>Visual / OCR</th><th>MRZ</th><th>Status</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
  return section;
}

// ── SECTION 4: IMAGE & TAMPERING ────────────────
function renderImageAnalysis(image, face, tampering) {
  const section = createSection(
    "Image &amp; Security Analysis",
    `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`
  );

  // Image metadata grid
  const exifStatus = image.has_exif ? "Present" : "None detected";
  section.innerHTML += `
    <div class="image-grid">
      <div class="image-stat">
        <span class="image-stat-label">Format</span>
        <span class="image-stat-value">${esc(image.format || "—")}</span>
      </div>
      <div class="image-stat">
        <span class="image-stat-label">Resolution</span>
        <span class="image-stat-value">${image.width || "—"} × ${image.height || "—"}</span>
      </div>
      <div class="image-stat">
        <span class="image-stat-label">EXIF Metadata</span>
        <span class="image-stat-value">${esc(exifStatus)}</span>
      </div>
      <div class="image-stat">
        <span class="image-stat-label">Portrait Regions</span>
        <span class="image-stat-value">${face.faces_detected ?? 0}</span>
      </div>
    </div>
  `;

  // ELA cards
  if (Array.isArray(tampering) && tampering.length > 0) {
    const cardsHtml = tampering.map(t => {
      const level = (t.level || "LOW").toUpperCase();
      const barWidth = Math.min(t.ela_score, 100);
      const levelClass = level === "HIGH" ? "level-high"
                       : level === "MEDIUM" ? "level-medium"
                       : "level-low";
      return `
        <div class="ela-card">
          <div class="ela-card-title">${esc(t.region)}</div>
          <div class="ela-row">
            <span class="label">Image anomaly indicator</span>
            <span>${t.ela_score.toFixed(2)} / 100</span>
          </div>
          <div class="ela-row">
            <span class="label">Anomaly level</span>
            <span class="status-badge ${level === "HIGH" ? "status-mismatch" : level === "MEDIUM" ? "status-uncertain" : "status-match"}">${esc(level)}</span>
          </div>
          <div class="ela-bar-track">
            <div class="ela-bar-fill ${levelClass}" style="width:${barWidth}%"></div>
          </div>
        </div>
      `;
    }).join("");

    section.innerHTML += `<div class="ela-cards">${cardsHtml}</div>`;
  }

  return section;
}

// ── SECTION 5: REASONS / FLAGS ──────────────────
function renderFlags(risk) {
  const section = createSection(
    "Analysis Flags",
    `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>`
  );

  const reasons = risk.reasons || [];

  if (reasons.length === 0) {
    section.innerHTML += `
      <div class="flags-list">
        <div class="flag-item flag-clear">
          <span class="flag-icon">✓</span>
          <span>No significant anomalies detected</span>
        </div>
      </div>
    `;
  } else {
    const flagsHtml = reasons.map(r => `
      <div class="flag-item flag-warning">
        <span class="flag-icon">⚠</span>
        <span>${esc(r)}</span>
      </div>
    `).join("");
    section.innerHTML += `<div class="flags-list">${flagsHtml}</div>`;
  }

  return section;
}

// ── HELPERS ─────────────────────────────────────
function createSection(title, iconSvg) {
  const section = document.createElement("div");
  section.className = "results-section";
  section.innerHTML = `<div class="results-section-title">${iconSvg || ""} ${title}</div>`;
  return section;
}

function esc(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

