(() => {
  "use strict";

  let activeJobId = 0;
  let currentReceipt = null;

  const statusSymbol = document.getElementById("status-symbol");
  const statusText = document.getElementById("status-text");
  const headerSourceSha = document.getElementById("header-source-sha");

  const scenarioSelect = document.getElementById("scenario-select");
  const seedInput = document.getElementById("seed-input");
  const casesInput = document.getElementById("cases-input");
  const sizeInput = document.getElementById("size-input");
  const replicatesInput = document.getElementById("replicates-input");

  const runDemoBtn = document.getElementById("run-demo-btn");
  const runStudyBtn = document.getElementById("run-study-btn");
  const datasetFileInput = document.getElementById("dataset-file-input");
  const analyzeImportBtn = document.getElementById("analyze-import-btn");
  const exportReceiptBtn = document.getElementById("export-receipt-btn");
  const receiptFileInput = document.getElementById("receipt-file-input");
  const verifyReceiptBtn = document.getElementById("verify-receipt-btn");
  const reloadParityBtn = document.getElementById("reload-parity-btn");

  const errorAlert = document.getElementById("error-alert");
  const errorMessage = document.getElementById("error-message");
  const verifyBanner = document.getElementById("verify-banner");
  const verifyBadge = document.getElementById("verify-badge");
  const verifyMessage = document.getElementById("verify-message");

  const activeRunBadge = document.getElementById("active-run-badge");
  const emptyState = document.getElementById("empty-state");
  const singleResultView = document.getElementById("single-result-view");
  const studyResultView = document.getElementById("study-result-view");

  function setStatus(symbol, message) {
    statusSymbol.textContent = symbol;
    statusText.textContent = message;
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorAlert.hidden = false;
  }

  function hideError() {
    errorMessage.textContent = "";
    errorAlert.hidden = true;
  }

  function showVerifyBanner(valid, reason) {
    verifyBanner.hidden = false;
    verifyBanner.className = "alert-box verify-alert " + (valid ? "valid" : "invalid");
    verifyBadge.textContent = valid ? "[VALID RECEIPT]" : "[INVALID RECEIPT]";
    verifyMessage.textContent = reason;
  }

  function hideVerifyBanner() {
    verifyBanner.hidden = true;
    verifyMessage.textContent = "";
  }

  function clearExperimentDisplay(badgeText = "[NO ACTIVE RESULT]") {
    currentReceipt = null;
    exportReceiptBtn.disabled = true;
    activeRunBadge.textContent = badgeText;
    emptyState.hidden = false;
    singleResultView.hidden = true;
    studyResultView.hidden = true;
  }

  function fmtPct(rate) {
    return (Number(rate) * 100).toFixed(2) + "% (" + Number(rate).toFixed(4) + ")";
  }

  function fmtSignedPct(diff) {
    const num = Number(diff);
    const sign = num > 0 ? "+" : "";
    return sign + (num * 100).toFixed(2) + " pp (" + sign + num.toFixed(4) + ")";
  }

  function makeCell(tag, text, dataLabel = null) {
    const el = document.createElement(tag);
    el.textContent = text;
    if (dataLabel) {
      el.setAttribute("data-label", dataLabel);
    }
    return el;
  }

  function renderSingleAnalysis(receipt, sourceTag) {
    currentReceipt = receipt;
    exportReceiptBtn.disabled = false;
    const res = receipt.result;

    activeRunBadge.textContent =
      "[" + sourceTag + " // " + res.dataset + " // payload:" + receipt.payload_sha256.slice(0, 12) + "]";
    emptyState.hidden = true;
    studyResultView.hidden = true;
    singleResultView.hidden = false;

    const costs = res.costs;
    const strip = document.getElementById("cost-summary-strip");
    strip.textContent =
      "Dataset: " + res.dataset +
      " | Components: " + res.components.length +
      " | Panel Size k=" + res.panel_size +
      " | Candidate Panels: " + costs.candidate_panels +
      " | Calibration Rows: " + res.n_calibration +
      " (" + costs.calibration_component_calls + " comp calls)" +
      " | Test Rows: " + res.n_test +
      " (" + costs.test_deployment_calls_per_policy + " deploy calls/policy)" +
      " | Search Evaluations: " + costs.search_panel_row_evaluations;

    // Render comparison chart
    const chart = document.getElementById("comparison-chart");
    chart.replaceChildren();
    for (const pol of res.policies) {
      const card = document.createElement("div");
      card.className = "chart-card";

      const title = document.createElement("div");
      title.className = "chart-card-title";
      title.textContent = pol.id.toUpperCase() + " — [" + pol.panel.join(", ") + "]";
      card.appendChild(title);

      const rows = [
        { label: "Test Pooled Err", val: pol.test.error, cls: "pooled" },
        { label: "Test Worst-Cond Err", val: pol.test.worst_group_error, cls: "worst" },
      ];
      for (const item of rows) {
        const bRow = document.createElement("div");
        bRow.className = "bar-row";
        const lbl = document.createElement("span");
        lbl.textContent = item.label + ": " + fmtPct(item.val);
        const track = document.createElement("div");
        track.className = "bar-track";
        const fill = document.createElement("div");
        fill.className = "bar-fill " + item.cls;
        fill.style.width = Math.min(100, Math.max(1, item.val * 100)).toFixed(1) + "%";
        track.appendChild(fill);
        bRow.appendChild(lbl);
        bRow.appendChild(track);
        card.appendChild(bRow);
      }
      chart.appendChild(card);
    }

    // Render policy table
    const policyTbody = document.getElementById("policy-tbody");
    policyTbody.replaceChildren();
    for (const pol of res.policies) {
      const tr = document.createElement("tr");
      const th = makeCell("th", pol.id + " — " + pol.label);
      th.setAttribute("scope", "row");
      tr.appendChild(th);
      tr.appendChild(makeCell("td", pol.panel.join(", "), "Selected Panel"));
      tr.appendChild(makeCell("td", fmtPct(pol.calibration.error), "Cal Pooled Err"));
      tr.appendChild(makeCell("td", fmtPct(pol.calibration.worst_group_error), "Cal Worst-Cond Err"));
      tr.appendChild(makeCell("td", fmtPct(pol.test.error), "Test Pooled Err"));
      tr.appendChild(makeCell("td", fmtPct(pol.test.worst_group_error), "Test Worst-Cond Err"));
      tr.appendChild(makeCell("td", fmtPct(pol.test.unanimous_wrong_rate), "Test Unanimous Wrong"));
      policyTbody.appendChild(tr);
    }

    // Render co-failure matrix
    const matHead = document.getElementById("cofailure-matrix-head");
    const matBody = document.getElementById("cofailure-matrix-body");
    matHead.replaceChildren();
    matBody.replaceChildren();

    const headRow = document.createElement("tr");
    headRow.appendChild(makeCell("th", "Comp"));
    for (const c of res.components) {
      const th = makeCell("th", c.id);
      th.setAttribute("scope", "col");
      headRow.appendChild(th);
    }
    matHead.appendChild(headRow);

    res.cofailure.matrix.forEach((rowVals, rIdx) => {
      const tr = document.createElement("tr");
      const rowTh = makeCell("th", res.components[rIdx].id + " (" + res.components[rIdx].family + ")");
      rowTh.setAttribute("scope", "row");
      tr.appendChild(rowTh);
      rowVals.forEach((val) => {
        tr.appendChild(makeCell("td", Number(val).toFixed(3)));
      });
      matBody.appendChild(tr);
    });

    // Render top failure signatures
    const sigBody = document.getElementById("signatures-tbody");
    sigBody.replaceChildren();
    const topSigs = res.cofailure.signatures.slice(0, 12);
    for (const sig of topSigs) {
      const tr = document.createElement("tr");
      const th = makeCell("th", "{" + sig.members.join(", ") + "}");
      th.setAttribute("scope", "row");
      tr.appendChild(th);
      tr.appendChild(makeCell("td", String(sig.members.length), "Order"));
      tr.appendChild(makeCell("td", String(sig.count), "Count"));
      tr.appendChild(makeCell("td", fmtPct(sig.rate), "Cal Rate"));
      sigBody.appendChild(tr);
    }

    // Render witnesses for accuracy and joint
    const witBody = document.getElementById("witnesses-tbody");
    witBody.replaceChildren();
    for (const pol of res.policies) {
      if (pol.id !== "accuracy" && pol.id !== "joint" && pol.id !== "pairwise") continue;
      for (const w of pol.witnesses.slice(0, 4)) {
        const tr = document.createElement("tr");
        const th = makeCell("th", pol.id);
        th.setAttribute("scope", "row");
        tr.appendChild(th);
        tr.appendChild(makeCell("td", w.id, "Case ID"));
        tr.appendChild(makeCell("td", w.condition, "Condition"));
        tr.appendChild(makeCell("td", String(w.truth), "Truth"));
        tr.appendChild(makeCell("td", String(w.vote), "Panel Vote"));
        tr.appendChild(makeCell("td", w.wrong_components.join(", "), "Wrong Panel Members"));
        witBody.appendChild(tr);
      }
    }
  }

  function renderStudyAnalysis(receipt, sourceTag) {
    currentReceipt = receipt;
    exportReceiptBtn.disabled = false;
    const res = receipt.result;

    activeRunBadge.textContent =
      "[" + sourceTag + " // study:" + res.scenario + " // n=" + res.n_seeds + " // payload:" + receipt.payload_sha256.slice(0, 12) + "]";
    emptyState.hidden = true;
    singleResultView.hidden = true;
    studyResultView.hidden = false;

    const strip = document.getElementById("study-summary-strip");
    strip.textContent =
      "Scenario: " + res.scenario +
      " | Replicate Seeds: " + res.n_seeds +
      " (" + res.seeds[0] + ".." + res.seeds[res.seeds.length - 1] + ")" +
      " | Cases/Condition: " + res.cases_per_condition +
      " | Panel Size k=" + res.panel_size;

    const pairedBody = document.getElementById("study-paired-tbody");
    pairedBody.replaceChildren();
    for (const compId of ["accuracy", "pairwise", "pooled"]) {
      const row = res.aggregate.paired_vs_joint[compId];
      const tr = document.createElement("tr");
      const th = makeCell("th", compId + " — " + row.label);
      th.setAttribute("scope", "row");
      tr.appendChild(th);
      tr.appendChild(makeCell("td", fmtSignedPct(row.mean_diff_worst_group_error), "Mean Δ Worst-Cond Err"));
      tr.appendChild(
        makeCell(
          "td",
          "[" + fmtSignedPct(row.ci95_worst_group_error[0]) + ", " + fmtSignedPct(row.ci95_worst_group_error[1]) + "]",
          "95% Bootstrap Interval"
        )
      );
      tr.appendChild(makeCell("td", fmtSignedPct(row.mean_diff_pooled_error), "Mean Δ Pooled Err"));
      tr.appendChild(
        makeCell(
          "td",
          row.joint_wins + " W / " + row.ties + " T / " + row.comparator_wins + " L",
          "Win / Tie / Loss"
        )
      );
      pairedBody.appendChild(tr);
    }

    const aggBody = document.getElementById("study-agg-tbody");
    aggBody.replaceChildren();
    for (const pid of ["accuracy", "pairwise", "pooled", "joint"]) {
      const p = res.aggregate.policies[pid];
      const tr = document.createElement("tr");
      const th = makeCell("th", p.id + " — " + p.label);
      th.setAttribute("scope", "row");
      tr.appendChild(th);
      tr.appendChild(makeCell("td", fmtPct(p.mean_calibration_error), "Mean Cal Pooled"));
      tr.appendChild(makeCell("td", fmtPct(p.mean_calibration_worst_group_error), "Mean Cal Worst-Cond"));
      tr.appendChild(makeCell("td", fmtPct(p.mean_test_error), "Mean Test Pooled"));
      tr.appendChild(makeCell("td", fmtPct(p.mean_test_worst_group_error), "Mean Test Worst-Cond"));
      tr.appendChild(makeCell("td", fmtPct(p.mean_test_unanimous_wrong_rate), "Mean Test Unanimous Wrong"));
      aggBody.appendChild(tr);
    }
  }

  function renderParityDemo(data) {
    const container = document.getElementById("parity-content");
    container.replaceChildren();
    const specs = [
      {
        key: "even",
        title: "Even-Parity Failure Distribution (Majority Error = 3/4 = 75.00%)",
        data: data.even,
      },
      {
        key: "odd",
        title: "Odd-Parity Failure Distribution (Majority Error = 1/4 = 25.00%)",
        data: data.odd,
      },
    ];
    for (const item of specs) {
      const box = document.createElement("div");
      box.className = "parity-box";
      const h3 = document.createElement("h3");
      h3.textContent = item.title;
      box.appendChild(h3);

      const meta = document.createElement("p");
      meta.className = "helper-text";
      meta.textContent =
        "Marginals: [" + item.data.marginals.join(", ") + "]" +
        " | Off-diagonal Pairwise Co-Failure: 0.25" +
        " | Majority Error (≥2 wrong): " + fmtPct(item.data.majority_error);
      box.appendChild(meta);

      const list = document.createElement("ul");
      for (const pat of item.data.patterns) {
        const li = document.createElement("li");
        const wrongCount = pat[0] + pat[1] + pat[2];
        li.textContent =
          "Failure pattern [" + pat.join(", ") + "] — " +
          wrongCount + "/3 wrong → " +
          (wrongCount >= 2 ? "MAJORITY WRONG" : "MAJORITY CORRECT");
        list.appendChild(li);
      }
      box.appendChild(list);
      container.appendChild(box);
    }
  }

  async function fetchJson(url, options = {}) {
    const resp = await fetch(url, options);
    const body = await resp.json().catch(() => ({ error: "Non-JSON response from server." }));
    if (!resp.ok) {
      throw new Error(body.error || ("HTTP " + resp.status));
    }
    return body;
  }

  async function runSingleDemo() {
    const jobId = ++activeJobId;
    hideError();
    hideVerifyBanner();
    clearExperimentDisplay("[RUNNING SINGLE-SEED...]");
    setStatus("[RUNNING]", "Computing single-seed joint-failure analysis...");

    const params = new URLSearchParams({
      seed: seedInput.value,
      cases: casesInput.value,
      scenario: scenarioSelect.value,
      size: sizeInput.value,
    });
    try {
      const rec = await fetchJson("/api/demo?" + params.toString());
      if (jobId !== activeJobId) return;
      renderSingleAnalysis(rec, "DEMO");
      setStatus("[COMPLETE]", "Single-seed analysis complete (" + rec.result.dataset + ")");
    } catch (err) {
      if (jobId !== activeJobId) return;
      clearExperimentDisplay("[RUN FAILED]");
      showError("Single-seed run failed: " + err.message);
      setStatus("[ERROR]", "Single-seed run failed");
    }
  }

  async function runPairedStudy() {
    const jobId = ++activeJobId;
    hideError();
    hideVerifyBanner();
    clearExperimentDisplay("[RUNNING PAIRED STUDY...]");
    setStatus("[RUNNING]", "Executing paired multi-seed study...");

    const params = new URLSearchParams({
      seed: seedInput.value,
      replicates: replicatesInput.value,
      cases: casesInput.value,
      scenario: scenarioSelect.value,
      size: sizeInput.value,
    });
    try {
      const rec = await fetchJson("/api/study?" + params.toString());
      if (jobId !== activeJobId) return;
      renderStudyAnalysis(rec, "STUDY");
      setStatus("[COMPLETE]", "Paired study complete (" + rec.result.n_seeds + " seeds)");
    } catch (err) {
      if (jobId !== activeJobId) return;
      clearExperimentDisplay("[STUDY FAILED]");
      showError("Paired study failed: " + err.message);
      setStatus("[ERROR]", "Paired study failed");
    }
  }

  async function analyzeImportedDataset() {
    const jobId = ++activeJobId;
    hideError();
    hideVerifyBanner();
    // Strictly clear any existing result before reading or validating imported file
    clearExperimentDisplay("[VALIDATING IMPORT...]");

    const file = datasetFileInput.files && datasetFileInput.files[0];
    if (!file) {
      clearExperimentDisplay("[IMPORT REJECTED]");
      showError("No dataset file selected. Please choose a faultline-dataset-v1 JSON file.");
      setStatus("[ERROR]", "Dataset import failed: no file selected");
      return;
    }

    setStatus("[RUNNING]", "Validating and analyzing imported dataset...");
    try {
      const rawText = await file.text();
      if (jobId !== activeJobId) return;
      let parsed;
      try {
        parsed = JSON.parse(rawText);
      } catch (parseErr) {
        throw new Error("File is not valid JSON: " + parseErr.message);
      }
      const size = Number.parseInt(sizeInput.value, 10);
      const rec = await fetchJson("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset: parsed, size }),
      });
      if (jobId !== activeJobId) return;
      renderSingleAnalysis(rec, "IMPORTED DATASET");
      setStatus("[COMPLETE]", "Imported dataset analyzed (" + rec.result.dataset + ")");
    } catch (err) {
      if (jobId !== activeJobId) return;
      // Never fall back to fixture data after import failure
      clearExperimentDisplay("[IMPORT REJECTED]");
      showError("Dataset import rejected: " + err.message);
      setStatus("[ERROR]", "Dataset import failed");
    }
  }

  function exportCurrentReceipt() {
    if (!currentReceipt) return;
    const blob = new Blob([JSON.stringify(currentReceipt, null, 2) + "\n"], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "faultline-receipt-" + currentReceipt.kind + "-" + currentReceipt.payload_sha256.slice(0, 10) + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function verifyImportedReceipt() {
    const jobId = ++activeJobId;
    hideError();
    hideVerifyBanner();

    const file = receiptFileInput.files && receiptFileInput.files[0];
    if (!file) {
      showError("No receipt file selected for verification.");
      setStatus("[ERROR]", "Receipt verification failed: no file selected");
      return;
    }

    setStatus("[RUNNING]", "Verifying receipt hashes and replaying computation...");
    try {
      const rawText = await file.text();
      if (jobId !== activeJobId) return;
      let parsed;
      try {
        parsed = JSON.parse(rawText);
      } catch (parseErr) {
        throw new Error("Receipt file is not valid JSON: " + parseErr.message);
      }
      const ver = await fetchJson("/api/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      if (jobId !== activeJobId) return;
      showVerifyBanner(Boolean(ver.valid), ver.reason);
      if (ver.valid) {
        if (parsed.kind === "demo" || parsed.kind === "analyze") {
          renderSingleAnalysis(parsed, "REPLAYED RECEIPT");
        } else if (parsed.kind === "study") {
          renderStudyAnalysis(parsed, "REPLAYED STUDY");
        }
        setStatus("[VERIFIED]", "Receipt verified and replayed");
      } else {
        clearExperimentDisplay("[RECEIPT REJECTED]");
        setStatus("[INVALID]", "Receipt failed replay verification");
      }
    } catch (err) {
      if (jobId !== activeJobId) return;
      clearExperimentDisplay("[VERIFY ERROR]");
      showError("Receipt verification error: " + err.message);
      setStatus("[ERROR]", "Receipt verification error");
    }
  }

  async function loadParityAndHealth() {
    try {
      const [health, parity] = await Promise.all([
        fetchJson("/api/health"),
        fetchJson("/api/parity"),
      ]);
      headerSourceSha.textContent = health.source_sha256.slice(0, 16) + "...";
      headerSourceSha.title = health.source_sha256;
      renderParityDemo(parity);
    } catch (err) {
      showError("Failed to initialize laboratory status: " + err.message);
    }
  }

  runDemoBtn.addEventListener("click", runSingleDemo);
  runStudyBtn.addEventListener("click", runPairedStudy);
  analyzeImportBtn.addEventListener("click", analyzeImportedDataset);
  exportReceiptBtn.addEventListener("click", exportCurrentReceipt);
  verifyReceiptBtn.addEventListener("click", verifyImportedReceipt);
  reloadParityBtn.addEventListener("click", loadParityAndHealth);

  loadParityAndHealth().then(() => {
    runSingleDemo();
  });
})();
