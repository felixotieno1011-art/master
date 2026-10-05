// ============================================
// NETKIT — static/app.js
// Dashboard logic: cards, forms, run, render.
// ============================================

const forms = {
  ping:         () => [{ name: "target", label: "Host (e.g. 8.8.8.8)", placeholder: "8.8.8.8" }],
  dns:          () => [{ name: "domain", label: "Domain", placeholder: "google.com" }],
  portscan:     () => [{ name: "target", label: "Target host or IP", placeholder: "192.168.1.1" }],
  traceroute:   () => [{ name: "target", label: "Target", placeholder: "8.8.8.8" }],
  firewall:     () => [{ name: "target", label: "Target", placeholder: "192.168.1.1" }],
  loadbalancer: () => [
    { name: "count", label: "Number of requests", placeholder: "12", value: "12" },
    { name: "algorithm", label: "Algorithm", type: "select",
      options: ["roundrobin", "leastconn", "iphash"] }
  ],
  ids:          () => []
};

let currentTool = null;


async function loadTools() {
  const res = await fetch("/api/tools");
  const tools = await res.json();
  const grid = document.getElementById("toolGrid");
  grid.innerHTML = "";
  for (const t of tools) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h3>${t.label}</h3><p>${t.desc}</p>`;
    card.onclick = () => openTool(t);
    grid.appendChild(card);
  }
}


function openTool(tool) {
  currentTool = tool.id;
  document.getElementById("runnerTitle").textContent = tool.label;
  document.getElementById("runner").hidden = false;

  const form = document.getElementById("formArea");
  form.innerHTML = "";

  const fields = forms[tool.id] ? forms[tool.id]() : [];
  for (const f of fields) {
    const label = document.createElement("label");
    label.textContent = f.label;
    form.appendChild(label);

    if (f.type === "select") {
      const sel = document.createElement("select");
      sel.name = f.name;
      for (const opt of f.options) {
        const o = document.createElement("option");
        o.value = opt; o.textContent = opt;
        sel.appendChild(o);
      }
      form.appendChild(sel);
    } else {
      const input = document.createElement("input");
      input.name = f.name;
      input.placeholder = f.placeholder || "";
      input.value = f.value || "";
      form.appendChild(input);
    }
  }

  const row = document.createElement("div");
  row.className = "run-row";
  const btn = document.createElement("button");
  btn.className = "btn";
  btn.textContent = "▶ Run";
  btn.onclick = () => runTool(btn);
  row.appendChild(btn);
  form.appendChild(row);

  const output = document.getElementById("outputArea");
  output.classList.remove("visible");
  output.textContent = "";

  document.getElementById("runner").scrollIntoView({ behavior: "smooth", block: "start" });
}


async function runTool(btn) {
  if (!currentTool) return;
  btn.disabled = true;
  btn.textContent = "⏳ Running...";

  const payload = {};
  document.querySelectorAll("#formArea input, #formArea select").forEach(el => {
    payload[el.name] = el.value;
  });

  const output = document.getElementById("outputArea");
  output.classList.add("visible");
  output.textContent = "Running...";

  try {
    const res = await fetch(`/api/run/${currentTool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    output.innerHTML = renderResult(currentTool, data);
  } catch (e) {
    output.innerHTML = `<span class="fail">❌ ${e}</span>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run";
  }
}


function esc(s) {
  return String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
}


function renderResult(tool, r) {
  if (!r || r.ok === false) {
    return `<span class="fail">❌ ${esc(r?.error || "failed")}</span>`;
  }

  if (tool === "ping") {
    let out = `<span class="ok">✅ ${esc(r.target)} is reachable</span>`;
    if (r.avg_ms != null) {
      out += `\n   Min: ${r.min_ms} ms\n   Avg: ${r.avg_ms} ms\n   Max: ${r.max_ms} ms`;
    }
    return out;
  }

  if (tool === "dns") {
    return `<span class="ok">✅ ${esc(r.domain)} → ${esc(r.ip)}</span>`;
  }

  if (tool === "portscan") {
    let out = `<span class="muted">Target: ${esc(r.target)} (${esc(r.ip)})</span>\n\n`;
    for (const port of r.scanned) {
      out += r.open.includes(port)
        ? `<span class="ok">   ✅ Port ${port} OPEN</span>\n`
        : `<span class="fail">   ❌ Port ${port} closed</span>\n`;
    }
    out += `\n<span class="ok">Found ${r.open.length} open port(s): [${r.open.join(", ")}]</span>`;
    return out;
  }

  if (tool === "traceroute") {
    return `<pre style="margin:0">${esc(r.raw || "")}</pre>`;
  }

  if (tool === "firewall") {
    let out = `<span class="muted">Target: ${esc(r.target)} (${esc(r.ip)})</span>\n\n`;
    for (const a of r.allowed) {
      out += `<span class="ok">   ✅ ${a.port} (${a.name}) ALLOWED</span>\n`;
    }
    for (const b of r.blocked) {
      out += `<span class="fail">   ❌ ${b.port} (${b.name}) BLOCKED</span>\n`;
    }
    return out;
  }

  if (tool === "loadbalancer") {
    let out = `<span class="muted">Algorithm: ${esc(r.algorithm)}   Requests: ${r.total}</span>\n\n`;
    for (const [server, count] of Object.entries(r.counts)) {
      const bar = "█".repeat(count);
      out += `   ${server}: ${String(count).padStart(3, " ")}  <span class="ok">${bar}</span>\n`;
    }
    return out;
  }

  if (tool === "ids") {
    let out = "";
    for (const line of r.traffic) out += `   ${esc(line)}\n`;
    out += "\n";
    if (r.clean) {
      out += `<span class="ok">✅ No threats detected</span>`;
    } else {
      for (const a of r.alerts) {
        out += `<span class="fail">🚨 ALERT: Port scan from ${esc(a.ip)}</span>\n`;
        out += `   Ports hit: [${a.ports.join(", ")}]\n`;
      }
    }
    return out;
  }

  return `<pre style="margin:0">${esc(JSON.stringify(r, null, 2))}</pre>`;
}


document.addEventListener("DOMContentLoaded", () => {
  loadTools();
  document.getElementById("closeRunner").onclick = () => {
    document.getElementById("runner").hidden = true;
    currentTool = null;
  };
});
