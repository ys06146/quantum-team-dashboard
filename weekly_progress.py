"""Render shared weekly completion from the existing plan and explicit checklist state."""
from pathlib import Path
from html import escape
import json
import re
import shutil

CHECKPOINTS = [('work','작업 수행',2),('output','산출물 준비',3),('validation','완료 기준 확인',4),('handoff','검토·전달',5)]
PREFIX = {'소연':'s','지우':'j','예찬':'y','서진':'e','서희':'c'}
VALID = {key for key, _, _ in CHECKPOINTS}

def completion(completed):
    if not isinstance(completed,list) or any(not isinstance(v,str) for v in completed):
        raise ValueError('Completion must be a list of checkpoint names')
    if len(completed)!=len(set(completed)) or not set(completed)<=VALID:
        raise ValueError('Unknown or duplicate completion checkpoint')
    return {'done':len(completed),'total':len(CHECKPOINTS),'percent':len(completed)*100//len(CHECKPOINTS)}

def validate_data(data,tasks,people):
    if data.get('schema_version') != 1:raise ValueError('Unsupported progress schema')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',data.get('updated_at','')):raise ValueError('Missing progress update date')
    expected={PREFIX[p[1]]+str(w) for p in people for w in range(1,4)}
    if set(data.get('tasks',{}))!=expected:raise ValueError('Progress must cover all 5 people and all 3 weeks')
    for slug,name,*_ in people:
        for week in range(1,4):
            key=PREFIX[name]+str(week)
            if key not in tasks or len(tasks[key])!=6:raise ValueError('Missing plan task: '+key)
            if not tasks[key][0].startswith(f'{name} · {week}주차'):raise ValueError('Plan owner/week mismatch: '+key)
            completion(data['tasks'][key].get('completed'))

def bar(percent,label,extra=''):
    return f'<div class="progress-track {extra}" role="progressbar" aria-label="{escape(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percent}"><span style="width:{percent}%"></span></div>'

def build_progress(root,out,page,people,summary):
    data=json.loads((root/'content/progress.json').read_text(encoding='utf-8'))
    tasks=json.loads((root/'content/tasks.json').read_text(encoding='utf-8'))
    validate_data(data,tasks,people)
    states={key:completion(row['completed']) for key,row in data['tasks'].items()}
    total=sum(x['total'] for x in states.values());done=sum(x['done'] for x in states.values())
    overall=round(100*done/total)
    phases=summary['phases']
    week_stats={w:{'done':sum(states[PREFIX[p[1]]+str(w)]['done'] for p in people),'total':len(people)*4} for w in range(1,4)}
    for row in week_stats.values():row['percent']=round(100*row['done']/row['total'])
    body=f'''<header class="progress-heading"><div><span class="eyebrow">WEEKLY PROGRESS</span><h1>주차별 진행도</h1><p>누가, 어느 주차에, 어디까지 했는지 함께 확인해요.</p></div><p class="progress-updated">진행도 갱신 <time datetime="{data['updated_at']}">{data['updated_at'].replace('-','.')}</time></p></header>
<section class="progress-overview" aria-labelledby="overall-title"><div><span class="eyebrow">전체 3주</span><h2 id="overall-title">함께 채워 가는 진행률</h2><p>5명 × 3주 × 4개 확인 항목</p></div><div class="overall-stat"><strong>{overall}<span>%</span></strong><p>{done} / {total}개 완료</p>{bar(overall,'3주 전체 진행률')}</div></section>
<p class="progress-start">{data['initialized_at'].replace('-','.')} 기록 시작 · 전원 0%에서 시작한 새 체크리스트입니다.</p>
<section class="progress-section" aria-labelledby="matrix-title"><div class="section-title"><div><h2 id="matrix-title">팀원별 주차 진행률</h2><p>퍼센트를 누르면 해당 주차의 과제를 볼 수 있어요.</p></div><span class="progress-count">5명 · 3주</span></div><div class="progress-matrix-wrap"><table class="progress-matrix"><caption class="sr-only">팀원 5명의 1·2·3주차 완료율</caption><thead><tr><th scope="col">팀원</th>'''
    for w,phase in enumerate(phases,1):
        dates=phase['label'].split('·')[-1].strip()
        body+=f'<th scope="col"><strong>{w}주차</strong><span>{escape(dates)}</span><small>{escape(phase["title"])}</small></th>'
    body+='</tr></thead><tbody>'
    for slug,name,role,*_ in people:
        body+=f'<tr><th scope="row"><span class="progress-person"><span class="avatar" aria-hidden="true">{name[-1]}</span><span><strong>{name}</strong><small>{escape(role)}</small></span></span></th>'
        for w in range(1,4):
            st=states[PREFIX[name]+str(w)]
            body+=f'<td><a class="progress-cell" href="#check-{slug}-{w}" data-progress-person="{slug}" data-progress-week="{w}" aria-label="{name} {w}주차 {st["percent"]}% 완료, 과제 보기"><span class="cell-value">{st["percent"]}<small>%</small></span>{bar(st["percent"],f"{name} {w}주차 진행률")}<span class="cell-count">{st["done"]} / {st["total"]} 완료</span></a></td>'
        body+='</tr>'
    body+='</tbody></table></div></section><section class="progress-section" id="weekly-checklists" aria-labelledby="checklist-title"><div class="section-title"><div><h2 id="checklist-title">주차별 체크리스트</h2><p>개인별 기존 계획의 작업·산출물·완료 기준·전달 항목을 연결했어요.</p></div></div><div class="progress-tabs" aria-label="체크리스트 주차 선택">'
    for w,phase in enumerate(phases,1):
        st=week_stats[w]
        body+=f'<button type="button" id="week-tab-{w}" data-progress-tab="{w}" aria-controls="week-panel-{w}"><strong>{w}주차</strong><span>{escape(phase["title"])}</span><b>{st["percent"]}%</b></button>'
    body+='</div>'
    for w,phase in enumerate(phases,1):
        st=week_stats[w]
        body+=f'<section class="progress-week-panel" id="week-panel-{w}" data-progress-panel="{w}" aria-labelledby="week-tab-{w}"><div class="week-panel-heading"><div><h3>{w}주차 · {escape(phase["title"])}</h3><p>{escape(phase["detail"])} · {escape(phase["label"].split("·")[-1].strip())}</p></div><span>{st["done"]} / {st["total"]}개 완료</span></div>'
        for slug,name,role,*_ in people:
            key=PREFIX[name]+str(w);task=tasks[key];current=states[key];completed=set(data['tasks'][key]['completed'])
            task_title=task[0].split('—',1)[-1].strip()
            body+=f'<details class="progress-details" id="check-{slug}-{w}"><summary><span class="progress-person"><span class="avatar" aria-hidden="true">{name[-1]}</span><span><strong>{name}</strong><small>{escape(task_title)}</small></span></span><span class="progress-detail-score">{current["percent"]}%<small>{current["done"]} / 4 완료</small></span><span class="details-chevron" aria-hidden="true">⌄</span></summary><div class="progress-detail-body"><ol class="progress-checks">'
            for cp,title,index in CHECKPOINTS:
                complete=cp in completed;state='완료' if complete else '미체크'
                body+=f'<li class="{"is-done" if complete else "is-pending"}" data-checkpoint="{cp}" data-status="{"done" if complete else "pending"}"><span class="check-icon" aria-hidden="true">{"✓" if complete else ""}</span><div><div class="check-heading"><strong>{title}</strong><span>{state}</span></div><p>{escape(task[index])}</p></div></li>'
            body+=f'</ol><div class="progress-detail-footer"><span>검토 연결 · {escape(task[1])}</span><a href="guides/{slug}.html">{name} 가이드 보기 ↗</a></div></div></details>'
        body+='</section>'
    body+='''</section><details class="progress-method"><summary>진행률은 어떻게 계산하나요?</summary><p>주차별 완료율 = 완료한 확인 항목 ÷ 4 × 100입니다. 항목 하나당 25%이며, 주차 전체와 3주 전체도 완료 항목 수로 계산합니다.</p><p>이 보드는 공유된 진행 기록을 보여줍니다. 완료 항목을 기록에 반영하면 다음 갱신에 퍼센트가 함께 바뀝니다. 각 항목의 난이도나 투입 시간을 점수로 매기는 방식은 아닙니다.</p><p>사용자 요청에 따라 새 보드의 모든 항목을 미체크로 시작했습니다. 기존 실험 결과와 제출 점수는 <a href="week1.html">1주차 작업 결과</a>에서 확인할 수 있어요.</p></details>'''
    extra='<link rel="stylesheet" href="assets/progress.css"><script src="assets/progress.js" defer></script>'
    (out/'progress.html').write_text(page('주차별 진행도','progress',body,extra_script=extra),encoding='utf-8')
    for name in ['progress.css','progress.js']:shutil.copyfile(root/'assets'/name,out/'assets'/name)
    (out/'data').mkdir(exist_ok=True)
    (out/'data/progress.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
