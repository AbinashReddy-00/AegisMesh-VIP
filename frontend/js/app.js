/**
 * AegisMesh — Main Application Controller
 *
 * Handles:
 * - Dashboard initialization
 * - Topology rendering
 * - Domain filtering
 * - Scenario simulation
 * - Zero-Trust evaluation
 * - KPI statistics
 * - Incidents
 * - Audit logs
 * - LIVE SIEM SECURITY EVENTS
 */

import { api } from "./api.js";
import { renderTopology, highlightFlow } from "./topology.js";
import { runSimulation } from "./simulator.js";


/* ============================================================================
   GLOBAL STATE
   ============================================================================ */

let currentTopology = null;
let currentDomainFilter = "ALL";

let lastEvaluatedFlow = null;
// {
//   sourceId,
//   targetId,
//   action
// }


/* ============================================================================
   SCENARIO DEFINITIONS
   ============================================================================ */

const SCENARIO_MAP = {

  "PT-01": {
    source: "FAC-PC-01",
    target: "APP-SRV-01",
    action: "CONNECT",
  },

  "E-04": {
    source: "FAC-PC-01",
    target: "DB-SRV-01",
    action: "CONNECT",
  },

  "E-02": {
    source: "APP-SRV-01",
    target: "MGMT-SRV-01",
    action: "ADMIN",
  },

  "ARCH-SCENARIO-01": {
    source: "DB-SRV-01",
    target: "FAC-PC-01",
    action: "CONNECT",
  },

  "I-01": {
    source: "k8s-edu-api",
    target: "k8s-fin-db",
    action: "WRITE",
  },

};


/* ============================================================================
   APPLICATION INITIALIZATION
   ============================================================================ */

async function init() {

  await refreshDashboard();


  /* --------------------------------------------------------------------------
     DOMAIN FILTER TABS
     -------------------------------------------------------------------------- */

  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => {

      btn.addEventListener("click", () => {

        document
          .querySelectorAll(".tab-btn")
          .forEach((b) => {
            b.classList.remove("active");
          });


        btn.classList.add("active");


        currentDomainFilter =
          btn.getAttribute("data-filter") || "ALL";


        renderTopology(
          currentTopology,
          onNodeSelect,
          currentDomainFilter
        );

      });

    });


  /* --------------------------------------------------------------------------
     SCENARIO SIMULATION BUTTONS
     -------------------------------------------------------------------------- */

  document
    .querySelectorAll(".scenario-card-btn")
    .forEach((btn) => {

      btn.addEventListener("click", () => {

        const scenId =
          btn.getAttribute("data-scenario");


        /* Synchronize evaluator form */

        syncFormToScenario(scenId);


        /* Run simulation */

        runSimulation(
          scenId,
          async (result) => {

            const srcNode =
              currentTopology?.nodes.find(
                (n) =>
                  n.id === result.source.workload_id
              );


            const dstNode =
              currentTopology?.nodes.find(
                (n) =>
                  n.id === result.destination.resource_id
              );


            lastEvaluatedFlow = {

              sourceId:
                result.source.workload_id,

              targetId:
                result.destination.resource_id,

              action:
                result.action,

            };


            displayEvaluationResult(
              result.evaluation,
              srcNode,
              dstNode,
              result.action
            );


            highlightFlow(
              result.source.workload_id,
              result.destination.resource_id,
              result.evaluation.decision
            );


            currentTopology = await api.getTopology();

            renderTopology(
              currentTopology,
              onNodeSelect,
              currentDomainFilter
            );

            populateDropdowns(
              currentTopology.nodes
            );

            await refreshIncidentsAndLogs();

            refreshKpiStats();

          }
        );

      });

    });


  /* --------------------------------------------------------------------------
     CUSTOM ZERO-TRUST EVALUATOR
     -------------------------------------------------------------------------- */

  const form =
    document.getElementById("eval-form");


  if (form) {

    form.addEventListener(
      "submit",
      async (e) => {

        e.preventDefault();

        await handleCustomEvaluate();

      }
    );

  }


  /* --------------------------------------------------------------------------
     DROPDOWN LISTENERS
     -------------------------------------------------------------------------- */

  const srcSelect =
    document.getElementById("eval-source");

  const dstSelect =
    document.getElementById("eval-target");

  const actSelect =
    document.getElementById("eval-action");


  [
    srcSelect,
    dstSelect,
    actSelect,
  ].forEach((el) => {

    if (el) {

      el.addEventListener(
        "change",
        handleDropdownSelectionChange
      );

    }

  });


  /* --------------------------------------------------------------------------
     MANUAL QUARANTINE
     -------------------------------------------------------------------------- */

  const quarantineBtn =
    document.getElementById(
      "btn-manual-quarantine"
    );


  if (quarantineBtn) {

    quarantineBtn.addEventListener(
      "click",
      async () => {

        const workloadId =
          document.getElementById(
            "eval-source"
          )?.value;


        if (!workloadId) {

          alert(
            "Select a source workload in the evaluator form to quarantine."
          );

          return;

        }


        try {

          await api.isolateWorkload(
            workloadId,
            "Manual Security Analyst Quarantine Triggered"
          );


          await refreshDashboard();

        } catch (err) {

          console.error(
            "Manual quarantine failed:",
            err
          );


          alert(
            "Unable to quarantine the selected workload."
          );

        }

      }
    );

  }

}


/* ============================================================================
   SCENARIO → FORM SYNCHRONIZATION
   ============================================================================ */

function syncFormToScenario(scenarioId) {

  const scen =
    SCENARIO_MAP[scenarioId];


  if (!scen) {

    console.warn(
      `Unknown scenario ID: ${scenarioId}`
    );

    return;

  }


  const srcSelect =
    document.getElementById(
      "eval-source"
    );

  const dstSelect =
    document.getElementById(
      "eval-target"
    );

  const actSelect =
    document.getElementById(
      "eval-action"
    );


  if (srcSelect) {

    srcSelect.value =
      scen.source;

  }


  if (dstSelect) {

    dstSelect.value =
      scen.target;

  }


  if (actSelect) {

    actSelect.value =
      scen.action;

  }

}


/* ============================================================================
   DROPDOWN STATE SYNCHRONIZATION
   ============================================================================ */

function handleDropdownSelectionChange() {

  const currentSrc =
    document.getElementById(
      "eval-source"
    )?.value;


  const currentDst =
    document.getElementById(
      "eval-target"
    )?.value;


  const currentAct =
    document.getElementById(
      "eval-action"
    )?.value;


  if (
    lastEvaluatedFlow &&
    (
      lastEvaluatedFlow.sourceId !== currentSrc ||
      lastEvaluatedFlow.targetId !== currentDst ||
      lastEvaluatedFlow.action !== currentAct
    )
  ) {

    markEvaluationAsStale(
      currentSrc,
      currentDst,
      currentAct
    );

  }

}


/* ============================================================================
   STALE EVALUATION WARNING
   ============================================================================ */

function markEvaluationAsStale(
  newSrc,
  newDst,
  newAct
) {

  const container =
    document.getElementById(
      "decision-panel"
    );


  if (!container) {
    return;
  }


  const srcNode =
    currentTopology?.nodes.find(
      (n) => n.id === newSrc
    );


  const dstNode =
    currentTopology?.nodes.find(
      (n) => n.id === newDst
    );


  const srcLabel =
    srcNode
      ? `${srcNode.name} (${srcNode.id})`
      : newSrc;


  const dstLabel =
    dstNode
      ? `${dstNode.name} (${dstNode.id})`
      : newDst;


  container.innerHTML = `

    <div
      class="decision-hero-card"
      style="
        border-color: var(--status-restrict);
        background: rgba(245, 158, 11, 0.06);
      "
    >

      <div
        style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid rgba(245, 158, 11, 0.25);
          padding-bottom: 12px;
          margin-bottom: 14px;
        "
      >

        <div
          style="
            display: flex;
            align-items: center;
            gap: 10px;
          "
        >

          <span style="font-size: 20px;">
            ⚠️
          </span>

          <div>

            <div
              style="
                font-size: 13px;
                font-weight: 800;
                color: #fbbf24;
                text-transform: uppercase;
                letter-spacing: 0.5px;
              "
            >
              Selections Changed — Evaluation Outdated
            </div>

            <div
              style="
                font-size: 11px;
                color: var(--text-secondary);
              "
            >
              Dropdown parameters modified.
              Click <strong>EVALUATE</strong> to compute
              the decision for the newly selected flow.
            </div>

          </div>

        </div>


        <button
          type="button"
          onclick="document.getElementById('eval-form').requestSubmit();"
          style="
            background: linear-gradient(
              135deg,
              #00f2fe,
              #4facfe
            );
            color: #060913;
            border: none;
            font-weight: 800;
            font-size: 10px;
            padding: 7px 14px;
            border-radius: var(--radius-sm);
            cursor: pointer;
          "
        >
          EVALUATE NOW ⚡
        </button>

      </div>


      <div
        style="
          font-size: 12px;
          font-family: var(--font-mono);
          color: #f8fafc;
          background: rgba(0, 0, 0, 0.3);
          padding: 10px 14px;
          border-radius: var(--radius-sm);
          border: 1px dashed rgba(245, 158, 11, 0.3);
        "
      >

        <span style="color: #94a3b8;">
          Pending Request:
        </span>

        <span
          style="
            color: #38bdf8;
            font-weight: 700;
          "
        >
          ${srcLabel}
        </span>

        <span style="color: #fbbf24;">
          —[${newAct}]—▶
        </span>

        <span
          style="
            color: #ec4899;
            font-weight: 700;
          "
        >
          ${dstLabel}
        </span>

      </div>

    </div>

  `;

}


/* ============================================================================
   TOPOLOGY NODE SELECTION
   ============================================================================ */

function onNodeSelect(node) {

  const srcSelect =
    document.getElementById(
      "eval-source"
    );


  const dstSelect =
    document.getElementById(
      "eval-target"
    );


  if (!srcSelect || !dstSelect) {
    return;
  }


  if (srcSelect.value === node.id) {

    return;

  }


  if (
    !srcSelect.value ||
    srcSelect.value === dstSelect.value
  ) {

    srcSelect.value =
      node.id;

  } else {

    dstSelect.value =
      node.id;

  }


  handleDropdownSelectionChange();

}


/* ============================================================================
   DASHBOARD REFRESH
   ============================================================================ */

async function refreshDashboard() {

  try {

    currentTopology =
      await api.getTopology();


    if (!currentTopology) {

      console.error(
        "Topology API returned no data."
      );

      return;

    }


    renderTopology(
      currentTopology,
      onNodeSelect,
      currentDomainFilter
    );


    populateDropdowns(
      currentTopology.nodes
    );


    await updateK8sStatus();

    await refreshIncidentsAndLogs();

    refreshKpiStats();

  } catch (err) {

    console.error(
      "Dashboard refresh error:",
      err
    );

  }

}


/* ============================================================================
   KUBERNETES STATUS
   ============================================================================ */

async function updateK8sStatus() {

  const statusText =
    document.getElementById(
      "k8s-status-text"
    );


  const statusDot =
    document.getElementById(
      "k8s-status-dot"
    );


  const statusPill =
    document.getElementById(
      "k8s-status-pill"
    );


  if (
    !statusText ||
    !statusDot ||
    !statusPill
  ) {

    return;

  }


  try {

    const k8s =
      await api.getK8sStatus();


    if (k8s.connected) {

      statusText.textContent =
        `K8S: CONNECTED (${k8s.cni})`;

      statusText.style.color =
        "#38bdf8";

      statusDot.style.background =
        "#10b981";

      statusDot.style.boxShadow =
        "0 0 8px #10b981";

      statusPill.style.borderColor =
        "rgba(16, 185, 129, 0.4)";

      statusPill.style.background =
        "rgba(16, 185, 129, 0.1)";

    } else {

      statusText.textContent =
        "K8S: OFFLINE (Simulated)";

      statusText.style.color =
        "#f59e0b";

      statusDot.style.background =
        "#f59e0b";

      statusDot.style.boxShadow =
        "0 0 8px #f59e0b";

      statusPill.style.borderColor =
        "rgba(245, 158, 11, 0.3)";

      statusPill.style.background =
        "rgba(245, 158, 11, 0.1)";

    }

  } catch (e) {

    console.error(
      "Kubernetes status check failed:",
      e
    );


    statusText.textContent =
      "K8S: OFFLINE";

    statusText.style.color =
      "#f59e0b";

    statusDot.style.background =
      "#f59e0b";

    statusDot.style.boxShadow =
      "0 0 8px #f59e0b";

  }

}


/* ============================================================================
   KPI STATISTICS
   ============================================================================ */

function refreshKpiStats() {

  if (!currentTopology) {
    return;
  }


  const nodeCountEl =
    document.getElementById(
      "stat-nodes-count"
    );


  if (nodeCountEl) {

    nodeCountEl.textContent =
      currentTopology.nodes.length;

  }


  const containedNodes =
    currentTopology.nodes.filter(
      (n) => n.state === "CONTAINED"
    );


  const containedCountEl =
    document.getElementById(
      "stat-contained-count"
    );


  if (containedCountEl) {

    containedCountEl.textContent =
      containedNodes.length;


    containedCountEl.style.color =
      containedNodes.length > 0
        ? "var(--status-isolate)"
        : "#ffffff";

  }

}


/* ============================================================================
   DROPDOWN POPULATION
   ============================================================================ */

function populateDropdowns(nodes) {

  const srcSelect =
    document.getElementById(
      "eval-source"
    );


  const dstSelect =
    document.getElementById(
      "eval-target"
    );


  if (!srcSelect || !dstSelect) {
    return;
  }


  const prevSrc =
    srcSelect.value;


  const prevDst =
    dstSelect.value;


  const optionsHtml =
    nodes
      .map(
        (n) => `
          <option value="${n.id}">
            [${String(
              n.domain || ""
            ).substring(0, 3)}]
            ${n.id} — ${n.name}
          </option>
        `
      )
      .join("");


  srcSelect.innerHTML =
    optionsHtml;


  dstSelect.innerHTML =
    optionsHtml;


  if (
    prevSrc &&
    nodes.some(
      (n) => n.id === prevSrc
    )
  ) {

    srcSelect.value =
      prevSrc;

  } else {

    srcSelect.value =
      "FAC-PC-01";

  }


  if (
    prevDst &&
    nodes.some(
      (n) => n.id === prevDst
    )
  ) {

    dstSelect.value =
      prevDst;

  } else {

    dstSelect.value =
      "APP-SRV-01";

  }

}


/* ============================================================================
   CUSTOM ZERO-TRUST EVALUATION
   ============================================================================ */

async function handleCustomEvaluate() {

  if (!currentTopology) {

    console.error(
      "Cannot evaluate: topology unavailable."
    );

    return;

  }


  const srcId =
    document.getElementById(
      "eval-source"
    )?.value;


  const dstId =
    document.getElementById(
      "eval-target"
    )?.value;


  const action =
    document.getElementById(
      "eval-action"
    )?.value;


  const srcNode =
    currentTopology.nodes.find(
      (n) => n.id === srcId
    );


  const dstNode =
    currentTopology.nodes.find(
      (n) => n.id === dstId
    );


  if (!srcNode || !dstNode) {

    console.error(
      "Invalid source or destination node."
    );

    return;

  }


  const payload = {

    source: {

      workload_id:
        srcNode.id,

      domain:
        srcNode.domain,

      zone:
        srcNode.zone,

      ip_address:
        srcNode.ip_address,

    },


    destination: {

      resource_id:
        dstNode.id,

      resource_type:
        dstNode.id.includes("DB")
          ? "DATABASE"
          : "SERVICE",

      domain:
        dstNode.domain,

      zone:
        dstNode.zone,

      sensitivity:
        dstNode.is_critical
          ? "RESTRICTED"
          : "INTERNAL",

      ip_address:
        dstNode.ip_address,

    },


    action:
      action,


    context: {

      source_zone:
        srcNode.zone,

      is_anomaly:
        false,

    },

  };


  try {

    const evalRes =
      await api.evaluateRequest(
        payload
      );


    lastEvaluatedFlow = {

      sourceId:
        srcNode.id,

      targetId:
        dstNode.id,

      action:
        action,

    };


    displayEvaluationResult(
      evalRes,
      srcNode,
      dstNode,
      action
    );


    highlightFlow(
      srcNode.id,
      dstNode.id,
      evalRes.decision
    );


    await refreshIncidentsAndLogs();

    refreshKpiStats();

  } catch (err) {

    console.error(
      "Evaluation failed:",
      err
    );


    const container =
      document.getElementById(
        "decision-panel"
      );


    if (container) {

      container.innerHTML = `

        <div
          class="decision-hero-card"
          style="
            border-color: var(--status-block);
            background: rgba(239, 68, 68, 0.06);
          "
        >

          <div
            style="
              font-size: 14px;
              font-weight: 800;
              color: var(--status-block);
            "
          >
            ⚠️ Evaluation Failed
          </div>

          <div
            style="
              margin-top: 6px;
              font-size: 11px;
              color: var(--text-secondary);
            "
          >
            The Decision Engine could not process
            this access request.
          </div>

        </div>

      `;

    }

  }

}


/* ============================================================================
   DECISION RESULT RENDERING
   ============================================================================ */

function displayEvaluationResult(
  evaluation,
  srcNode,
  dstNode,
  action
) {

  const container =
    document.getElementById(
      "decision-panel"
    );


  if (!container) {
    return;
  }


  const srcId =
    srcNode
      ? srcNode.id
      : "SOURCE";


  const srcName =
    srcNode
      ? srcNode.name
      : srcId;


  const srcZone =
    srcNode
      ? srcNode.zone
      : "";


  const srcIp =
    srcNode?.ip_address
      ? ` (${srcNode.ip_address})`
      : "";


  const dstId =
    dstNode
      ? dstNode.id
      : "DESTINATION";


  const dstName =
    dstNode
      ? dstNode.name
      : dstId;


  const dstZone =
    dstNode
      ? dstNode.zone
      : "";


  const dstIp =
    dstNode?.ip_address
      ? ` (${dstNode.ip_address})`
      : "";


  let barColor =
    "var(--status-allow)";


  if (
    evaluation.risk_score > 30
  ) {

    barColor =
      "#38bdf8";

  }


  if (
    evaluation.risk_score > 60
  ) {

    barColor =
      "var(--status-restrict)";

  }


  if (
    evaluation.risk_score > 80
  ) {

    barColor =
      "var(--status-block)";

  }


  let factorsHtml = "";


  if (
    evaluation.factors &&
    evaluation.factors.length > 0
  ) {

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

                  <td
                    style="
                      font-weight: 700;
                      color: #f8fafc;
                    "
                  >
                    ${f.name}
                  </td>

                  <td
                    style="
                      color: var(--text-secondary);
                    "
                  >
                    ${Math.round(
                      f.weight * 100
                    )}%
                  </td>

                  <td
                    style="
                      color: #38bdf8;
                      font-family: var(--font-mono);
                      font-weight: 700;
                    "
                  >
                    ${f.score}/100
                  </td>

                  <td
                    style="
                      color: #fbbf24;
                      font-family: var(--font-mono);
                      font-weight: 700;
                    "
                  >
                    ${f.weighted_score}
                  </td>

                  <td
                    style="
                      color: var(--text-secondary);
                      font-size: 10px;
                    "
                  >
                    ${f.description}
                  </td>

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

      <div
        style="
          background: rgba(0, 0, 0, 0.4);
          padding: 8px 14px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-subtle);
          margin-bottom: 14px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 11px;
          font-family: var(--font-mono);
        "
      >

        <div>

          <span
            style="
              color: var(--text-muted);
            "
          >
            EVALUATED ACCESS FLOW:
          </span>

          <span
            style="
              color: #38bdf8;
              font-weight: 700;
            "
          >
            ${srcName}
            [${srcId}]
            ${srcIp}
          </span>

          <span
            style="
              color: #fbbf24;
              margin: 0 6px;
            "
          >
            —[${action || "CONNECT"}]—▶
          </span>

          <span
            style="
              color: #ec4899;
              font-weight: 700;
            "
          >
            ${dstName}
            [${dstId}]
            ${dstIp}
          </span>

        </div>

        <div
          style="
            font-size: 10px;
            color: var(--text-muted);
          "
        >

          Zone:

          <span
            style="
              color: #7dd3fc;
            "
          >
            ${srcZone}
          </span>

          ➔

          <span
            style="
              color: #7dd3fc;
            "
          >
            ${dstZone}
          </span>

        </div>

      </div>


      <div class="decision-hero-header">

        <div>

          <div
            style="
              font-size: 10px;
              font-weight: 700;
              text-transform: uppercase;
              color: var(--text-muted);
              margin-bottom: 4px;
            "
          >
            Zero-Trust Decision Engine Verdict
          </div>

          <span
            class="decision-badge-large ${evaluation.decision}"
          >
            ${evaluation.decision}
          </span>

        </div>


        <div class="risk-gauge-block">

          <div
            style="
              text-align: right;
            "
          >

            <div
              style="
                font-size: 10px;
                font-weight: 700;
                color: var(--text-muted);
                text-transform: uppercase;
              "
            >
              Composite Risk
            </div>

            <div
              class="risk-number"
              style="
                color: ${barColor};
              "
            >
              ${evaluation.risk_score}/100

              <span
                style="
                  font-size: 11px;
                  font-weight: 700;
                "
              >
                (${evaluation.risk_level})
              </span>

            </div>

          </div>


          <div class="risk-progress-track">

            <div
              class="risk-progress-fill"
              style="
                width: ${evaluation.risk_score}%;
                background: ${barColor};
              "
            ></div>

          </div>

        </div>

      </div>


      <div class="decision-summary-text">

        <strong>
          Verdict Rationale:
        </strong>

        ${evaluation.explanation}

      </div>


      <div class="decision-meta-tags">

        <div>
          Enforcement Point:

          <span>
            ${evaluation.enforcement_layer}
          </span>
        </div>

        <div>
          Request ID:

          <span>
            ${evaluation.request_id}
          </span>
        </div>

        <div>
          Audit ID:

          <span>
            ${evaluation.audit_id}
          </span>
        </div>

      </div>


      <div
        style="
          font-size: 11px;
          font-weight: 800;
          text-transform: uppercase;
          color: var(--accent-cyan);
          margin: 16px 0 8px 0;
          letter-spacing: 0.5px;
        "
      >
        Multi-Factor Risk Scoring Decomposition
        (6 Architectural Factors)
      </div>


      ${factorsHtml}

    </div>

  `;

}


/* ============================================================================
   SIEM EVENT HELPERS
   ============================================================================ */

/**
 * Converts a SIEM event into a predictable structure.
 *
 * This makes the dashboard tolerant of slightly different
 * backend field names while still displaying the exact
 * Task 2 fields.
 */

function normalizeSIEMEvent(event) {

  const decision =
    String(
      event.decision ??
      event.action ??
      "UNKNOWN"
    ).toUpperCase();


  const riskScore =
    Number(
      event.risk_score ??
      event.riskScore ??
      0
    );


  const severity =
    String(
      event.severity ??
      event.risk_level ??
      event.level ??
      getSeverityFromRisk(riskScore)
    ).toUpperCase();


  const sourceDomain =
    event.source_domain ??
    event.sourceDomain ??
    event.domain ??
    event.source?.domain ??
    "UNKNOWN";


  const source =
    event.source ??
    event.source_workload ??
    event.workload_id ??
    event.source?.workload_id ??
    event.actor ??
    "UNKNOWN";


  const target =
    event.target ??
    event.destination ??
    event.resource_id ??
    event.destination?.resource_id ??
    event.target_resource ??
    "UNKNOWN";


  const timestamp =
    event.timestamp ??
    event.created_at ??
    event.createdAt ??
    event.time ??
    "UNKNOWN";


  const containmentStatus =
    event.containment_status ??
    event.containmentStatus ??
    event.containment_state ??
    event.containment?.status ??
    event.status ??
    (
      decision === "ISOLATE"
        ? "ACTIVE"
        : "NOT_REQUIRED"
    );


  return {

    timestamp,

    decision,

    riskScore,

    severity,

    sourceDomain,

    source,

    target,

    containmentStatus,

  };

}


/**
 * Fallback severity when backend does not explicitly
 * provide severity.
 */

function getSeverityFromRisk(riskScore) {

  if (riskScore >= 80) {
    return "CRITICAL";
  }


  if (riskScore >= 60) {
    return "HIGH";
  }


  if (riskScore >= 30) {
    return "MEDIUM";
  }


  return "LOW";

}


/**
 * Returns a CSS-friendly class based on the decision.
 */

function getDecisionClass(decision) {

  switch (
    String(decision).toUpperCase()
  ) {

    case "ALLOW":
      return "allow";

    case "BLOCK":
      return "block";

    case "ISOLATE":
      return "isolate";

    case "RESTORE":
      return "restore";

    default:
      return "unknown";

  }

}


/**
 * Returns a visual icon for the decision.
 */

function getDecisionIcon(decision) {

  switch (
    String(decision).toUpperCase()
  ) {

    case "ISOLATE":
      return "🔴";

    case "BLOCK":
      return "🟠";

    case "ALLOW":
      return "🟢";

    case "RESTORE":
      return "🔵";

    default:
      return "⚪";

  }

}


/* ============================================================================
   INCIDENTS + AUDIT LOGS + SIEM EVENTS
   ============================================================================ */

async function refreshIncidentsAndLogs() {

  try {

    /* ------------------------------------------------------------------------
       GET INCIDENTS
       ------------------------------------------------------------------------ */

    const incidents =
      await api.getIncidents();


    /* ------------------------------------------------------------------------
       GET AUDIT LOGS
       ------------------------------------------------------------------------ */

    const logs =
      await api.getAuditLogs();


    /* ------------------------------------------------------------------------
       INCIDENT FEED
       ------------------------------------------------------------------------ */

    const incContainer =
      document.getElementById(
        "incident-list"
      );


    if (incContainer) {

      if (
        !incidents ||
        incidents.length === 0
      ) {

        incContainer.innerHTML = `

          <div
            style="
              font-size: 11px;
              color: var(--text-muted);
              padding: 12px;
            "
          >
            No active containment incidents.
            All workloads nominal.
          </div>

        `;

      } else {

        incContainer.innerHTML =
          incidents
            .map(
              (inc) => {

                const active =
                  inc.status === "ACTIVE";


                const statusColor =
                  active
                    ? "var(--status-isolate)"
                    : "var(--status-allow)";


                return `

                  <div
                    class="feed-card"
                    style="
                      border-left: 3px solid ${statusColor};
                    "
                  >

                    <div>

                      <div
                        class="feed-header"
                        style="
                          color: ${statusColor};
                        "
                      >
                        [${inc.threat_id}]
                        ${inc.title}
                      </div>


                      <div class="feed-sub">

                        ${inc.workload_name}
                        (${inc.zone})

                        • Status:

                        <strong>
                          ${inc.status}
                        </strong>

                      </div>


                      ${
                        inc.containment_actions &&
                        inc.containment_actions.length > 0
                          ? `

                            <div
                              style="
                                font-size: 10px;
                                color: #7dd3fc;
                                margin-top: 3px;
                                font-family: var(--font-mono);
                              "
                            >
                              ${
                                inc.containment_actions[
                                  inc.containment_actions.length - 1
                                ]
                              }
                            </div>

                          `
                          : ""
                      }

                    </div>


                    <div>

                      ${
                        active

                          ? `

                            <button
                              class="btn-restore-pill"
                              data-id="${inc.workload_id}"
                            >
                              Lift Quarantine
                            </button>

                          `

                          : `

                            <span
                              style="
                                font-size: 10px;
                                color: var(--text-muted);
                                font-weight: 600;
                              "
                            >
                              Resolved
                            </span>

                          `
                      }

                    </div>

                  </div>

                `;

              }
            )
            .join("");


        /* --------------------------------------------------------------------
           RESTORE BUTTONS
           -------------------------------------------------------------------- */

        incContainer
          .querySelectorAll(
            ".btn-restore-pill"
          )
          .forEach((button) => {

            button.addEventListener(
              "click",
              async () => {

                const workloadId =
                  button.getAttribute(
                    "data-id"
                  );


                try {

                  await api.restoreWorkload(
                    workloadId
                  );


                  await refreshDashboard();

                } catch (err) {

                  console.error(
                    "Restore workload failed:",
                    err
                  );


                  alert(
                    "Unable to restore workload."
                  );

                }

              }
            );

          });

      }

    }


    /* ------------------------------------------------------------------------
       AUDIT LOG FEED
       ------------------------------------------------------------------------ */

    const auditContainer =
      document.getElementById(
        "audit-list"
      );


    if (auditContainer) {

      if (
        !logs ||
        logs.length === 0
      ) {

        auditContainer.innerHTML = `

          <div
            style="
              font-size: 11px;
              color: var(--text-muted);
              padding: 12px;
            "
          >
            No audit events recorded yet.
          </div>

        `;

      } else {

        auditContainer.innerHTML =
          logs
            .slice(0, 10)
            .map(
              (l) => `

                <div class="feed-card">

                  <div>

                    <div class="feed-header">
                      ${l.actor}
                      →
                      ${l.target}
                    </div>

                    <div class="feed-sub">
                      ${l.details}
                    </div>

                  </div>


                  <div
                    style="
                      text-align: right;
                    "
                  >

                    <span
                      class="badge-status ${String(
                        l.decision
                      ).toLowerCase()}"
                      style="
                        font-size: 9px;
                      "
                    >
                      ${l.decision}
                    </span>


                    <div
                      style="
                        font-size: 9px;
                        color: var(--text-muted);
                        font-family: var(--font-mono);
                        margin-top: 3px;
                      "
                    >
                      Risk:
                      ${l.risk_score}/100
                    </div>

                  </div>

                </div>

              `
            )
            .join("");

      }

    }


    /* =========================================================================
       LIVE SECURITY EVENTS — TASK 2
       ========================================================================= */

    const siemContainer =
      document.getElementById(
        "siem-event-list"
      );


    if (siemContainer) {

      let siemEvents = [];


      /* ----------------------------------------------------------------------
         Fetch events from:
         GET /api/v1/siem/events

         api.js is responsible for making the actual request.
         ---------------------------------------------------------------------- */

      try {

        if (
          typeof api.getSIEMEvents ===
          "function"
        ) {

          siemEvents =
            await api.getSIEMEvents();

        } else {

          console.error(
            "api.getSIEMEvents() is not available in api.js"
          );

        }

      } catch (siemError) {

        console.error(
          "SIEM event retrieval failed:",
          siemError
        );


        siemContainer.innerHTML = `

          <div
            style="
              font-size: 11px;
              color: var(--status-block);
              padding: 12px;
            "
          >
            Unable to retrieve SIEM security events.
          </div>

        `;


        return;

      }


      /* ----------------------------------------------------------------------
         EMPTY STATE
         ---------------------------------------------------------------------- */

      if (
        !Array.isArray(siemEvents) ||
        siemEvents.length === 0
      ) {

        siemContainer.innerHTML = `

          <div
            style="
              font-size: 11px;
              color: var(--text-muted);
              padding: 12px;
            "
          >
            Waiting for SIEM security events...
          </div>

        `;


        return;

      }


      /* ----------------------------------------------------------------------
         NORMALIZE EVENTS
         ---------------------------------------------------------------------- */

      const normalizedEvents =
        siemEvents
          .map(normalizeSIEMEvent)
          .slice(0, 10);


      /* ----------------------------------------------------------------------
         RENDER LIVE SECURITY EVENTS
         ---------------------------------------------------------------------- */

      siemContainer.innerHTML =
        normalizedEvents
          .map(
            (event) => {

              const decisionClass =
                getDecisionClass(
                  event.decision
                );


              const decisionIcon =
                getDecisionIcon(
                  event.decision
                );


              return `

                <div
                  class="feed-card siem-event-card"
                  style="
                    border-left: 3px solid
                      ${
                        decisionClass === "isolate"
                          ? "var(--status-isolate)"
                          : decisionClass === "block"
                            ? "var(--status-block)"
                            : decisionClass === "allow"
                              ? "var(--status-allow)"
                              : "var(--border-subtle)"
                      };
                  "
                >

                  <!-- LEFT SIDE -->

                  <div
                    style="
                      flex: 1;
                      min-width: 0;
                    "
                  >

                    <!-- Timestamp -->

                    <div
                      style="
                        font-size: 9px;
                        color: var(--text-muted);
                        font-family: var(--font-mono);
                        margin-bottom: 5px;
                      "
                    >
                      ${event.timestamp}
                    </div>


                    <!-- Decision -->

                    <div
                      style="
                        display: flex;
                        align-items: center;
                        gap: 7px;
                        margin-bottom: 5px;
                      "
                    >

                      <span
                        style="
                          font-size: 14px;
                        "
                      >
                        ${decisionIcon}
                      </span>


                      <span
                        class="badge-status ${decisionClass}"
                        style="
                          font-size: 10px;
                          font-weight: 800;
                        "
                      >
                        ${event.decision}
                      </span>

                    </div>


                    <!-- Source Domain -->

                    <div
                      style="
                        font-size: 10px;
                        color: #38bdf8;
                        font-weight: 700;
                        text-transform: uppercase;
                        margin-bottom: 4px;
                      "
                    >
                      ${event.sourceDomain}
                    </div>


                    <!-- Source → Target -->

                    <div
                      class="feed-sub"
                      style="
                        font-family: var(--font-mono);
                      "
                    >

                      ${event.source}

                      <span
                        style="
                          color: var(--text-muted);
                          margin: 0 5px;
                        "
                      >
                        →
                      </span>

                      ${event.target}

                    </div>

                  </div>


                  <!-- RIGHT SIDE -->

                  <div
                    style="
                      text-align: right;
                      min-width: 90px;
                    "
                  >

                    <!-- Risk -->

                    <div
                      style="
                        font-size: 10px;
                        color: var(--text-muted);
                        text-transform: uppercase;
                        font-weight: 700;
                      "
                    >
                      Risk
                    </div>


                    <div
                      style="
                        font-size: 18px;
                        font-family: var(--font-mono);
                        font-weight: 800;
                        color:
                          ${
                            event.riskScore >= 80
                              ? "var(--status-block)"
                              : event.riskScore >= 60
                                ? "var(--status-restrict)"
                                : "var(--status-allow)"
                          };
                      "
                    >
                      ${event.riskScore}
                    </div>


                    <!-- Severity -->

                    <span
                      class="badge-status ${event.severity.toLowerCase()}"
                      style="
                        font-size: 9px;
                      "
                    >
                      ${event.severity}
                    </span>


                    <!-- Containment -->

                    <div
                      style="
                        margin-top: 5px;
                        font-size: 9px;
                        color: var(--text-muted);
                      "
                    >

                      Containment:

                      <strong
                        style="
                          color:
                            ${
                              String(
                                event.containmentStatus
                              ).toUpperCase() === "ACTIVE"
                                ? "var(--status-isolate)"
                                : "var(--text-secondary)"
                            };
                        "
                      >
                        ${event.containmentStatus}
                      </strong>

                    </div>

                  </div>

                </div>

              `;

            }
          )
          .join("");

    }


  } catch (err) {

    console.error(
      "Incident / audit / SIEM refresh failed:",
      err
    );

  }

}


/* ============================================================================
   APPLICATION START
   ============================================================================ */

document.addEventListener(
  "DOMContentLoaded",
  init
);