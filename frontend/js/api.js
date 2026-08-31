// /**
//  * AegisMesh — API Client Module
//  * Communicates with FastAPI backend (/api/v1/*)
//  */

// const API_BASE = "/api/v1";

// export const api = {
//   async getHealth() {
//     const res = await fetch(`${API_BASE}/health`);
//     return await res.json();
//   },

//   async getTopology() {
//     const res = await fetch(`${API_BASE}/topology`);
//     return await res.json();
//   },

//   async evaluateRequest(payload) {
//     const res = await fetch(`${API_BASE}/evaluate`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify(payload),
//     });
//     return await res.json();
//   },

//   async getScenarios() {
//     const res = await fetch(`${API_BASE}/scenarios`);
//     return await res.json();
//   },

//   async simulateScenario(scenarioId) {
//     const res = await fetch(`${API_BASE}/simulate`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ scenario_id: scenarioId }),
//     });
//     return await res.json();
//   },

//   async isolateWorkload(workloadId, reason) {
//     const res = await fetch(`${API_BASE}/isolate`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ workload_id: workloadId, reason: reason }),
//     });
//     return await res.json();
//   },

//   async restoreWorkload(workloadId) {
//     const res = await fetch(`${API_BASE}/restore?workload_id=${encodeURIComponent(workloadId)}`, {
//       method: "POST",
//     });
//     return await res.json();
//   },

//   async getIncidents() {
//     const res = await fetch(`${API_BASE}/incidents`);
//     return await res.json();
//   },

//   async getAuditLogs() {
//     const res = await fetch(`${API_BASE}/audit`);
//     return await res.json();
//   },
//   async getSIEMEvents() {
//   const res = await fetch(`${API_BASE}/siem/events`);
//   return await res.json();
//  }, 

//   async getPolicies() {
//     const res = await fetch(`${API_BASE}/policies`);
//     return await res.json();
//   },

//   async getK8sStatus() {
//     const res = await fetch(`${API_BASE}/kubernetes/status`);
//     return await res.json();
//   }
// };
/**
 * AegisMesh — API Client Module
 * Communicates with FastAPI backend (/api/v1/*)
 */

const API_BASE = "/api/v1";

export const api = {

  /* --------------------------------------------------------------------------
     HEALTH
     -------------------------------------------------------------------------- */

  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);

    if (!res.ok) {
      throw new Error(`Health request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     TOPOLOGY
     -------------------------------------------------------------------------- */

  async getTopology() {
    const res = await fetch(`${API_BASE}/topology`);

    if (!res.ok) {
      throw new Error(`Topology request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     ZERO-TRUST EVALUATION
     -------------------------------------------------------------------------- */

  async evaluateRequest(payload) {
    const res = await fetch(`${API_BASE}/evaluate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Evaluation request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     SCENARIOS
     -------------------------------------------------------------------------- */

  async getScenarios() {
    const res = await fetch(`${API_BASE}/scenarios`);

    if (!res.ok) {
      throw new Error(`Scenarios request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     SCENARIO SIMULATION
     -------------------------------------------------------------------------- */

  async simulateScenario(scenarioId) {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        scenario_id: scenarioId,
      }),
    });

    if (!res.ok) {
      throw new Error(`Simulation request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     WORKLOAD ISOLATION
     -------------------------------------------------------------------------- */

  async isolateWorkload(workloadId, reason) {
    const res = await fetch(`${API_BASE}/isolate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workload_id: workloadId,
        reason: reason,
      }),
    });

    if (!res.ok) {
      throw new Error(`Isolation request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     WORKLOAD RESTORE
     -------------------------------------------------------------------------- */

  async restoreWorkload(workloadId) {
    const res = await fetch(
      `${API_BASE}/restore?workload_id=${encodeURIComponent(workloadId)}`,
      {
        method: "POST",
      }
    );

    if (!res.ok) {
      throw new Error(`Restore request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     INCIDENTS
     -------------------------------------------------------------------------- */

  async getIncidents() {
    const res = await fetch(`${API_BASE}/incidents`);

    if (!res.ok) {
      throw new Error(`Incidents request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     AUDIT LOGS
     -------------------------------------------------------------------------- */

  async getAuditLogs() {
    const res = await fetch(`${API_BASE}/audit`);

    if (!res.ok) {
      throw new Error(`Audit logs request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     SIEM SECURITY EVENTS
     --------------------------------------------------------------------------

     Backend response:

     {
       "value": [
         {
           "event_id": "...",
           "timestamp": "...",
           "source": "AegisMesh",
           "event_type": "containment_action",
           "source_domain": "KUBERNETES",
           "source_workload": "k8s-edu-api",
           "target": "k8s-edu-api",
           "risk_score": 90,
           "decision": "ISOLATE",
           "severity": "CRITICAL",
           "containment_status": "ACTIVE",
           "threat_id": "I-01"
         }
       ],
       "Count": 1
     }

     Return only the event array to the dashboard.
     -------------------------------------------------------------------------- */

  async getSIEMEvents() {
  const res = await fetch(`${API_BASE}/siem/events`);

  if (!res.ok) {
    throw new Error(`SIEM events request failed: ${res.status}`);
  }

  const data = await res.json();

  if (!Array.isArray(data)) {
    throw new Error("Invalid SIEM events response format");
  }

  return data;
},


  /* --------------------------------------------------------------------------
     POLICIES
     -------------------------------------------------------------------------- */

  async getPolicies() {
    const res = await fetch(`${API_BASE}/policies`);

    if (!res.ok) {
      throw new Error(`Policies request failed: ${res.status}`);
    }

    return await res.json();
  },


  /* --------------------------------------------------------------------------
     KUBERNETES STATUS
     -------------------------------------------------------------------------- */

  async getK8sStatus() {
    const res = await fetch(`${API_BASE}/kubernetes/status`);

    if (!res.ok) {
      throw new Error(
        `Kubernetes status request failed: ${res.status}`
      );
    }

    return await res.json();
  },

};