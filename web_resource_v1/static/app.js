const $ = (sel) => document.querySelector(sel);
const fmt = (n) => Number(n || 0).toLocaleString();

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function metric(label, value) {
  return `<article class="metric"><div class="num">${fmt(value)}</div><div class="label">${label}</div></article>`;
}

async function loadRelease() {
  const data = await getJSON('/api/v1/releases');
  $('#release-status').textContent = data.status;
  const scope = data.source_freeze_summary.scope || {};
  $('#metrics').innerHTML = [
    metric('paper final artifacts', scope.paper_final_artifact_count),
    metric('public v1 candidate papers', scope.public_v1_candidate_papers),
    metric('database audit rows', scope.database_audit_rows),
    metric('non-source-verified rows', scope.non_source_verified_rows),
  ].join('');
}

function renderRow(row) {
  const title = row.audit_record_id || row.paper_id || row.activity_record_id || row.mechanism_claim_id || row.issue_id || 'record';
  const tags = ['database', 'status', 'difference_categories', 'review_status', 'evidence_class']
    .map((k) => row[k] ? `<span class="tag">${row[k]}</span>` : '')
    .join('');
  const fields = Object.entries(row)
    .filter(([k, v]) => v && !['audit_record_id', 'activity_record_id', 'mechanism_claim_id', 'issue_id'].includes(k))
    .slice(0, 12)
    .map(([k, v]) => `<div>${k}</div><div>${String(v).slice(0, 420)}</div>`)
    .join('');
  return `<article class="result-card"><h3>${title}</h3><div class="tags">${tags}</div><div class="kv">${fields}</div></article>`;
}

async function runSearch(event) {
  if (event) event.preventDefault();
  const form = new FormData($('#search-form'));
  const params = new URLSearchParams();
  for (const [key, value] of form.entries()) {
    if (String(value).trim()) params.set(key, value);
  }
  $('#search-summary').textContent = 'Searching large release tables...';
  $('#results').innerHTML = '';
  try {
    const data = await getJSON(`/api/v1/search?${params}`);
    $('#search-summary').textContent = `${fmt(data.matched_rows)} matched, ${fmt(data.returned_rows)} returned, ${fmt(data.scanned_rows)} scanned.`;
    $('#results').innerHTML = data.results.map(renderRow).join('') || '<p class="muted">No results.</p>';
  } catch (err) {
    $('#search-summary').textContent = `Search failed: ${err.message}`;
  }
}

async function loadDownloads() {
  const data = await getJSON('/api/v1/downloads');
  $('#downloads-list').innerHTML = data.files.map((file) => `
    <div class="download-item">
      <a href="${file.url}">${file.name}</a>
      <span>${fmt(file.size_bytes)} bytes</span>
    </div>
  `).join('');
}

async function boot() {
  await loadRelease();
  await loadDownloads();
  $('#search-form').addEventListener('submit', runSearch);
  const form = $('#search-form');
  form.q.value = 'DBAASPS_18493';
  form.status.value = 'source_conflict';
  await runSearch();
}

boot().catch((err) => {
  $('#release-status').textContent = `failed: ${err.message}`;
});
