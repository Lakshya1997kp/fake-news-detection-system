/* ═══════════════════════════════════════════════════════════
   TruthLens – Frontend App
   Base URL: adjust if your Flask server runs on a different port
═══════════════════════════════════════════════════════════ */

const API = '';

/* ─── TOKEN HELPERS ─────────────────────────────────────── */
const getToken  = ()        => localStorage.getItem('tl_token');
const setToken  = (t)       => localStorage.setItem('tl_token', t);
const clearToken = ()       => localStorage.removeItem('tl_token');
const isLoggedIn = ()       => !!getToken();

const authHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${getToken()}`
});

/* ─── ROUTER ────────────────────────────────────────────── */
const PROTECTED = ['analyze', 'history', 'profile'];
const GUEST_ONLY = ['login', 'signup'];

function navigate(page) {
  if (PROTECTED.includes(page) && !isLoggedIn()) { showPage('login'); return; }
  if (GUEST_ONLY.includes(page) && isLoggedIn())  { showPage('analyze'); return; }
  showPage(page);
}

function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  const el = document.getElementById(`page-${page}`);
  if (el) el.classList.remove('hidden');

  // update active nav link
  document.querySelectorAll('.nav-item').forEach(a => {
    a.classList.toggle('active', a.dataset.page === page);
  });

  // show/hide shared footer
  const footer = document.getElementById('siteFooter');
  if (footer) footer.style.display = GUEST_ONLY.includes(page) ? 'none' : 'block';

  // swap navbar brand subtitle on auth pages
  const brandSub = document.getElementById('brandSub');
  if (brandSub) {
    brandSub.style.display = GUEST_ONLY.includes(page) ? 'block' : 'none';
  }

  // lifecycle hooks
  if (page === 'profile')  loadProfile();
  if (page === 'history')  loadHistory();
  if (page === 'analyze')  resetAnalyze();

  window.scrollTo(0, 0);
}

/* ─── NAV VISIBILITY ────────────────────────────────────── */
function updateNav() {
  const loggedIn = isLoggedIn();
  document.getElementById('navLinks').style.display  = loggedIn ? 'flex' : 'none';
  document.getElementById('navAuth').style.display   = loggedIn ? 'none' : 'none';
  document.getElementById('logoutBtn').style.display = loggedIn ? 'flex' : 'none';
}

/* ─── TOAST ─────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type}`;
  t.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), 3200);
}

/* ─── ALERT HELPERS ─────────────────────────────────────── */
function showAlert(id, msg, type = 'alert-error') {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `alert ${type}`;
  el.classList.remove('hidden');
}
function hideAlert(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

/* ─── BUTTON LOADING STATE ──────────────────────────────── */
function setLoading(btn, loading) {
  const text    = btn.querySelector('.btn-text');
  const spinner = btn.querySelector('.spinner');
  btn.disabled  = loading;
  if (text)    text.classList.toggle('hidden', loading);
  if (spinner) spinner.classList.toggle('hidden', !loading);
}

/* ─── PASSWORD TOGGLE ───────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('.toggle-pw');
  if (!btn) return;
  const input = document.getElementById(btn.dataset.target);
  if (!input) return;
  const isText = input.type === 'text';
  input.type = isText ? 'password' : 'text';
  btn.querySelector('i').className = isText ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
});

/* ─── LINK NAVIGATION ───────────────────────────────────── */
document.addEventListener('click', e => {
  const a = e.target.closest('[data-page]');
  if (!a) return;
  e.preventDefault();
  navigate(a.dataset.page);
});

/* ─── HAMBURGER ─────────────────────────────────────────── */
document.getElementById('hamburger').addEventListener('click', () => {
  document.getElementById('navLinks').classList.toggle('open');
});

/* ─── LOGOUT ────────────────────────────────────────────── */
document.getElementById('logoutBtn').addEventListener('click', e => {
  e.preventDefault();
  clearToken();
  updateNav();
  showToast('Logged out successfully');
  navigate('login');
});

/* ══════════════════════════════════════════════════════════
   AUTH
══════════════════════════════════════════════════════════ */

/* LOGIN */
document.getElementById('loginForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideAlert('loginError');
  const btn   = document.getElementById('loginBtn');
  const email = document.getElementById('loginEmail').value.trim();
  const pass  = document.getElementById('loginPassword').value;

  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: pass })
    });
    const data = await res.json();
    if (data.token) {
    setToken(data.token);
      updateNav();
      showToast('Welcome back!', 'success');
      navigate('analyze');
    } else {
      showAlert('loginError', data.message || 'Login failed');
    }
  } catch {
    showAlert('loginError', 'Could not connect to server. Is Flask running?');
  } finally {
    setLoading(btn, false);
  }
});

/* SIGNUP */
document.getElementById('signupForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideAlert('signupError');
  hideAlert('signupSuccess');
  const btn  = document.getElementById('signupBtn');
  const name = document.getElementById('signupName').value.trim();
  const email= document.getElementById('signupEmail').value.trim();
  const pass = document.getElementById('signupPassword').value;
  const conf = document.getElementById('signupConfirm').value;

  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password: pass, confirm_password: conf })
    });
    const data = await res.json();
    if (data.status === 200) {
      showAlert('signupSuccess', 'Account created! Redirecting to login…', 'alert-success');
      document.getElementById('signupForm').reset();
      setTimeout(() => navigate('login'), 1800);
    } else {
      showAlert('signupError', data.message || 'Signup failed');
    }
  } catch {
    showAlert('signupError', 'Could not connect to server. Is Flask running?');
  } finally {
    setLoading(btn, false);
  }
});

/* ══════════════════════════════════════════════════════════
   ANALYZE
══════════════════════════════════════════════════════════ */

function resetAnalyze() {
  document.getElementById('analyzeText').value = '';
  document.getElementById('charCount').textContent = '0 / 10,000';
  document.getElementById('resultCard').classList.add('hidden');
  hideAlert('analyzeError');
}

document.getElementById('analyzeText').addEventListener('input', function () {
  const len = this.value.length;
  const cc  = document.getElementById('charCount');
  cc.textContent = `${len} / 10,000`;
  cc.style.color = len > 9500 ? 'var(--danger)' : len > 8000 ? 'var(--warning)' : '';
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  hideAlert('analyzeError');
  const btn  = document.getElementById('analyzeBtn');
  const text = document.getElementById('analyzeText').value.trim();

  if (!text) { showAlert('analyzeError', 'Please enter some text to analyze.'); return; }

  setLoading(btn, true);
  document.getElementById('resultCard').classList.add('hidden');

  try {
    const res  = await fetch(`${API}/analyze`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ text })
    });
    const data = await res.json();

    if (res.status === 401) { handleExpired(); return; }

    if (data.status === 200 && data.message?.result) {
      renderResult(data.message.result);
    } else {
      showAlert('analyzeError', data.message || 'Analysis failed.');
    }
  } catch {
    showAlert('analyzeError', 'Could not connect to server.');
  } finally {
    setLoading(btn, false);
  }
});

function renderResult(r) {
  const card   = document.getElementById('resultCard');
  const header = document.getElementById('resultHeader');
  const icon   = document.getElementById('resultIcon');
  const label  = document.getElementById('resultLabel');
  const conf   = document.getElementById('resultConfidence');

  const labelLower = (r.label || '').toLowerCase();
  let cls, ico, labelText;

  if (labelLower.includes('fake')) {
    cls = 'fake'; ico = '🚨'; labelText = 'Likely Fake News';
  } else if (labelLower.includes('real') || labelLower.includes('true')) {
    cls = 'real'; ico = '✅'; labelText = 'Likely Real News';
  } else {
    cls = 'uncertain'; ico = '⚠️'; labelText = 'Uncertain';
  }

  header.className  = `result-header ${cls}`;
  icon.textContent  = ico;
  label.textContent = labelText;
  conf.textContent  = `Confidence: ${(r.confidence * 100).toFixed(1)}%`;

  // ── ML Model ──────────────────────────────────────────────
  const ml = r.breakdown?.ml_model;
  if (ml) {
    const mlLabelEl = document.getElementById('mlLabel');
    const mlBarEl   = document.getElementById('mlBar');
    const mlScoreEl = document.getElementById('mlScore');
    const pct       = ((ml.score || 0) * 100).toFixed(1);

    mlLabelEl.textContent = ml.label || '—';
    mlLabelEl.style.color = ml.label?.toLowerCase().includes('fake') ? 'var(--danger)' : 'var(--success)';
    mlScoreEl.textContent = `ML Classifier score: ${pct}%`;
    mlBarEl.style.width      = `${pct}%`;
    mlBarEl.style.background = ml.label?.toLowerCase().includes('fake') ? 'var(--danger)' : 'var(--success)';
  }

  // ── Wikipedia ─────────────────────────────────────────────
  const wiki = r.breakdown?.wikipedia;
  if (wiki) {
    const wikiCredEl   = document.getElementById('wikiCredible');
    const wikiBarEl    = document.getElementById('wikiBar');
    const wikiMatchEl  = document.getElementById('wikiMatched');
    const wikiSumEl    = document.getElementById('wikiSummary');

    if (wiki.found) {
      const credText        = wiki.credible ? 'Credible match found' : 'Low credibility match';
      wikiCredEl.textContent = credText;
      wikiCredEl.style.color = wiki.credible ? 'var(--success)' : 'var(--danger)';

      // fake_prob: 0 = real, 1 = fake → bar shows "realness" = 1 - fake_prob
      const realPct          = ((1 - (wiki.fake_prob || 0.5)) * 100).toFixed(1);
      wikiBarEl.style.width      = `${realPct}%`;
      wikiBarEl.style.background = wiki.credible ? 'var(--success)' : 'var(--danger)';

      wikiMatchEl.textContent = wiki.matched ? `Matched: "${wiki.matched}"` : '';
      wikiSumEl.textContent   = wiki.summary ? `"${wiki.summary.slice(0, 250)}${wiki.summary.length > 250 ? '…' : ''}"` : '';
    } else {
      wikiCredEl.textContent = 'No Wikipedia match found';
      wikiCredEl.style.color = 'var(--gray-400)';
      wikiBarEl.style.width  = '50%';
      wikiBarEl.style.background = 'var(--gray-300)';
      wikiMatchEl.textContent = '';
      wikiSumEl.textContent   = '';
    }
  }

  // ── Fact Check ────────────────────────────────────────────
  const fc = r.breakdown?.fact_check;
  if (fc) {
    const factLabelEl  = document.getElementById('factLabel');
    const factSourceEl = document.getElementById('factSource');

    if (fc.found) {
      factLabelEl.textContent  = fc.label || '—';
      const isPositive = fc.label?.toLowerCase().includes('true');
      factLabelEl.style.color  = isPositive ? 'var(--success)' : 'var(--danger)';
      factSourceEl.textContent = fc.source ? `Source: ${fc.source}` : '';
    } else {
      factLabelEl.textContent  = 'No fact-check record found';
      factLabelEl.style.color  = 'var(--gray-400)';
      factSourceEl.textContent = '';
    }
  }

  // ── Knowledge Base ────────────────────────────────────────
  const kb = r.breakdown?.knowledge_base;
  if (kb) {
    const kbMatchEl   = document.getElementById('kbMatch');
    const kbClaimedEl = document.getElementById('kbClaimed');
    const kbActualEl  = document.getElementById('kbActual');

    if (kb.found) {
      if (kb.match) {
        kbMatchEl.textContent = '✔ Claim matches knowledge base';
        kbMatchEl.style.color = 'var(--success)';
      } else {
        kbMatchEl.textContent = '✘ Claim contradicts knowledge base';
        kbMatchEl.style.color = 'var(--danger)';
      }
      kbClaimedEl.textContent = kb.claimed ? `Claimed: "${kb.claimed}"` : '';
      kbActualEl.textContent  = kb.actual  ? `Actual: "${kb.actual}"` : '';
    } else {
      kbMatchEl.textContent   = 'Not found in knowledge base';
      kbMatchEl.style.color   = 'var(--gray-400)';
      kbClaimedEl.textContent = '';
      kbActualEl.textContent  = '';
    }
  }

  card.classList.remove('hidden');
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ══════════════════════════════════════════════════════════
   HISTORY
══════════════════════════════════════════════════════════ */

let historyOffset = 0;
let historyTotal  = 0;

async function loadHistory(offset = 0) {
  hideAlert('historyError');
  const limit = parseInt(document.getElementById('historyLimit').value) || 20;
  historyOffset = offset;

  const loading = document.getElementById('historyLoading');
  const list    = document.getElementById('historyList');
  const empty   = document.getElementById('historyEmpty');
  const pag     = document.getElementById('pagination');

  loading.classList.remove('hidden');
  list.innerHTML = '';
  empty.classList.add('hidden');
  pag.innerHTML  = '';

  try {
    const res  = await fetch(`${API}/analyze/history?limit=${limit}&offset=${offset}`, {
      headers: authHeaders()
    });
    const data = await res.json();

    if (res.status === 401) { handleExpired(); return; }

    loading.classList.add('hidden');

    if (data.status === 200) {
      const records = data.message?.history || [];
      historyTotal  = data.message?.count   || 0;

      if (records.length === 0) {
        empty.classList.remove('hidden');
        return;
      }

      records.forEach(r => list.appendChild(buildHistoryItem(r)));
      buildPagination(limit, offset, records.length);
    } else {
      showAlert('historyError', data.message || 'Failed to load history.');
    }
  } catch {
    loading.classList.add('hidden');
    showAlert('historyError', 'Could not connect to server.');
  }
}

function buildHistoryItem(r) {
  const labelLower = (r.result || r.label || '').toLowerCase();
  let cls, badgeCls, badgeText;

  if (labelLower.includes('fake')) {
    cls = 'fake'; badgeCls = 'badge-fake'; badgeText = 'Fake';
  } else if (labelLower.includes('real') || labelLower.includes('true')) {
    cls = 'real'; badgeCls = 'badge-real'; badgeText = 'Real';
  } else {
    cls = 'uncertain'; badgeCls = 'badge-uncertain'; badgeText = 'Uncertain';
  }

  const conf = r.confidence != null ? `${(r.confidence * 100).toFixed(1)}% confidence` : '';
  const date = (r.Time || r.created_at) ? new Date(r.Time || r.created_at).toLocaleString() : '';
  const text = r.text_preview || r.text || r.input_text || '(no text stored)';

  const div = document.createElement('div');
  div.className = `history-item ${cls}`;
  div.innerHTML = `
    <span class="history-badge ${badgeCls}">${badgeText}</span>
    <div class="history-body">
      <div class="history-text" title="${escHtml(text)}">${escHtml(text)}</div>
      <div class="history-meta">
        ${conf ? `<span><i class="fa-solid fa-chart-simple"></i> ${conf}</span>` : ''}
        ${date ? `<span><i class="fa-regular fa-clock"></i> ${date}</span>` : ''}
      </div>
    </div>`;
  return div;
}

function buildPagination(limit, offset, count) {
  const pag = document.getElementById('pagination');
  if (offset === 0 && count < limit) return; // single page

  if (offset > 0) {
    const prev = document.createElement('button');
    prev.className = 'page-btn';
    prev.innerHTML = '<i class="fa-solid fa-chevron-left"></i> Prev';
    prev.onclick = () => loadHistory(offset - limit);
    pag.appendChild(prev);
  }

  const info = document.createElement('span');
  info.style.cssText = 'font-size:.85rem;color:var(--gray-500);align-self:center;';
  info.textContent = `Showing ${offset + 1}–${offset + count}`;
  pag.appendChild(info);

  if (count === limit) {
    const next = document.createElement('button');
    next.className = 'page-btn';
    next.innerHTML = 'Next <i class="fa-solid fa-chevron-right"></i>';
    next.onclick = () => loadHistory(offset + limit);
    pag.appendChild(next);
  }
}

document.getElementById('historyLimit').addEventListener('change', () => loadHistory(0));
document.getElementById('refreshHistory').addEventListener('click', () => loadHistory(0));

/* ══════════════════════════════════════════════════════════
   PROFILE
══════════════════════════════════════════════════════════ */

async function loadProfile() {
  try {
    const res  = await fetch(`${API}/users/profile`, { headers: authHeaders() });
    const data = await res.json();
    if (res.status === 401) { handleExpired(); return; }
    if (res.ok) {
      document.getElementById('profileName').textContent  = data.name  || '—';
      document.getElementById('profileEmail').textContent = data.email || '—';
      document.getElementById('profileAvatar').textContent =
        (data.name || '?').charAt(0).toUpperCase();
      document.getElementById('newName').value  = data.name  || '';
      document.getElementById('newEmail').value = data.email || '';
    }
  } catch { /* silent */ }
}

/* Change Name */
document.getElementById('changeNameForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideAlert('nameMsg');
  const btn  = document.getElementById('changeNameBtn');
  const name = document.getElementById('newName').value.trim();
  if (!name) { showAlert('nameMsg', 'Name cannot be empty.'); return; }

  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/users/profile/change_name`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ new_name: name })
    });
    const data = await res.json();
    if (res.status === 401) { handleExpired(); return; }
    if (data.status === 200) {
      showAlert('nameMsg', 'Name updated successfully!', 'alert-success');
      document.getElementById('profileName').textContent = name;
      document.getElementById('profileAvatar').textContent = name.charAt(0).toUpperCase();
      showToast('Name updated', 'success');
    } else {
      showAlert('nameMsg', data.message || 'Failed to update name.');
    }
  } catch {
    showAlert('nameMsg', 'Could not connect to server.');
  } finally {
    setLoading(btn, false);
  }
});

/* Change Email */
document.getElementById('changeEmailForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideAlert('emailMsg');
  const btn   = document.getElementById('changeEmailBtn');
  const email = document.getElementById('newEmail').value.trim();
  if (!email) { showAlert('emailMsg', 'Email cannot be empty.'); return; }

  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/users/profile`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ new_email: email })
    });
    const data = await res.json();
    if (res.status === 401) { handleExpired(); return; }
    if (data.status === 200) {
      showAlert('emailMsg', 'Email updated! Please log in again.', 'alert-success');
      document.getElementById('changeEmailForm').reset();
      showToast('Session expired. Please log in again.', 'error');
      setTimeout(() => {
        clearToken();
        updateNav();
        navigate('login');
      }, 2000);
    } else {
      showAlert('emailMsg', data.message || 'Failed to update email.');
    }
  } catch {
    showAlert('emailMsg', 'Could not connect to server.');
  } finally {
    setLoading(btn, false);
  }
});

/* Change Password */
document.getElementById('changePasswordForm').addEventListener('submit', async e => {
  e.preventDefault();
  hideAlert('passwordMsg');
  const btn  = document.getElementById('changePasswordBtn');
  const old  = document.getElementById('oldPassword').value;
  const nw   = document.getElementById('newPassword').value;
  const conf = document.getElementById('confirmNewPassword').value;

  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/users/profile/change_password`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ old_password: old, new_password: nw, confirm_new_password: conf })
    });
    const data = await res.json();
    if (res.status === 401) { handleExpired(); return; }
    if (data.status === 200) {
      showAlert('passwordMsg', 'Password changed! Please log in again with your new password.', 'alert-success');
      document.getElementById('changePasswordForm').reset();
      showToast('Session expired. Please log in again.', 'error');
      setTimeout(() => {
        clearToken();
        updateNav();
        navigate('login');
      }, 2000);
    } else {
      showAlert('passwordMsg', data.message || 'Failed to change password.');
    }
  } catch {
    showAlert('passwordMsg', 'Could not connect to server.');
  } finally {
    setLoading(btn, false);
  }
});

/* Delete Account */
document.getElementById('deleteAccountBtn').addEventListener('click', () => {
  document.getElementById('deleteModal').classList.remove('hidden');
});
document.getElementById('cancelDelete').addEventListener('click', () => {
  document.getElementById('deleteModal').classList.add('hidden');
});
document.getElementById('deleteModal').addEventListener('click', e => {
  if (e.target === document.getElementById('deleteModal'))
    document.getElementById('deleteModal').classList.add('hidden');
});

document.getElementById('confirmDelete').addEventListener('click', async () => {
  const btn = document.getElementById('confirmDelete');
  setLoading(btn, true);
  try {
    const res  = await fetch(`${API}/users/profile/Delete`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    const data = await res.json();
    if (data.status === 200) {
      clearToken();
      updateNav();
      document.getElementById('deleteModal').classList.add('hidden');
      showToast('Account deleted', 'error');
      navigate('login');
    } else {
      showAlert('deleteMsg', data.message || 'Failed to delete account.');
      document.getElementById('deleteModal').classList.add('hidden');
    }
  } catch {
    showAlert('deleteMsg', 'Could not connect to server.');
    document.getElementById('deleteModal').classList.add('hidden');
  } finally {
    setLoading(btn, false);
  }
});

/* ══════════════════════════════════════════════════════════
   SESSION EXPIRED HANDLER
══════════════════════════════════════════════════════════ */
function handleExpired() {
  clearToken();
  updateNav();
  showToast('Session expired. Please log in again.', 'error');
  navigate('login');
}

/* ══════════════════════════════════════════════════════════
   UTILS
══════════════════════════════════════════════════════════ */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ══════════════════════════════════════════════════════════
   INIT
══════════════════════════════════════════════════════════ */
updateNav();
navigate(isLoggedIn() ? 'analyze' : 'login');
