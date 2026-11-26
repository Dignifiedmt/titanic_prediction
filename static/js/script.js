/* Titanic Predictor interactions: theme, validation, profile helper and chart. */
(() => {
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const form = document.getElementById("predictionForm");
  const predictButton = document.getElementById("predictButton");
  const resetButton = document.getElementById("resetButton");
  const resultCard = document.getElementById("resultCard");
  const smartProfile = document.getElementById("smartProfile");

  function readTheme() { try { return localStorage.getItem("titanic-theme"); } catch (_) { return null; } }
  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (themeToggle) {
      const nextLabel = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
      themeToggle.setAttribute("aria-label", nextLabel);
      themeToggle.setAttribute("title", nextLabel);
    }
    try { localStorage.setItem("titanic-theme", theme); } catch (_) { /* Theme still works without storage. */ }
  }
  if (!root.dataset.theme) applyTheme(readTheme() || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  else applyTheme(root.dataset.theme);
  themeToggle?.addEventListener("click", () => applyTheme(root.dataset.theme === "dark" ? "light" : "dark"));

  form?.addEventListener("submit", (event) => {
    if (!form.reportValidity()) { event.preventDefault(); return; }
    if (predictButton) {
      predictButton.disabled = true;
      predictButton.classList.add("is-loading");
      const label = predictButton.querySelector(".button-label");
      if (label) label.textContent = "Generating prediction…";
    }
  });
  resetButton?.addEventListener("click", () => window.setTimeout(() => {
    resultCard?.remove();
    document.querySelector(".alert")?.remove();
    if (predictButton) {
      predictButton.disabled = false;
      predictButton.classList.remove("is-loading");
      const label = predictButton.querySelector(".button-label");
      if (label) label.textContent = "Predict survival";
    }
    updateProfileSummary();
  }, 0));

  function updateProfileSummary() {
    if (!smartProfile || !form) return;
    const age = Number(form.elements.age.value);
    const sibsp = Number(form.elements.sibsp.value || 0);
    const parch = Number(form.elements.parch.value || 0);
    if (form.elements.age.value === "") {
      smartProfile.textContent = "Add an age to see a quick profile summary. This helper does not change the model prediction.";
      return;
    }
    const partySize = Math.max(1, sibsp + parch + 1);
    const ageLabel = age < 16 ? "child" : age >= 60 ? "older adult" : "adult";
    const classLabel = { "1": "1st", "2": "2nd", "3": "3rd" }[form.elements.pclass.value] || "selected";
    smartProfile.textContent = `${ageLabel[0].toUpperCase()}${ageLabel.slice(1)} passenger · ${classLabel} class · party size ${partySize}. This is a profile summary, not an explanation of the model's decision.`;
  }
  form?.querySelectorAll("input, select").forEach((control) => control.addEventListener("input", updateProfileSummary));
  form?.querySelectorAll("select").forEach((control) => control.addEventListener("change", updateProfileSummary));
  updateProfileSummary();

  const filter = document.getElementById("chartSexFilter");
  const chart = document.getElementById("survivalChart");
  const chartDataElement = document.getElementById("survivalData");
  let chartData = [];
  try { chartData = JSON.parse(chartDataElement?.textContent || "[]"); } catch (_) { chartData = []; }
  function renderChart() {
    if (!chart) return;
    const selectedSex = filter?.value || "all";
    const sexes = selectedSex === "all" ? ["female", "male"] : [selectedSex];
    chart.replaceChildren();
    for (const pclass of [1, 2, 3]) {
      const group = document.createElement("div"); group.className = "chart-group";
      const title = document.createElement("div"); title.className = "chart-group-title"; title.textContent = `${pclass}${pclass === 1 ? "st" : pclass === 2 ? "nd" : "rd"} class`;
      const bars = document.createElement("div"); bars.className = "chart-bars";
      for (const sex of sexes) {
        const record = chartData.find((item) => Number(item.class) === pclass && item.sex.toLowerCase() === sex);
        const wrap = document.createElement("div"); wrap.className = "chart-bar-wrap";
        if (record) {
          const value = document.createElement("span"); value.className = "chart-value"; value.textContent = `${record.rate}%`;
          const bar = document.createElement("div"); bar.className = `chart-bar ${sex}`; bar.style.height = `${Math.max(3, Math.min(100, Number(record.rate)))}%`;
          bar.title = `${sex}: ${record.rate}% observed survival (${record.count} passengers)`;
          bar.setAttribute("aria-label", bar.title); bar.setAttribute("role", "img");
          const label = document.createElement("span"); label.className = "chart-x-label"; label.textContent = sex === "female" ? "Female" : "Male";
          wrap.append(value, bar, label);
        } else {
          const empty = document.createElement("span"); empty.className = "chart-value"; empty.textContent = "No data"; wrap.append(empty);
        }
        bars.append(wrap);
      }
      group.append(title, bars); chart.append(group);
    }
  }
  filter?.addEventListener("change", renderChart);
  renderChart();
  resultCard?.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
  document.querySelectorAll(".field input, .field select").forEach((control) => {
    control.addEventListener("focus", () => control.closest(".field")?.classList.add("is-focused"));
    control.addEventListener("blur", () => control.closest(".field")?.classList.remove("is-focused"));
  });
})();
