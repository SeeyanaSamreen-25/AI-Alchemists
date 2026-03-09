/**
 * StyleSense — Main JavaScript
 * Global utilities and enhancements
 */

// ── PAGE LOAD ANIMATION ──
document.addEventListener('DOMContentLoaded', function () {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.3s ease';
  requestAnimationFrame(() => {
    document.body.style.opacity = '1';
  });

  // Animate stat bars on dashboard
  document.querySelectorAll('.sc-bar div').forEach(bar => {
    const w = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = w; }, 300);
  });

  // Animate trend bars
  document.querySelectorAll('.tp-bar div, .tc-bar div').forEach(bar => {
    const w = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = w; }, 400);
  });
});

// ── TOAST NOTIFICATION ──
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: ${type === 'success' ? 'rgba(92,184,122,0.15)' : 'rgba(224,85,85,0.15)'};
    border: 1px solid ${type === 'success' ? 'rgba(92,184,122,0.3)' : 'rgba(224,85,85,0.3)'};
    color: ${type === 'success' ? '#4ade80' : '#f87171'};
    padding: 12px 20px; border-radius: 8px;
    font-size: 0.85rem; font-family: 'DM Sans', sans-serif;
    backdrop-filter: blur(8px);
    animation: slideInRight 0.3s ease;
  `;

  const style = document.createElement('style');
  style.textContent = `@keyframes slideInRight { from { opacity:0; transform: translateX(20px); } to { opacity:1; transform: translateX(0); } }`;
  document.head.appendChild(style);

  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3000);
}
