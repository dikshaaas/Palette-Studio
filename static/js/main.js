/**
 * main.js — Palette Studio Workspace
 * Handles theme, upload drag-drop, favoriting, deletion, toast notifications, and tabs.
 */

// ── Theme ────────────────────────────────────────────────────────────────────
const root        = document.documentElement;
const themeToggle = document.getElementById('theme-toggle');

const ICON_MOON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 14.5A8.5 8.5 0 1 1 9.5 3a7 7 0 0 0 11.5 11.5z"/></svg>`;
const ICON_SUN  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>`;

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
  const icon  = document.getElementById('theme-icon');
  const label = document.getElementById('theme-label');
  if (icon)  icon.innerHTML = theme === 'light' ? ICON_MOON : ICON_SUN;
  if (label) label.textContent = theme === 'light' ? 'Dark Mode' : 'Light Mode';
}

function initTheme() {
  const saved = localStorage.getItem('ps-theme') || 'light';
  applyTheme(saved);
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') || 'light';
    const next    = current === 'light' ? 'dark' : 'light';
    localStorage.setItem('ps-theme', next);
    applyTheme(next);
  });
}

initTheme();

// ── Toast ────────────────────────────────────────────────────────────────────
const toast = document.getElementById('toast');
let toastTimer;

function showToast(msg = 'Copied!') {
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
}

// ── Drag & Drop Upload ───────────────────────────────────────────────────────
const uploadZone       = document.getElementById('upload-zone');
const fileInput        = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const previewImg       = document.getElementById('preview-img');
const removePreview    = document.getElementById('remove-preview');
const uploadForm       = document.getElementById('upload-form');
const submitBtn        = document.getElementById('submit-btn');
const slider           = document.getElementById('n-colors');
const sliderVal        = document.getElementById('slider-val');

if (uploadZone) {
  uploadZone.addEventListener('click', () => fileInput && fileInput.click());

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    uploadZone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    document.body.addEventListener(evt, e => { e.preventDefault(); });
  });

  uploadZone.addEventListener('dragenter', () => uploadZone.classList.add('dragover'));
  uploadZone.addEventListener('dragover',  () => uploadZone.classList.add('dragover'));
  uploadZone.addEventListener('dragleave', (e) => {
    if (!uploadZone.contains(e.relatedTarget)) uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', (e) => {
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
  });
}

if (fileInput) {
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
  });
}

function handleFile(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!allowed.includes(file.type)) {
    showToast('Only JPG, JPEG, and PNG files allowed');
    return;
  }
  if (file.size > 16 * 1024 * 1024) {
    showToast('File size exceeds 16 MB');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    if (previewImg)        previewImg.src = e.target.result;
    if (previewContainer)  previewContainer.style.display = 'block';
    if (uploadZone)        uploadZone.style.display = 'none';
  };
  reader.readAsDataURL(file);

  const dt = new DataTransfer();
  dt.items.add(file);
  if (fileInput) fileInput.files = dt.files;
}

if (removePreview) {
  removePreview.addEventListener('click', () => {
    if (previewImg)        previewImg.src = '';
    if (previewContainer)  previewContainer.style.display = 'none';
    if (uploadZone)        uploadZone.style.display = 'block';
    if (fileInput)         fileInput.value = '';
  });
}

if (slider && sliderVal) {
  sliderVal.textContent = slider.value;
  slider.addEventListener('input', () => { sliderVal.textContent = slider.value; });
}

if (uploadForm && submitBtn) {
  uploadForm.addEventListener('submit', (e) => {
    if (!fileInput || !fileInput.files.length) {
      e.preventDefault();
      showToast('Please select an image file first');
      return;
    }
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
  });
}

// ── Copy Colors ──────────────────────────────────────────────────────────────
document.querySelectorAll('.copy-icon-btn, .swatch-row, .harmony-block').forEach(elem => {
  elem.addEventListener('click', async (e) => {
    e.stopPropagation();
    const hex = elem.dataset.hex;
    if (!hex) return;
    try {
      await navigator.clipboard.writeText(hex);
      showToast(`Copied ${hex}`);
    } catch {
      showToast('Copy failed');
    }
  });
});

// Copy All Colors Button
const copyAllBtn = document.getElementById('copy-all-btn');
if (copyAllBtn) {
  copyAllBtn.addEventListener('click', async () => {
    const hexes = Array.from(document.querySelectorAll('.swatch-row')).map(el => el.dataset.hex);
    if (!hexes.length) return;
    try {
      await navigator.clipboard.writeText(hexes.join(', '));
      showToast(`Copied ${hexes.length} colors`);
    } catch {
      showToast('Copy failed');
    }
  });
}

// ── Favoriting AJAX ──────────────────────────────────────────────────────────
document.querySelectorAll('.heart-badge, .fav-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const paletteId = btn.dataset.id;
    if (!paletteId) return;

    try {
      const res = await fetch('/api/favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: paletteId })
      });
      const data = await res.json();
      if (data.success) {
        if (data.is_favorite) {
          btn.classList.add('active');
          showToast('Added to favorites');
        } else {
          btn.classList.remove('active');
          showToast('Removed from favorites');
        }
      }
    } catch (err) {
      showToast('Action failed');
    }
  });
});

// ── Deleting Palette AJAX ────────────────────────────────────────────────────
const deleteBtn = document.getElementById('delete-palette-btn');
if (deleteBtn) {
  deleteBtn.addEventListener('click', async () => {
    const paletteId = deleteBtn.dataset.id;
    if (!paletteId || !confirm('Are you sure you want to delete this palette?')) return;

    try {
      const res = await fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: paletteId })
      });
      const data = await res.json();
      if (data.success) {
        showToast('Palette deleted');
        setTimeout(() => { window.location.href = '/library'; }, 600);
      }
    } catch {
      showToast('Delete failed');
    }
  });
}

// Clear All History AJAX
const clearBtn = document.getElementById('clear-history-btn');
if (clearBtn) {
  clearBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to clear all palette history?')) return;
    try {
      const res = await fetch('/api/clear', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast('History cleared');
        setTimeout(() => { window.location.reload(); }, 600);
      }
    } catch {
      showToast('Action failed');
    }
  });
}

// ── Export Code Tabs ─────────────────────────────────────────────────────────
const tabBtns = document.querySelectorAll('.tab-btn');
const codeBox = document.getElementById('code-output');

if (tabBtns.length && codeBox) {
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const targetElem = document.getElementById(btn.dataset.target);
      if (targetElem) codeBox.textContent = targetElem.textContent.trim();
    });
  });
}

const copyCodeBtn = document.getElementById('copy-code-btn');
if (copyCodeBtn && codeBox) {
  copyCodeBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(codeBox.textContent);
      showToast('Copied code snippet!');
    } catch {
      showToast('Failed to copy code');
    }
  });
}

// ── Animations on Load ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pct-bar-fg').forEach(bar => {
    const target = bar.dataset.percent + '%';
    setTimeout(() => { bar.style.width = target; }, 100);
  });
  document.querySelectorAll('.swatch-strip-seg').forEach(seg => {
    const pct = parseFloat(seg.dataset.percent) || 10;
    seg.style.flex = pct.toString();
  });
});
