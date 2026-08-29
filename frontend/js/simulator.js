/**
 * AegisMesh — Attack Simulation Module
 * Traces canned scenarios and animates packet traversal & decision pipeline
 */

import { api } from "./api.js";
import { highlightFlow } from "./topology.js";

export async function runSimulation(scenarioId, onComplete) {
  const terminal = document.getElementById("packet-terminal");
  if (terminal) {
    terminal.innerHTML = `<div class="terminal-line" style="color: #fbbf24;">Initiating simulation scenario [${scenarioId}]...</div>`;
  }

  try {
    const result = await api.simulateScenario(scenarioId);

    // Highlight nodes in topology
    highlightFlow(result.source.workload_id, result.destination.resource_id, result.evaluation.decision);

    // Animate packet trace in terminal
    if (terminal && result.packet_trace) {
      terminal.innerHTML = "";
      result.packet_trace.forEach((line, idx) => {
        setTimeout(() => {
          const div = document.createElement("div");
          div.className = "terminal-line";
          if (line.includes("[BLOCKED]") || line.includes("drops packet")) {
            div.style.color = "#ef4444";
          } else if (line.includes("[REPLY ALLOWED]")) {
            div.style.color = "#10b981";
          } else if (line.includes("[ISOLATED]")) {
            div.style.color = "#ec4899";
          }
          div.textContent = line;
          terminal.appendChild(div);
          terminal.scrollTop = terminal.scrollHeight;
        }, idx * 180);
      });
    }

    if (onComplete) {
      onComplete(result);
    }
  } catch (err) {
    console.error("Simulation error:", err);
    if (terminal) {
      terminal.innerHTML += `<div class="terminal-line" style="color: #ef4444;">Simulation error: ${err.message}</div>`;
    }
  }
}
