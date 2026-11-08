(() => {
  const toggle=document.querySelector('.menu-button');
  const sidebar=document.querySelector('.sidebar');
  if(toggle&&sidebar) toggle.addEventListener('click',()=>{
    const open=sidebar.classList.toggle('menu-open');
    toggle.setAttribute('aria-expanded',String(open));
    toggle.textContent=open?'닫기':'메뉴';
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&sidebar?.classList.contains('menu-open')){
      sidebar.classList.remove('menu-open');toggle.setAttribute('aria-expanded','false');toggle.textContent='메뉴';toggle.focus();
    }
  });
})();
