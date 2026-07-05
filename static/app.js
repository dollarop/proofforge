const form = document.querySelector("#campaign-form");
const button = document.querySelector("#generate");
const gallery = document.querySelector("#gallery");
const empty = document.querySelector("#empty");
const integrity = document.querySelector("#integrity");
const manifest = document.querySelector("#manifest");
const resultTitle = document.querySelector("#result-title");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  button.firstElementChild.textContent = "Running pipeline...";
  const values = new FormData(form);
  const payload = Object.fromEntries(values.entries());
  payload.variants = 3;

  try {
    const response = await fetch("/api/campaigns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Pipeline failed (${response.status})`);
    render(await response.json());
  } catch (error) {
    resultTitle.textContent = error.message;
  } finally {
    button.disabled = false;
    button.firstElementChild.textContent = "Generate campaign pack";
  }
});

function render(result) {
  empty.classList.add("hidden");
  resultTitle.textContent = `${result.assets.length} evaluated variants`;
  integrity.classList.remove("hidden");
  integrity.textContent = result.verified ? "✓ Manifest verified" : "Verification failed";
  gallery.innerHTML = result.assets.map((asset, index) => `
    <article class="asset">
      <img src="${asset.url}" alt="${escapeHtml(asset.alt_text)}">
      <div class="asset-info">
        <div class="asset-row"><span class="asset-title">Variant ${index + 1}</span><span class="score">${asset.score}/100</span></div>
        <p class="hash" title="${asset.sha256}">SHA-256 ${asset.sha256}</p>
      </div>
    </article>
  `).join("");
  manifest.classList.remove("hidden");
  manifest.innerHTML = `Run <strong>${result.run_id}</strong> · ${result.storage.toUpperCase()} storage · <a href="${result.manifest_url}" target="_blank" rel="noreferrer">Inspect canonical manifest</a>`;
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
  })[character]);
}

