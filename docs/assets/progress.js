(() => {
  const tabs = [...document.querySelectorAll('[data-progress-tab]')];
  const panels = [...document.querySelectorAll('[data-progress-panel]')];
  if (!tabs.length) return;
  const list = document.querySelector('.progress-tabs');
  list.setAttribute('role', 'tablist');
  tabs.forEach(tab => tab.setAttribute('role', 'tab'));
  panels.forEach(panel => panel.setAttribute('role', 'tabpanel'));
  function choose(week, focus = false) {
    tabs.forEach(tab => {
      const selected = tab.dataset.progressTab === String(week);
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && focus) tab.focus();
    });
    panels.forEach(panel => panel.hidden = panel.dataset.progressPanel !== String(week));
  }
  function openHash() {
    const match = location.hash.match(/^#check-([a-z]+)-([123])$/);
    if (!match) return false;
    const detail = document.getElementById(`check-${match[1]}-${match[2]}`);
    if (!detail) return false;
    choose(match[2]);
    detail.open = true;
    requestAnimationFrame(() => detail.scrollIntoView({block:'start'}));
    return true;
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => choose(tab.dataset.progressTab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); choose(tabs[next].dataset.progressTab, true); }
    });
  });
  document.querySelectorAll('[data-progress-person]').forEach(link => {
    link.addEventListener('click', () => {
      choose(link.dataset.progressWeek);
      const detail = document.getElementById(link.hash.slice(1));
      detail.open = true;
      requestAnimationFrame(() => { detail.scrollIntoView({block:'start'}); detail.querySelector('summary').focus({preventScroll:true}); });
    });
  });
  window.addEventListener('hashchange', openHash);
  if (!openHash()) choose('1');
})();
