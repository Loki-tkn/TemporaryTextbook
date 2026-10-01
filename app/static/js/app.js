// TemporaryTextbook Client Application Scripts

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Tab navigation for Admin & Student
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.toggle('active', content.id === tabId);
  });
}

// Modal helper
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

// Format input code automatically as XXXX-XXXX
function setupCodeInputFormatter(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener('input', (e) => {
    let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (val.length > 4) {
      val = val.slice(0, 4) + '-' + val.slice(4, 8);
    }
    e.target.value = val;
  });
}

// ----------------------------------------------------
// STUDENT PORTAL FUNCTIONS
// ----------------------------------------------------

async function submitStudentRequest(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = 'Submitting...';

  const payload = {
    student_name: form.student_name.value.trim(),
    student_id: form.student_id.value.trim(),
    class_grade: form.class_grade.value.trim(),
    subject: form.subject.value.trim(),
    textbook_title: form.textbook_title.value.trim() || null,
    reason: form.reason.value.trim() || null
  };

  try {
    const res = await fetch('/api/requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Submission failed');

    showToast('Request submitted successfully! Tracking ID: #' + data.id, 'success');
    form.reset();
    
    // Auto-fill student ID search and query status
    const searchInput = document.getElementById('search-student-id');
    if (searchInput) {
      searchInput.value = payload.student_id;
      lookupStudentStatus();
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

async function lookupStudentStatus() {
  const searchInput = document.getElementById('search-student-id');
  if (!searchInput) return;
  const query = searchInput.value.trim();
  if (!query) {
    showToast('Please enter your Student ID or Name', 'error');
    return;
  }

  const resultsDiv = document.getElementById('student-status-results');
  resultsDiv.innerHTML = '<p class="text-muted" style="padding: 1rem; text-align: center;">Searching records...</p>';

  try {
    const res = await fetch(`/api/student/status?query=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!data.requests || data.requests.length === 0) {
      resultsDiv.innerHTML = `
        <div style="padding: 1.5rem; text-align: center; color: var(--text-muted);">
          <p>No textbook requests found for <strong>"${query}"</strong>.</p>
          <p style="font-size: 0.85rem; margin-top: 0.5rem;">Please check your Student ID or submit a new request above.</p>
        </div>`;
      return;
    }

    let html = '<div class="grid" style="gap: 1rem; margin-top: 1rem;">';
    data.requests.forEach(req => {
      const statusClass = req.status === 'Approved' ? 'badge-approved' : req.status === 'Rejected' ? 'badge-rejected' : 'badge-pending';
      let codeBoxHtml = '';
      if (req.status === 'Approved' && req.access_code) {
        codeBoxHtml = `
          <div style="margin-top: 0.75rem; padding: 0.75rem 1rem; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px;">
            <div style="font-size: 0.8rem; color: #166534; font-weight: 600; text-transform: uppercase;">Your Temporary Access Code</div>
            <div style="font-family: monospace; font-size: 1.3rem; font-weight: 700; color: #15803d; letter-spacing: 2px; margin: 0.25rem 0;">
              ${req.access_code}
            </div>
            <div style="font-size: 0.8rem; color: #166534;">
              Valid until: <strong>${new Date(req.expires_at).toLocaleDateString()} ${new Date(req.expires_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</strong>
            </div>
            <button class="btn btn-sm btn-success" style="margin-top: 0.5rem;" onclick="applyAndVerifyCode('${req.access_code}')">
              ⚡ Use Code Now to Unlock Materials
            </button>
          </div>
        `;
      } else if (req.status === 'Pending') {
        codeBoxHtml = `<div style="margin-top: 0.5rem; font-size: 0.85rem; color: #b45309;">⏳ Waiting for teacher/admin approval. Please check back shortly.</div>`;
      } else if (req.status === 'Rejected') {
        codeBoxHtml = `<div style="margin-top: 0.5rem; font-size: 0.85rem; color: #b91c1c;">Note: ${req.admin_note || 'Request not approved.'}</div>`;
      }

      html += `
        <div class="card" style="border-left: 4px solid ${req.status === 'Approved' ? '#10b981' : req.status === 'Pending' ? '#f59e0b' : '#ef4444'};">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div>
              <strong style="font-size: 1.05rem;">${req.subject}</strong>
              <div style="font-size: 0.85rem; color: var(--text-muted);">${req.class_grade} • Request #${req.id}</div>
            </div>
            <span class="badge ${statusClass}">${req.status}</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
            Textbook: <em>${req.textbook_title || 'General Subject Materials'}</em>
          </p>
          ${req.reason ? `<p style="font-size: 0.85rem; color: #475569;">Reason: ${req.reason}</p>` : ''}
          ${codeBoxHtml}
        </div>
      `;
    });
    html += '</div>';
    resultsDiv.innerHTML = html;
  } catch (err) {
    resultsDiv.innerHTML = `<div style="color: var(--danger); padding: 1rem;">Failed to fetch status: ${err.message}</div>`;
  }
}

function applyAndVerifyCode(code) {
  const codeInput = document.getElementById('student-access-code');
  if (codeInput) {
    codeInput.value = code;
    document.getElementById('code-unlock-section')?.scrollIntoView({ behavior: 'smooth' });
    verifyAccessCode();
  }
}

async function verifyAccessCode() {
  const input = document.getElementById('student-access-code');
  if (!input) return;
  const code = input.value.trim().toUpperCase();
  if (!code) {
    showToast('Please enter an access code', 'error');
    return;
  }

  const container = document.getElementById('unlocked-materials-container');
  const msgBox = document.getElementById('code-feedback-msg');
  container.innerHTML = '';
  msgBox.innerHTML = '<span style="color: var(--text-muted);">Verifying code...</span>';

  try {
    const res = await fetch('/api/codes/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });

    const data = await res.json();

    if (!data.valid) {
      msgBox.innerHTML = `
        <div style="background: var(--danger-bg); border: 1px solid #fca5a5; color: #991b1b; padding: 0.85rem; border-radius: var(--radius-md); text-align: center; margin-top: 1rem;">
          <strong>Access Denied:</strong> ${data.message}
          ${data.status ? `<div style="font-size: 0.8rem; margin-top: 0.25rem;">Status: <span class="badge badge-${data.status.toLowerCase()}">${data.status}</span></div>` : ''}
        </div>`;
      showToast(data.message, 'error');
      return;
    }

    // Valid code!
    showToast(`Access granted for ${data.subject}!`, 'success');
    msgBox.innerHTML = `
      <div style="background: var(--success-bg); border: 1px solid #a7f3d0; color: #065f46; padding: 0.85rem; border-radius: var(--radius-md); text-align: center; margin-top: 1rem;">
        <div style="font-weight: 600; font-size: 1rem;">✓ Authorized Temporary Access Active</div>
        <div style="font-size: 0.85rem; margin-top: 0.25rem;">
          Student: <strong>${data.student_name} (${data.student_id})</strong> | Subject: <strong>${data.subject}</strong>
        </div>
        <div style="font-size: 0.8rem; margin-top: 0.25rem; color: #047857;">
          Valid until: <strong>${new Date(data.expires_at).toLocaleString()}</strong>
        </div>
      </div>
    `;

    // Render materials
    if (!data.materials || data.materials.length === 0) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 2.5rem; margin-top: 1.5rem;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
          <h3>No materials uploaded yet for ${data.subject}</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem;">
            Your teacher is preparing authorized summaries and exercises. Please check back soon.
          </p>
        </div>
      `;
      return;
    }

    let matHtml = `
      <div style="margin-top: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-size: 1.25rem;">Authorized Materials (${data.materials.length})</h3>
          <span class="badge badge-active">${data.subject}</span>
        </div>
        <div class="grid grid-2">
    `;

    data.materials.forEach(m => {
      matHtml += `
        <div class="material-card">
          <div>
            <div class="material-header">
              <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                <div class="material-icon">📄</div>
                <div>
                  <h4 style="font-size: 1.05rem; margin-bottom: 0.2rem;">${m.title}</h4>
                  <span class="badge badge-subject">${m.file_type} • ${m.file_size_kb} KB</span>
                </div>
              </div>
            </div>
            <p style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.75rem;">
              ${m.description || 'Authorized temporary course resource.'}
            </p>
            <div style="margin-top: 0.75rem; font-size: 0.75rem; color: #64748b; background: #f8fafc; padding: 0.4rem 0.6rem; border-radius: 4px;">
              <strong>Instructor/Author:</strong> ${m.author}<br>
              <strong>License:</strong> ${m.license_type}
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
            <a href="/api/materials/${m.id}/download?code=${code}" class="btn btn-primary btn-sm" style="flex: 1;" target="_blank" download>
              ⬇ Download File
            </a>
            <a href="/api/materials/${m.id}/view?code=${code}" class="btn btn-secondary btn-sm" style="flex: 1;" target="_blank">
              👁 View Online
            </a>
          </div>
        </div>
      `;
    });

    matHtml += '</div></div>';
    container.innerHTML = matHtml;

  } catch (err) {
    msgBox.innerHTML = `<div style="color: var(--danger); text-align: center; margin-top: 0.5rem;">Verification error: ${err.message}</div>`;
  }
}


// ----------------------------------------------------
// ADMIN DASHBOARD FUNCTIONS
// ----------------------------------------------------

let currentApproveRequestId = null;

function openApproveModal(requestId, studentName, subject) {
  currentApproveRequestId = requestId;
  document.getElementById('approve-req-id').value = requestId;
  document.getElementById('approve-modal-student').innerText = studentName;
  document.getElementById('approve-modal-subject').innerText = subject;
  openModal('approveModal');
}

async function submitApproveRequest(e) {
  e.preventDefault();
  const form = e.target;
  const requestId = parseInt(form.request_id.value);
  const durationDays = parseInt(form.duration_days.value);
  const adminNote = form.admin_note.value.trim() || null;

  try {
    const res = await fetch('/api/admin/requests/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: requestId,
        duration_days: durationDays,
        admin_note: adminNote
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Approval failed');

    showToast(`Request #${requestId} approved! Code: ${data.code}`, 'success');
    closeModal('approveModal');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function rejectRequest(requestId) {
  const reason = prompt('Enter rejection reason (optional):');
  if (reason === null) return; // cancelled

  try {
    const res = await fetch('/api/admin/requests/reject', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: requestId,
        admin_note: reason || 'Not approved by instructor.'
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Rejection failed');

    showToast(`Request #${requestId} marked as Rejected.`, 'info');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function revokeAccessCode(code) {
  const reason = prompt(`Are you sure you want to revoke access code ${code}?\nEnter reason:`, 'Textbook arrived / access finished');
  if (reason === null) return;

  try {
    const res = await fetch('/api/admin/codes/revoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: code,
        reason: reason
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Revocation failed');

    showToast(`Access code ${code} revoked!`, 'warning');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function extendAccessCode(code) {
  const daysStr = prompt(`Extend expiration for code ${code}.\nHow many additional days?`, '7');
  if (!daysStr) return;
  const days = parseInt(daysStr);
  if (isNaN(days) || days <= 0) {
    showToast('Invalid number of days', 'error');
    return;
  }

  try {
    const res = await fetch('/api/admin/codes/extend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: code,
        additional_days: days
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Extension failed');

    showToast(`Code ${code} extended by ${days} days!`, 'success');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function uploadMaterial(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const submitBtn = form.querySelector('button[type="submit"]');
  const orig = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = 'Uploading...';

  try {
    const res = await fetch('/api/admin/materials/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');

    showToast(`Material "${data.title}" uploaded successfully!`, 'success');
    form.reset();
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = orig;
  }
}

async function deleteMaterial(materialId, title) {
  if (!confirm(`Are you sure you want to delete material "${title}"?`)) return;

  try {
    const res = await fetch(`/api/admin/materials/${materialId}`, {
      method: 'DELETE'
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Delete failed');

    showToast('Material deleted', 'info');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function resetDemoData() {
  if (!confirm('Reset and re-seed the system with fresh sample data?')) return;

  try {
    const res = await fetch('/api/admin/seed-demo', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Reset failed');
    showToast('Demo data successfully re-seeded!', 'success');
    setTimeout(() => window.location.reload(), 800);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Auto init on page load
document.addEventListener('DOMContentLoaded', () => {
  setupCodeInputFormatter('student-access-code');
});
