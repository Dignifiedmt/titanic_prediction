/* Titanic Predictor interactions: theme, validation, loading and result animation. */
(() => {
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const form = document.getElementById("predictionForm");
  const predictButton = document.getElementById("predictButton");
  const resetButton = document.getElementById("resetButton");
  const resultCard = document.getElementById("resultCard");
  const probabilityBar = document.getElementById("probabilityBar");

  function readTheme() {
    try { return localStorage.getItem("titanic-theme"); }
    catch (_) { return null; }
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    if (themeToggle) {
      const nextLabel = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
      themeToggle.setAttribute("aria-label", nextLabel);
      themeToggle.setAttribute("title", nextLabel);
    }
    try { localStorage.setItem("titanic-theme", theme); }
    catch (_) { /* The theme still works if storage is unavailable. */ }
  }

  // Use the value set in the document head, or fall back to the system theme.
  if (!root.dataset.theme) {
    const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    applyTheme(readTheme() || preferred);
  } else {
    applyTheme(root.dataset.theme);
  }

  themeToggle?.addEventListener("click", () => {
    applyTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  // Client-side checks improve feedback; Flask repeats all important validation.
  form?.addEventListener("submit", (event) => {
    if (!form.reportValidity()) {
      event.preventDefault();
      return;
    }
    if (predictButton) {
      predictButton.disabled = true;
      predictButton.classList.add("is-loading");
      const label = predictButton.querySelector(".button-label");
      if (label) label.textContent = "Generating prediction…";
    }
  });

  resetButton?.addEventListener("click", () => {
    window.setTimeout(() => {
      // The browser resets field values. Remove a previous result from this page.
      resultCard?.remove();
      const alert = document.querySelector(".alert");
      alert?.remove();
      if (predictButton) {
        predictButton.disabled = false;
        predictButton.classList.remove("is-loading");
        const label = predictButton.querySelector(".button-label");
        if (label) label.textContent = "Predict survival";
      }
    }, 0);
  });

  if (probabilityBar) {
    const rawValue = Number(probabilityBar.dataset.value || 0);
    const safeValue = Math.min(100, Math.max(0, Number.isFinite(rawValue) ? rawValue : 0));
    requestAnimationFrame(() => {
      window.setTimeout(() => { probabilityBar.style.width = `${safeValue}%`; }, 120);
    });
  }

  if (resultCard) {
    window.setTimeout(() => {
      resultCard.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
    }, 250);
  }

  // Add a subtle focus class for assistive and keyboard users.
  document.querySelectorAll(".field input, .field select").forEach((control) => {
    control.addEventListener("focus", () => control.closest(".field")?.classList.add("is-focused"));
    control.addEventListener("blur", () => control.closest(".field")?.classList.remove("is-focused"));
  });
})();
