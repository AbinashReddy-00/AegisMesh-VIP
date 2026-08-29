/**
 * AegisMesh — Main Application Controller
 * Handles state, events, KPI cards, filter tabs, live decision rendering,
 * and strict form/evaluation state synchronization.
 */

import { api } from "./api.js";
import { renderTopology, highlightFlow } from "./topology.js";
import { runSimulation } from "./simulator.js";

let currentTopology = null;
let currentDomainFilter = "ALL";
let lastEvaluatedFlow = null; // { sourceId, targetId, action }

// Scenario definition mapping for instant form synchronization
const SCENARIO_MAP = {
  "PT-01": { source: "FAC-PC-01", target: "APP-SRV-01", action: "CONNECT" },
  "E-04": { source: "FAC-PC-01", target: "DB-SRV-01", action: "CONNECT" },
  "E-02": { source: "APP-SRV-01", target: "MGMT-SRV-01", action: "ADMIN" },
  "ARCH-SCENARIO-01": { source: "DB-SRV-01", target: "FAC-PC-01", action: "CONNECT" },
  "I-01": { source: "k8s-edu-api", target: "k8s-fin-db", action: "WRITE" },
};

async function init() {
  await refreshDashboard();

  // 1. Bind Domain Filter Tabs
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentDomainFilter = btn.getAttribute("data-filter");
      renderTopology(currentTopology, onNodeSelect, currentDomainFilter);
    });
  });

  // 2. Bind Scenario Simulation Buttons with form synchronization
  document.querySelectorAll(".scenario-card-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const scenId = btn.getAttribute("data-scenario");
      syncFormToScenario(scenId);

      runSimulation(scenId, (result) => {
        const srcNode = currentTopology?.nodes.find((n) => n.id === result.source.workload_id);
        const dstNode = currentTopology?.nodes.find((n) => n.id === result.destination.resource_id);

        lastEvaluatedFlow = {
          sourceId: result.source.workload_id,
          targetId: result.destination.resource_id,
          action: result.action,
        };

        displayEvaluationResult(result.evaluation, srcNode, dstNode, result.action);
        refreshIncidentsAndLogs();
        refreshKpiStats();
      });
    });
  });

  // 3. Bind Custom Evaluator Form
  const form = document.getElementById("eval-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await handleCustomEvaluate();
    });
  }

  // 4. Bind Dropdown Change Listeners for State Consistency
  const srcSelect = document.getElementById("eval-source");
  const dstSelect = document.getElementById("eval-target");
  const actSelect = document.getElementById("eval-action");

  [srcSelect, dstSelect, actSelect].forEach((el) => {
    if (el) {
      el.addEventListener("change", handleDropdownSelectionChange);
    }
  });

  // 5. Bind Manual Quarantine Button
  const quarantineBtn = document.getElementById("btn-manual-quarantine");
  if (quarantineBtn) {
    quarantineBtn.addEventListener("click", async () => {
      const workloadId = document.getElementById("eval-source")?.value;
      if (!workloadId) {
        alert("Select a source workload in the evaluator form to quarantine.");
        return;
      }
      await api.isolateWorkload(workloadId, "Manual Security Analyst Quarantine Triggered");
      await refreshDashboard();
    });
  }
}

function syncFormToScenario(scenarioId) {
  const scen = SCENARIO_MAP[scenarioId];
  if (!scen) return;

  const srcSelect = document.getElementById("eval-source");
  const dstSelect = document.getElementById("eval-target");
  const actSelect = document.getElementById("eval-action");

  if (srcSelect) srcSelect.value = scen.source;
  if (dstSelect) dstSelect.value = scen.target;
  if (actSelect) actSelect.value = scen.action;
}

function handleDropdownSelectionChange() {
  const currentSrc = document.getElementById("eval-source")?.value;
  const currentDst = document.getElementById("eval-target")?.value;
  const currentAct = document.getElementById("eval-action")?.value;

  // Check if current form differs from last evaluated flow
  if (
    lastEvaluatedFlow &&
    (lastEvaluatedFlow.sourceId !== currentSrc ||
      lastEvaluatedFlow.targetId !== currentDst ||
      lastEvaluatedFlow.action !== currentAct)
  ) {
    markEvaluationAsStale(currentSrc, currentDst, currentAct);
  }
}

function markEvaluationAsStale(newSrc, newDst, newAct) {
  const container = document.getElementById("decision-panel");
  if (!container) return;

  const srcNode = currentTopology?.nodes.find((n) => n.id === newSrc);
  const dstNode = currentTopology?.nodes.find((n) => n.id === newDst);

  const srcLabel = srcNode ? `${srcNode.name} (${srcNode.id})` : newSrc;
  const dstLabel = dstNode ? `${dstNode.name} (${dstNode.id})` : newDst;

  container.innerHTML = `
    <div class="decision-hero-card" style="border-color: var(--status-restrict); background: rgba(245, 158, 11, 0.06);">
      <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(245, 158, 11, 0.25); padding-bottom: 12px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 20px;">⚠️</span>
          <div>
            <div style="font-size: 13px; font-weight: 800; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.5px;">
              Selections Changed — Evaluation Outdated
            </div>
            <div style="font-size: 11px; color: var(--text-secondary);">
              Dropdown parameters modified. Click <strong>EVALUATE</strong> to compute decision for the newly selected flow.
            </div>
          </div>
        </div>
        <button type="button" onclick="document.getElementById('eval-form').requestSubmit();" 
                style="background: linear-gradient(135deg, #00f2fe, #4facfe); color: #060913; border: none; font-weight: 800; font-size: 10px; padding: 7px 14px; border-radius: var(--radius-sm); cursor: pointer;">
          EVALUATE NOW ⚡
        </button>
      </div>

      <div style="font-size: 12px; font-family: var(--font-mono); color: #f8fafc; background: rgba(0, 0, 0, 0.3); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px dashed rgba(245, 158, 11, 0.3);">
        <span style="color: #94a3b8;">Pending Request:</span> 
        <span style="color: #38bdf8; font-weight: 700;">${srcLabel}</span> 
        <span style="color: #fbbf24;">—[${newAct}]—▶</span> 
        <span style="color: #ec4899; font-weight: 700;">${dstLabel}</span>
      </div>
    </div>
  `;
}

function onNodeSelect(node) {
  const srcSelect = document.getElementById("eval-source");
  const dstSelect = document.getElementById("eval-target");

  if (!srcSelect || !dstSelect) return;

  // If source is already set to this node, set target instead, otherwise set source
  if (srcSelect.value === node.id) {
    // Already source, do nothing
  } else if (!srcSelect.value || srcSelect.value === dstSelect.value) {
    srcSelect.value = node.id;
  } else {
    // Prompt or set target
    dstSelect.value = node.id;
  }

  handleDropdownSelectionChange();
}

async function refreshDashboard() {
  try {
    currentTopology = await api.getTopology();
    renderTopology(currentTopology, onNodeSelect, currentDomainFilter);
    populateDropdowns(currentTopology.nodes);
    await refreshIncidentsAndLogs();
    refreshKpiStats();
  } catch (err) {
    console.error("Dashboard refresh error:", err);
  }
}

function refreshKpiStats() {
  if (!currentTopology) return;

  const nodeCountEl = document.getElementById("stat-nodes-count");
  if (nodeCountEl) nodeCountEl.textContent = currentTopology.nodes.length;

  const containedNodes = currentTopology.nodes.filter((n) => n.state === "CONTAINED");
  const containedCountEl = document.getElementById("stat-contained-count");
  if (containedCountEl) {
    containedCountEl.textContent = containedNodes.length;
    containedCountEl.style.color = containedNodes.length > 0 ? "var(--status-isolate)" : "#ffffff";
  }
}

function populateDropdowns(nodes) {
  const srcSelect = document.getElementById("eval-source");
  const dstSelect = document.getElementById("eval-target");

  if (!srcSelect || !dstSelect) return;

  const prevSrc = srcSelect.value;
  const prevDst = dstSelect.value;

  srcSelect.innerHTML = nodes
    .map((n) => `<option value="${n.id}">[${n.domain.substring(0, 3)}] ${n.id} — ${n.name}</option>`)
    .join("");

  dstSelect.innerHTML = nodes
    .map((n) => `<option value="${n.id}">[${n.domain.substring(0, 3)}] ${n.id} — ${n.name}</option>`)
    .join("");

  // Default initial configuration: Faculty PC -> App Server (Normal Flow)
  if (prevSrc && nodes.some((n) => n.id === prevSrc)) {
    srcSelect.value = prevSrc;
  } else {
    srcSelect.value = "FAC-PC-01";
  }

  if (prevDst && nodes.some((n) => n.id === prevDst)) {
    dstSelect.value = prevDst;
  } else {
    dstSelect.value = "APP-SRV-01";
  }
}

async function handleCustomEvaluate() {
  const srcId = document.getElementById("eval-source").value;
  const dstId = document.getElementById("eval-target").value;
  const action = document.getElementById("eval-action").value;

  const srcNode = currentTopology.nodes.find((n) => n.id === srcId);
  const dstNode = currentTopology.nodes.find((n) => n.id === dstId);

  if (!srcNode || !dstNode) return;

  const payload = {
    source: {
      workload_id: srcNode.id,
      domain: srcNode.domain,
      zone: srcNode.zone,
      ip_address: srcNode.ip_address,
    },
    destination: {
      resource_id: dstNode.id,
      resource_type: dstNode.id.includes("DB") ? "DATABASE" : "SERVICE",
      domain: dstNode.domain,
      zone: dstNode.zone,
      sensitivity: dstNode.is_critical ? "RESTRICTED" : "INTERNAL",
      ip_address: dstNode.ip_address,
    },
    action: action,
    context: {
      source_zone: srcNode.zone,
      is_anomaly: false,
    },
  };

  const evalRes = await api.evaluateRequest(payload);
  lastEvaluatedFlow = { sourceId: srcNode.id, targetId: dstNode.id, action: action };

  displayEvaluationResult(evalRes, srcNode, dstNode, action);
  highlightFlow(srcNode.id, dstNode.id, evalRes.decision);
  await refreshIncidentsAndLogs();
  refreshKpiStats();
}

function displayEvaluationResult(evaluation, srcNode, dstNode, action) {
  const container = document.getElementById("decision-panel");
  if (!container) return;

  // Source & Destination Labels
  const srcId = srcNode ? srcNode.id : "SOURCE";
  const srcName = srcNode ? srcNode.name : srcId;
  const srcZone = srcNode ? srcNode.zone : "";
  const srcIp = srcNode?.ip_address ? ` (${srcNode.ip_address})` : "";

  const dstId = dstNode ? dstNode.id : "DESTINATION";
  const dstName = dstNode ? dstNode.name : dstId;
  const dstZone = dstNode ? dstNode.zone : "";
  const dstIp = dstNode?.ip_address ? ` (${dstNode.ip_address})` : "";

  // Risk meter bar color
  let barColor = "var(--status-allow)";
  if (evaluation.risk_score > 30) barColor = "#38bdf8";
  if (evaluation.risk_score > 60) barColor = "var(--status-restrict)";
  if (evaluation.risk_score > 80) barColor = "var(--status-block)";

  let factorsHtml = "";
  if (evaluation.factors) {
    factorsHtml = `
      <table class="risk-factor-table">
        <thead>
          <tr>
            <th>Evaluated Risk Factor</th>
            <th>Weight</th>
            <th>Score</th>
            <th>Weighted</th>
            <th>Architectural Context</th>
          </tr>
        </thead>
        <tbody>
          ${evaluation.factors
            .map(
              (f) => `
            <tr>
              <td style="font-weight: 700; color: #f8fafc;">${f.name}</td>
              <td style="color: var(--text-secondary);">${Math.round(f.weight * 100)}%</td>
              <td style="color: #38bdf8; font-family: var(--font-mono); font-weight: 700;">${f.score}/100</td>
              <td style="color: #fbbf24; font-family: var(--font-mono); font-weight: 700;">${f.weighted_score}</td>
              <td style="color: var(--text-secondary); font-size: 10px;">${f.description}</td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    `;
  }

  container.innerHTML = `
    <div class="decision-hero-card">
      <!-- Evaluated Access Flow Context Bar -->
      <div style="background: rgba(0, 0, 0, 0.4); padding: 8px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-family: var(--font-mono);">
        <div>
          <span style="color: var(--text-muted);">EVALUATED ACCESS FLOW:</span>
          <span style="color: #38bdf8; font-weight: 700;">${srcName} [${srcId}]${srcIp}</span>
          <span style="color: #fbbf24; margin: 0 6px;">—[${action || "CONNECT"}]—▶</span>
          <span style="color: #ec4899; font-weight: 700;">${dstName} [${dstId}]${dstIp}</span>
        </div>
        <div style="font-size: 10px; color: var(--text-muted);">
          Zone: <span style="color: #7dd3fc;">${srcZone}</span> ➔ <span style="color: #7dd3fc;">${dstZone}</span>
        </div>
      </div>

      <div class="decision-hero-header">
        <div>
          <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 4px;">
            Zero-Trust Decision Engine Verdict
          </div>
          <span class="decision-badge-large ${evaluation.decision}">
            ${evaluation.decision}
          </span>
        </div>

        <div class="risk-gauge-block">
          <div style="text-align: right;">
            <div style="font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Composite Risk</div>
            <div class="risk-number" style="color: ${barColor};">
              ${evaluation.risk_score}/100 <span style="font-size: 11px; font-weight: 700;">(${evaluation.risk_level})</span>
            </div>
          </div>
          <div class="risk-progress-track">
            <div class="risk-progress-fill" style="width: ${evaluation.risk_score}%; background: ${barColor};"></div>
          </div>
        </div>
      </div>

      <div class="decision-summary-text">
        <strong>Verdict Rationale:</strong> ${evaluation.explanation}
      </div>

      <div class="decision-meta-tags">
        <div>Enforcement Point: <span>${evaluation.enforcement_layer}</span></div>
        <div>Request ID: <span>${evaluation.request_id}</span></div>
        <div>Audit ID: <span>${evaluation.audit_id}</span></div>
      </div>

      <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--accent-cyan); margin: 16px 0 8px 0; letter-spacing: 0.5px;">
        Multi-Factor Risk Scoring Decomposition (6 Architectural Factors)
      </div>
      ${factorsHtml}
    </div>
  `;
}

async function refreshIncidentsAndLogs() {
  const incidents = await api.getIncidents();
  const logs = await api.getAuditLogs();

  // Render Incidents Feed
  const incContainer = document.getElementById("incident-list");
  if (incContainer) {
    if (incidents.length === 0) {
      incContainer.innerHTML = `<div style="font-size: 11px; color: var(--text-muted); padding: 12px;">No active containment incidents. All workloads nominal.</div>`;
    } else {
      incContainer.innerHTML = incidents
        .map(
          (inc) => `
        <div class="feed-card" style="border-left: 3px solid ${inc.status === "ACTIVE" ? "var(--status-isolate)" : "var(--status-allow)"};">
          <div>
            <div class="feed-header" style="color: ${inc.status === "ACTIVE" ? "var(--status-isolate)" : "var(--status-allow)"};">
              [${inc.threat_id}] ${inc.title}
            </div>
            <div class="feed-sub">${inc.workload_name} (${inc.zone}) • Status: <strong>${inc.status}</strong></div>
          </div>
          <div>
            ${
              inc.status === "ACTIVE"
                ? `<button class="btn-restore-pill" data-id="${inc.workload_id}">Lift Quarantine</button>`
                : `<span style="font-size: 10px; color: var(--text-muted); font-weight: 600;">Resolved</span>`
            }
          </div>
        </div>
      `
        )
        .join("");

      // Bind restore buttons
      incContainer.querySelectorAll(".btn-restore-pill").forEach((b) => {
        b.addEventListener("click", async () => {
          const wId = b.getAttribute("data-id");
          await api.restoreWorkload(wId);
          await refreshDashboard();
        });
      });
    }
  }

  // Render Audit Logs Feed
  const auditContainer = document.getElementById("audit-list");
  if (auditContainer) {
    auditContainer.innerHTML = logs
      .slice(0, 10)
      .map(
        (l) => `
      <div class="feed-card">
        <div>
          <div class="feed-header">${l.actor} → ${l.target}</div>
          <div class="feed-sub">${l.details}</div>
        </div>
        <div style="text-align: right;">
          <span class="badge-status ${l.decision.toLowerCase()}" style="font-size: 9px;">
            ${l.decision}
          </span>
          <div style="font-size: 9px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 3px;">
            Risk: ${l.risk_score}/100
          </div>
        </div>
      </div>
    `
      )
      .join("");
  }
}

document.addEventListener("DOMContentLoaded", init);
