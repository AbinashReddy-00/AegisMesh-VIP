/**
 * AegisMesh — Topology Renderer Module
 * Interactive 3-Domain Visualization (Private DC, AWS, Kubernetes)
 */

export function renderTopology(topologyData, onNodeClick, activeFilter = "ALL") {
  const container = document.getElementById("topology-canvas");
  if (!container) return;

  const domains = {
    PRIVATE_DC: {
      key: "PRIVATE_DC",
      title: "🏢 Private Datacenter",
      sub: "Packet Tracer Architecture Model (VLANs 10–60)",
      nodes: [],
    },
    AWS_CLOUD: {
      key: "AWS_CLOUD",
      title: "☁️ AWS Public Cloud",
      sub: "Simulated Architecture Data (VPCs A–D)",
      nodes: [],
    },
    KUBERNETES: {
      key: "KUBERNETES",
      title: "☸️ Kubernetes Container Platform",
      sub: "Simulated Architecture Data (Namespaces)",
      nodes: [],
    },
  };

  // Group nodes by domain
  topologyData.nodes.forEach((node) => {
    if (domains[node.domain]) {
      domains[node.domain].nodes.push(node);
    }
  });

  let html = "";
  for (const [key, domain] of Object.entries(domains)) {
    if (activeFilter !== "ALL" && activeFilter !== key) {
      continue;
    }

    html += `
      <div class="domain-section" id="domain-${key}">
        <div class="domain-section-header">
          <div class="domain-name">
            <span>${domain.title}</span>
          </div>
          <div class="domain-badge-source">${domain.sub}</div>
        </div>
        <div class="node-grid">
          ${domain.nodes
            .map(
              (n) => `
            <div class="node-card ${n.state === "CONTAINED" ? "contained" : ""}" 
                 id="node-${n.id}" 
                 data-id="${n.id}"
                 data-domain="${n.domain}"
                 data-zone="${n.zone}"
                 title="Click to select '${n.id}' as source/target in evaluator">
              <div class="node-name">${n.name}</div>
              <div class="node-zone">${n.vlan_or_vpc_or_ns}</div>
              <div class="node-ip">IP: ${n.ip_address || "N/A"}</div>
              <div class="node-footer">
                <span class="badge-status ${n.state === "CONTAINED" ? "contained" : "normal"}">
                  ${n.state}
                </span>
                <span class="trust-meter">Trust: ${n.trust_score}%</span>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    `;
  }

  container.innerHTML = html;

  // Bind click listeners
  container.querySelectorAll(".node-card").forEach((el) => {
    el.addEventListener("click", () => {
      const nodeId = el.getAttribute("data-id");
      const node = topologyData.nodes.find((n) => n.id === nodeId);
      if (onNodeClick && node) onNodeClick(node);
    });
  });
}

export function highlightFlow(sourceId, targetId, decision) {
  // Reset previous highlights
  document.querySelectorAll(".node-card").forEach((el) => {
    el.style.boxShadow = "";
    el.style.transform = "";
  });

  const srcEl = document.getElementById(`node-${sourceId}`);
  const dstEl = document.getElementById(`node-${targetId}`);

  let glowColor = "rgba(16, 185, 129, 0.85)";
  if (decision === "BLOCK") glowColor = "rgba(239, 68, 68, 0.9)";
  if (decision === "ISOLATE") glowColor = "rgba(236, 72, 153, 0.95)";

  if (srcEl) {
    srcEl.style.boxShadow = `0 0 18px ${glowColor}`;
    srcEl.style.transform = "scale(1.04)";
  }
  if (dstEl) {
    dstEl.style.boxShadow = `0 0 18px ${glowColor}`;
    dstEl.style.transform = "scale(1.04)";
  }
}
