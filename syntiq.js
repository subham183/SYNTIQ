/* ═══════════════════════════════════════════════════════════
   SYNTIQ — Frontend Logic
   Tab management, API calls, dynamic result rendering
   ═══════════════════════════════════════════════════════════ */

'use strict';

// ── TAB SWITCHING ────────────────────────────────────────────

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  });
});


// ── SAMPLE DATA ──────────────────────────────────────────────

const SAMPLES = {
  code: `import sqlite3

def process_user_data(user_input, db_path):
    """Process user data from form submission."""
    conn = sqlite3.connect(db_path)
    
    # Dangerous: eval of user input
    result = eval(user_input)
    
    for i in range(len(result)):
        for j in range(len(result[i])):
            for k in range(10):
                # Triple nested loop — high complexity
                if result[i][j][k] > 0:
                    pass
    
    try:
        cursor = conn.execute("SELECT * FROM users")
    except:
        pass  # Bare except swallows all errors
    
    global db_connection
    db_connection = conn
    
    return result

async def fetch_data(url):
    import subprocess
    output = subprocess.run(url, shell=True)
    return output`,

  text: `Furthermore, it is worth noting that this comprehensive analysis delves deeply into the complex nature of artificial intelligence systems. In conclusion, the overall performance demonstrates notable improvements across all metrics. 

Firstly, the system processes data efficiently. Secondly, it generates accurate results. Lastly, the outputs are notably consistent.

Moreover, it's important to note that these findings are significant. The data shows that, consequently, users experience better outcomes. In summary, the system overall performs as expected.

To summarize: this tool is a comprehensive solution that delves into all aspects of the problem space.`
};

function loadSample(type) {
  switch(type) {
    case 'code':        document.getElementById('dual-code').value  = SAMPLES.code;  break;
    case 'text':        document.getElementById('dual-text').value  = SAMPLES.text;  break;
    case 'code-only':   document.getElementById('code-only').value  = SAMPLES.code;  break;
    case 'text-only':   document.getElementById('text-only').value  = SAMPLES.text;  break;
  }
}


// ── API HELPERS ──────────────────────────────────────────────

function setStatus(id, state, msg) {
  const el = document.getElementById(id);
  el.className = 'status-indicator ' + state;
  el.textContent = msg;
}

async function postJSON(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return r.json();
}


// ── RENDERING HELPERS ────────────────────────────────────────

function gradeCard(grade) {
  return `<span class="grade-display grade-${grade}">${grade}</span>`;
}

function renderMetrics(metrics, grade) {
  const risk = metrics.risk_score || 0;
  const riskClass = risk < 20 ? '' : risk < 50 ? 'warn' : 'danger';
  return `
    <div class="metrics-grid">
      ${gradeCard(grade)}
      <div class="metric-card highlight">
        <div class="metric-val">${metrics.complexity || 0}</div>
        <div class="metric-label">Cyclomatic Complexity</div>
      </div>
      <div class="metric-card ${riskClass}">
        <div class="metric-val">${risk}</div>
        <div class="metric-label">Risk Score</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.loc || 0}</div>
        <div class="metric-label">Lines of Code</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.function_count || 0}</div>
        <div class="metric-label">Functions</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.max_nesting_depth || 0}</div>
        <div class="metric-label">Max Nesting Depth</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.nested_loops || 0}</div>
        <div class="metric-label">Nested Loops</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.import_count || 0}</div>
        <div class="metric-label">Imports</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${metrics.comment_lines || 0}</div>
        <div class="metric-label">Comment Lines</div>
      </div>
    </div>`;
}

function renderHazards(hazards) {
  if (!hazards || !hazards.length) {
    return `<div class="hazard-item">
      <span class="hazard-sev sev-INFO">CLEAN</span>
      <div class="hazard-detail">No security hazards detected.</div>
    </div>`;
  }
  return hazards.map(h => `
    <div class="hazard-item">
      <span class="hazard-sev sev-${h.severity}">${h.severity}</span>
      <div>
        <div class="hazard-detail">${h.detail}</div>
        <div class="hazard-line">Line ${h.line} · ${h.type} · <code>${h.node}</code></div>
      </div>
    </div>`).join('');
}

function renderFunctions(fns) {
  if (!fns || !fns.length) return '<div class="empty-state">No functions detected.</div>';
  return fns.map(f => `
    <div class="fn-item">
      <span class="fn-name">${f.is_async ? '<span class="fn-async">async</span> ' : ''}def ${f.name}()</span>
      <span class="fn-args">(${f.args.join(', ')})</span>
      <span class="fn-meta">
        L${f.line} · ${f.body_lines} lines
        <span class="${f.has_docstring ? 'fn-doc' : 'fn-nodoc'}">&nbsp;${f.has_docstring ? '✓ docstring' : '✗ no docstring'}</span>
      </span>
    </div>`).join('');
}

function renderCodeResult(r) {
  if (!r || !r.success) {
    const errs = r && r.errors ? r.errors.join('<br>') : 'Unknown error';
    return `<div class="result-section">
      <div class="result-section-title">⚠ Parse Error</div>
      <div class="hazard-item"><span class="hazard-sev sev-CRITICAL">ERROR</span>
        <div class="hazard-detail">${errs}</div></div>
    </div>`;
  }
  return `
    <div class="result-section">
      <div class="result-section-title">Code Metrics &amp; Complexity</div>
      ${renderMetrics(r.metrics, r.grade)}
    </div>
    <div class="result-section">
      <div class="result-section-title">Security Hazards (AST Flagged)</div>
      <div class="hazard-list">${renderHazards(r.hazards)}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Function Profile</div>
      <div class="fn-list">${renderFunctions(r.functions)}</div>
    </div>`;
}

function renderTextResult(r) {
  if (!r || !r.metrics) return '';
  const m = r.metrics;
  const replacements = r.replacements || [];
  const repTags = replacements.length
    ? replacements.map(rp =>
        `<span class="replacement-tag">
          <span class="rt-from">${rp.from}</span>
          <span class="rt-arrow"> → </span>
          <span class="rt-to">${rp.to || '[removed]'}</span>
        </span>`).join('')
    : '<span style="font-family:var(--mono);font-size:.75rem;color:var(--text3)">No AI fingerprints detected.</span>';

  return `
    <div class="result-section">
      <div class="result-section-title">Linguistic Metrics</div>
      <div class="metrics-grid">
        <div class="metric-card highlight">
          <div class="metric-val">${m.fingerprints_removed}</div>
          <div class="metric-label">Fingerprints Removed</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">${m.reduction_pct}%</div>
          <div class="metric-label">Size Reduction</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">${m.orig_perplexity}</div>
          <div class="metric-label">Original Perplexity</div>
        </div>
        <div class="metric-card highlight">
          <div class="metric-val">${m.proc_perplexity}</div>
          <div class="metric-label">Post Perplexity</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">${m.orig_burstiness}</div>
          <div class="metric-label">Original Burstiness</div>
        </div>
        <div class="metric-card highlight">
          <div class="metric-val">${m.proc_burstiness}</div>
          <div class="metric-label">Post Burstiness</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">${m.original_chars}</div>
          <div class="metric-label">Original Chars</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">${m.processing_ms}ms</div>
          <div class="metric-label">Processing Time</div>
        </div>
      </div>
    </div>
    <div class="result-section">
      <div class="result-section-title">AI Fingerprint Replacements</div>
      <div class="replacement-list">${repTags}</div>
    </div>
    <div class="result-section">
      <div class="result-section-title">Before / After Comparison</div>
      <div class="comparison-grid">
        <div class="compare-col">
          <div class="compare-header before">ORIGINAL</div>
          <div class="compare-text">${escHtml(r.original)}</div>
        </div>
        <div class="compare-col">
          <div class="compare-header after">HUMANIZED</div>
          <div class="compare-text">${escHtml(r.humanized)}</div>
        </div>
      </div>
    </div>`;
}

function escHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}


// ── DUAL PIPELINE ────────────────────────────────────────────

async function runDual() {
  const code = document.getElementById('dual-code').value.trim();
  const text = document.getElementById('dual-text').value.trim();
  const btn  = document.getElementById('btn-dual');
  const res  = document.getElementById('dual-results');

  if (!code && !text) {
    setStatus('dual-status', 'error', '✗ Provide code and/or text');
    return;
  }

  btn.disabled = true;
  setStatus('dual-status', 'running', '⟳ Running dual pipeline...');
  res.classList.add('hidden');

  try {
    const data = await postJSON('/api/submit/', { code, text });

    if (data.error) throw new Error(data.error);

    let html = `<div style="font-family:var(--mono);font-size:.68rem;color:var(--text3);margin-bottom:1.5rem">
      SUBMISSION &nbsp;<span style="color:var(--accent-a);font-weight:700">#${data.submission_id}</span>
      &nbsp;·&nbsp; Dual pipeline complete
    </div>`;

    if (data.code_analysis && Object.keys(data.code_analysis).length) {
      html += `<div class="result-section-title" style="font-family:var(--mono);font-size:.7rem;color:var(--accent-a);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1rem">
        ⟨/⟩ TRACK A — AST Analysis
      </div>`;
      html += renderCodeResult(data.code_analysis);
    }

    if (data.text_humanization && Object.keys(data.text_humanization).length) {
      html += `<div class="result-section-title" style="font-family:var(--mono);font-size:.7rem;color:var(--accent-b);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1rem;margin-top:2rem">
        ◉ TRACK B — Linguistic Humanization
      </div>`;
      html += renderTextResult(data.text_humanization);
    }

    res.innerHTML = html;
    res.classList.remove('hidden');
    setStatus('dual-status', 'done', `✓ Job #${data.submission_id} complete`);
    res.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Live update hero stats
    fetch('/api/stats/').then(r => r.json()).then(s => {
      const ids = ['hs-total','hs-chars','hs-hazards','hs-fp'];
      const vals = [s.total_submissions, s.total_chars_modified, s.total_hazards_caught, s.total_fingerprints];
      ids.forEach((id, i) => {
        const el = document.getElementById(id);
        if (el) { el.textContent = vals[i]; el.style.color = 'var(--accent-g)'; setTimeout(() => el.style.color = '', 1000); }
      });
    });

  } catch(e) {
    setStatus('dual-status', 'error', '✗ ' + e.message);
  } finally {
    btn.disabled = false;
  }
}


// ── CODE ONLY ────────────────────────────────────────────────

async function runCode() {
  const code = document.getElementById('code-only').value.trim();
  const res  = document.getElementById('code-results');
  if (!code) { setStatus('code-status','error','✗ No code provided'); return; }
  setStatus('code-status','running','⟳ Parsing AST...');
  res.classList.add('hidden');
  try {
    const data = await postJSON('/api/analyze/', { code });
    res.innerHTML = renderCodeResult(data);
    res.classList.remove('hidden');
    setStatus('code-status','done','✓ AST parsed');
    res.scrollIntoView({ behavior:'smooth', block:'start' });
  } catch(e) {
    setStatus('code-status','error','✗ ' + e.message);
  }
}


// ── TEXT ONLY ────────────────────────────────────────────────

async function runText() {
  const text = document.getElementById('text-only').value.trim();
  const res  = document.getElementById('text-results');
  if (!text) { setStatus('text-status','error','✗ No text provided'); return; }
  setStatus('text-status','running','⟳ Humanizing...');
  res.classList.add('hidden');
  try {
    const data = await postJSON('/api/humanize/', { text });
    res.innerHTML = renderTextResult(data);
    res.classList.remove('hidden');
    setStatus('text-status','done','✓ Humanization complete');
    res.scrollIntoView({ behavior:'smooth', block:'start' });
  } catch(e) {
    setStatus('text-status','error','✗ ' + e.message);
  }
}


// ── KEYBOARD SHORTCUT ────────────────────────────────────────

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    const activePanel = document.querySelector('.panel.active');
    if (!activePanel) return;
    if (activePanel.id === 'tab-dual')  runDual();
    if (activePanel.id === 'tab-code')  runCode();
    if (activePanel.id === 'tab-text')  runText();
  }
});


// ── ANIMATED COUNTER (hero stats) ────────────────────────────

function animateCounter(el, target, duration = 800) {
  const start = performance.now();
  const from = 0;
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    el.textContent = Math.floor(from + (target - from) * p);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

window.addEventListener('DOMContentLoaded', () => {
  ['hs-total','hs-chars','hs-hazards','hs-fp'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      const v = parseInt(el.textContent) || 0;
      if (v > 0) animateCounter(el, v);
    }
  });
});
