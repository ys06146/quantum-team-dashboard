(() => {
  const today = new Date();
  const start = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  document.querySelectorAll('[data-deadline]').forEach(cell => {
    const [y, m, d] = cell.dataset.deadline.split('-').map(Number);
    if (!y || !m || !d) return;
    const days = Math.round((Date.UTC(y, m - 1, d) - start) / 86400000);
    cell.textContent = days > 0 ? `D-${days}` : days === 0 ? '오늘' : '지남';
  });
})();
