/**
 * AegisMesh — API Client Module
 * Communicates with FastAPI backend (/api/v1/*)
 */

const API_BASE = "/api/v1";

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return await res.json();
  },

  async getTopology() {
    const res = await fetch(`${API_BASE}/topology`);
    return await res.json();
  },

  async evaluateRequest(payload) {
    const res = await fetch(`${API_BASE}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return await res.json();
  },

  async getScenarios() {
    const res = await fetch(`${API_BASE}/scenarios`);
    return await res.json();
  },

  async simulateScenario(scenarioId) {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
    return await res.json();
  },

  async isolateWorkload(workloadId, reason) {
    const res = await fetch(`${API_BASE}/isolate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workload_id: workloadId, reason: reason }),
    });
    return await res.json();
  },

  async restoreWorkload(workloadId) {
    const res = await fetch(`${API_BASE}/restore?workload_id=${encodeURIComponent(workloadId)}`, {
      method: "POST",
    });
    return await res.json();
  },

  async getIncidents() {
    const res = await fetch(`${API_BASE}/incidents`);
    return await res.json();
  },

  async getAuditLogs() {
    const res = await fetch(`${API_BASE}/audit`);
    return await res.json();
  },

  async getPolicies() {
    const res = await fetch(`${API_BASE}/policies`);
    return await res.json();
  },

  async getK8sStatus() {
    const res = await fetch(`${API_BASE}/kubernetes/status`);
    return await res.json();
  }
};

