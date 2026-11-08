(() => {
  const root=document.getElementById('quantum-team-plan');
  if(!root) return;
  const buttons=[...root.querySelectorAll('[data-task]')];
  const tabs=[...root.querySelectorAll('[role="tab"]')];
  const fields=['q-detail-title','q-reviewer','q-detail-work','q-detail-output','q-detail-done','q-detail-handoff'];
  let task='s1',panel='q-roadmap';
  function selectTask(id){
    if(!Object.hasOwn(PLAN_TASKS,id)) return;
    task=id;
    fields.forEach((field,i)=>root.querySelector('#'+field).textContent=i===1?'검토: '+PLAN_TASKS[id][i]:PLAN_TASKS[id][i]);
    buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.task===id)));
  }
  function selectPanel(id){
    if(!tabs.some(t=>t.getAttribute('aria-controls')===id))return;
    panel=id;
    tabs.forEach(t=>{
      const active=t.getAttribute('aria-controls')===id;
      t.classList.toggle('active',active);t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;
      root.querySelector('#'+t.getAttribute('aria-controls')).hidden=!active;
    });
  }
  function save(){try{localStorage.setItem('quantum-team-plan-v1',JSON.stringify({task,panel}));}catch{}}
  buttons.forEach(b=>b.addEventListener('click',()=>{selectTask(b.dataset.task);save();}));
  tabs.forEach((tab,i)=>{
    tab.addEventListener('click',()=>{selectPanel(tab.getAttribute('aria-controls'));save();});
    tab.addEventListener('keydown',event=>{
      let next;
      if(event.key==='ArrowRight')next=(i+1)%tabs.length;
      if(event.key==='ArrowLeft')next=(i-1+tabs.length)%tabs.length;
      if(event.key==='Home')next=0;
      if(event.key==='End')next=tabs.length-1;
      if(next!==undefined){event.preventDefault();tabs[next].focus();selectPanel(tabs[next].getAttribute('aria-controls'));save();}
    });
  });
  try{const stored=JSON.parse(localStorage.getItem('quantum-team-plan-v1'));if(stored){selectTask(stored.task);selectPanel(stored.panel);}}catch{}
  if(location.hash==='#seohee')selectPanel('q-chemistry');
  else selectPanel(panel);
})();
