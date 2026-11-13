"""Build the public team dashboard with Python's standard library only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import html,json,re,shutil
from drive_sources import Tree

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'docs'
PEOPLE=[
 ('soyeon','소연','검증 · 실험 설계','공식 기준을 정리하고 후보의 효과를 독립적으로 비교해요.','검증표 · 기준 로그','Statistics'),
 ('jiwoo','지우','수치 최적화 · 탐색','화학 분해와 각도 데이터를 읽고 수치 후보를 만들어요.','재구성 오차표 · 탐색 범위','Data Science'),
 ('yechan','예찬','역제곱근 · 수치해석','근사식과 비트 폭의 정확도·연산량을 비교해요.','오차 분석 · 개선 가설','Mechanical Engineering'),
 ('seojin','서진','회로 · 실행 통합','공통 실행 환경과 회로, 검증 기록을 연결해요.','3과제 실행기 · 제출 구조','Data Science & CS'),
 ('seohee','서희','화학 해석 · 근사 검토','화학 지표를 해석하고 지우의 근사 후보를 검토해요.','문제 설명 · 지표표 · 검토 메모','Chemistry')
]
BASE=json.loads((ROOT/'content/baselines.json').read_text(encoding='utf-8'))
LATEST_PATH=ROOT/'content/latest-results.json'
LATEST=json.loads(LATEST_PATH.read_text(encoding='utf-8')) if LATEST_PATH.exists() else None
PROGRESS_PATH=ROOT/'content/progress.json'

SUMMARY_PATH=ROOT/'content/plan-summary.json'
SUMMARY=json.loads(SUMMARY_PATH.read_text(encoding='utf-8')) if SUMMARY_PATH.exists() else {}
SYNC_PATH=ROOT/'content/sync-info.json'
SYNC=json.loads(SYNC_PATH.read_text(encoding='utf-8')) if SYNC_PATH.exists() else {}
for i,person in enumerate(PEOPLE):
    slug,name,role,desc,output,major=person
    data=SUMMARY.get('people',{}).get(name,{})
    PEOPLE[i]=(slug,name,data.get('role') or role,data.get('description') or desc,data.get('output') or output,major)
SCHEDULE=SUMMARY.get('schedule') or '2026.11.09 — 11.29'
UPDATE_LABEL=('문서 동기화 '+SYNC['updated_at'][:10].replace('-','.')) if SYNC else '업데이트 2026.11.08'

LABELS={'invsqrt':'INVSQRT','dqi':'DQI','dfthcsos':'DFTHC-SOS'}
SUBTITLES={'invsqrt':'역제곱근 위상 회로','dqi':'Reed–Solomon 디코더','dfthcsos':'화학 분해 · 각도 로딩'}
def esc(x):return html.escape(str(x))
def inline(s):
    s=esc(s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
def markdown(s):
    lines=s.splitlines();out=[];headings=[];i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('```'):
            code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            out.append('<pre><code>'+esc('\n'.join(code))+'</code></pre>')
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                row=[x.strip() for x in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',x) for x in row):rows.append(row)
                i+=1
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>' for x in rows[0])+'</tr></thead><tbody>')
            out.extend('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in row)+'</tr>' for row in rows[1:])
            out.append('</tbody></table></div>');continue
        elif line.startswith('## '):
            id='section-'+str(len(headings)+1);title=line[3:];headings.append((id,title))
            out.append(f'<h2 id="{id}">'+inline(title)+'</h2>')
        elif line.startswith('### '):out.append('<h3>'+inline(line[4:])+'</h3>')
        elif line.startswith('# '):out.append('<p class="doc-title">'+inline(line[2:])+'</p>')
        elif line.startswith('- '):
            out.append('<ul>')
            while i<len(lines) and lines[i].startswith('- '):out.append('<li>'+inline(lines[i][2:])+'</li>');i+=1
            out.append('</ul>');continue
        else:out.append('<p>'+inline(line)+'</p>')
        i+=1
    return '\n'.join(out),headings

def page(title,active,body,depth=0,extra_script=''):
    p='../'*depth
    nav=[('home','index.html','전체 현황'),('plan','plan.html','3주 계획 · 역할'),('guides','guides.html','개인별 가이드'),('results','results.html','검증 결과'),('resources','resources.html','자료 · 실행 안내')]
    if LATEST:nav.insert(3,('latest','week1.html','1주차 작업 결과'))
    if PROGRESS_PATH.exists():nav.append(('progress','progress.html','주차별 진행도'))
    nav.append(('meetings','meetings.html','회의록'))
    links=''.join(f'<a href="{p+url}"'+(' aria-current="page"' if key==active else '')+f'><span class="nav-no">{i:02}</span>{text}</a>' for i,(key,url,text) in enumerate(nav,1))
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta name="description" content="다섯 명의 양자 회로 팀을 위한 3주 실행 계획, 개인별 가이드와 공식 기준 예제 검증 기록."><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'"><title>{esc(title)} · Quantum Team</title><link rel="stylesheet" href="{p}assets/styles.css"><script src="{p}assets/app.js" defer></script>{extra_script}</head><body><div class="shell">
<aside class="sidebar"><a class="brand" href="{p}index.html"><span class="brand-mark" aria-hidden="true">Q</span><span>Quantum Team<small>CIRCUIT COMPILATION</small></span></a><button class="menu-button" type="button" aria-controls="site-nav" aria-expanded="false">메뉴</button><div class="side-caption">TEAM WORKSPACE</div><nav class="side-nav" id="site-nav" aria-label="대시보드">{links}</nav><div class="side-bottom"><strong>Google Quantum AI</strong>5인 팀 · 3주 실행안<br>{esc(SCHEDULE)}</div></aside>
<main class="content"><div class="topline"><span>팀 워크스페이스 / {esc(title)}</span><span title="{esc(SYNC.get('updated_at','2026-11-08'))}">{esc(UPDATE_LABEL)}</span></div>{body}<footer class="footnote"><span>팀 실행 제안 · 기준 검증 기록 2026.11.07</span><span><a href="https://github.com/ys06146/quantum-team-dashboard">GitHub 저장소 ↗</a> · <a href="{p}resources.html">자료 출처</a></span></footer></main></div></body></html>'''

def team_cards():
    return '<div class="team-grid">'+''.join(f'<article class="person-card"><div class="person-top"><span class="avatar" aria-hidden="true">{name[-1]}</span><h3>{name}</h3></div><div class="person-role">{role}</div><p class="person-desc">{desc}</p><p class="bench-caption">이번 주 산출물<br>{output}</p><a href="guides/{slug}.html" aria-label="{name} 가이드 열기">가이드 열기 <span aria-hidden="true">→</span></a></article>' for slug,name,role,desc,output,major in PEOPLE)+'</div>'

def benchmarks():
    pieces=[]
    for task in ['invsqrt','dqi','dfthcsos']:
        r=BASE[task]['result'];score=f'{r["score"]:,.2f}' if task=='invsqrt' else ('2.444 × 10¹³' if task=='dqi' else '3.356 × 10⁹')
        pieces.append(f'<article class="bench-card"><div class="bench-top"><strong>{LABELS[task]}</strong><span class="pass">FULL PASS</span></div><div class="bench-value">{score}</div><div class="bench-caption">공식 로컬 비용 · {SUBTITLES[task]}</div><div class="bench-bottom"><span>{r["num_qubits"]:,} qubits</span><span>{r["verified_shots"]:,} shots</span><a href="results.html#{task}">상세 기록 ↗</a></div></article>')
    return '<div class="bench-grid">'+''.join(pieces)+'</div>'

def write(name,text):
    path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

def build():
    OUT.mkdir(exist_ok=True)
    for name in ['styles.css','app.js']:
        (OUT/'assets').mkdir(exist_ok=True);shutil.copyfile(ROOT/'assets'/name,OUT/'assets'/name)
    if LATEST:
        from public_results import build_public_results
        build_public_results(ROOT,OUT,page,markdown)
    tasks=json.loads((ROOT/'content/tasks.json').read_text(encoding='utf-8'))
    write('assets/plan.js','const PLAN_TASKS='+json.dumps(tasks,ensure_ascii=False)+';\n'+(ROOT/'assets/plan-runtime.js').read_text(encoding='utf-8'))
    home='''<section class="hero"><div><span class="eyebrow">ONE TEAM, THREE BENCHMARKS</span><h1>다음 작업을,<br>같은 기준으로.</h1><p>각자의 역할과 읽을 파일, 검증된 기준값을 한곳에 모았어요. 내 가이드부터 열고 이번 주 산출물을 확인하세요.</p><div class="hero-actions"><a class="button primary" href="guides.html">내 가이드 찾기 <span aria-hidden="true">→</span></a><a class="button" href="plan.html">3주 계획 보기</a></div></div><div class="phases"><div class="phase"><span class="phase-no">W1</span><div><strong>재현 · 기준 확정</strong><small>11/09–15 · 공통 언어와 유효본 확보</small></div></div><div class="phase"><span class="phase-no">W2</span><div><strong>후보 실험 · 선별</strong><small>11/16–22 · 근사·정밀도·회로 비교</small></div></div><div class="phase"><span class="phase-no">W3</span><div><strong>동결 · 독립 재검증</strong><small>11/23–29 · 재현 가능한 제출 묶음</small></div></div></div></section>'''
    if SUMMARY.get('phases'):
        phase_html='<div class="phases">'+''.join('<div class="phase"><span class="phase-no">W'+str(i)+'</span><div><strong>'+esc(p['title'])+'</strong><small>'+esc(p['label'])+' · '+esc(p['detail'])+'</small></div></div>' for i,p in enumerate(SUMMARY['phases'],1))+'</div></section>'
        home=home[:home.index('<div class="phases">')]+phase_html
    if LATEST:
        from public_results import banner
        home+=banner(LATEST)
    home+='<section class="section"><div class="section-title"><div><h2>검증된 출발점</h2><p>공식 기본 예제 3종의 전체 검증 기록</p></div><a href="results.html">결과 모두 보기 →</a></div>'+benchmarks()+'<p class="section-note">각 과제의 비용식은 서로 달라요. 같은 과제의 기준선과 후보를 비교하세요. 로컬 PASS는 Kaggle 제출 완료를 뜻하지 않습니다.</p></section>'
    home+='<section class="section"><div class="section-title"><div><h2>각자의 첫 주</h2><p>파일을 다운로드하지 않고 가이드를 바로 읽을 수 있어요.</p></div><a href="plan.html">역할 자세히 →</a></div>'+team_cards()+'</section>'
    home+='''<section class="section"><div class="section-title"><h2>후보가 제출본이 되기까지</h2></div><div class="handoff"><span><strong>예찬 · 지우</strong> 후보 생성</span><span class="arrow" aria-hidden="true">→</span><span><strong>서희</strong> 화학 지표 검토</span><span class="arrow" aria-hidden="true">→</span><span><strong>서진</strong> 회로 통합</span><span class="arrow" aria-hidden="true">→</span><span><strong>소연</strong> 독립 비교</span></div><p class="section-note">서희의 검토는 화학 후보에 해당해요. 채택 결과와 파일 버전은 함께 기록합니다.</p></section>'''
    write('index.html',page('전체 현황','home',home))
    fragment=(ROOT/'content/plan.html').read_text(encoding='utf-8')
    write('plan.html',page('3주 계획 · 역할','plan','<div class="page-head"><span class="eyebrow">SPRINT PLAN</span><h1>3주 계획과 역할</h1><p>업무 버튼을 선택하면 작업·산출물·완료 기준·검토자를 볼 수 있어요.</p></div><div class="document">'+fragment+'</div>',extra_script='<script src="assets/plan.js" defer></script>'))
    write('guides.html',page('개인별 가이드','guides','<div class="page-head"><span class="eyebrow">START HERE</span><h1>내 가이드부터 시작하세요.</h1><p>읽을 파일 순서와 직접 할 일, 완료 기준과 전달할 결과물을 정리했어요.</p></div>'+team_cards()+'<div class="section reading-note">가이드 읽기에는 설치가 필요 없어요. 회로 생성·검증을 실행할 때는 공식 데이터와 개인 PC의 Python 3.12 환경을 준비하세요. <a href="resources.html#environment">실행 환경 안내 →</a></div>'))
    for slug,name,role,desc,output,major in PEOPLE:
        md=(ROOT/'content/guides'/f'{slug}.md').read_text(encoding='utf-8')
        html_source=ROOT/'content/guides'/f'{slug}.html'
        if html_source.exists():
            body=html_source.read_text(encoding='utf-8')
            headings=[(h.attrs['id'],h.text()) for h in Tree(body).root.find('h2') if 'id' in h.attrs]
        else:
            body,headings=markdown(md)
        toc='<aside class="toc" aria-label="가이드 목차"><strong>ON THIS PAGE</strong>'+''.join(f'<a href="#{id}">{esc(title)}</a>' for id,title in headings)+'</aside>'
        intro=f'<div class="page-head"><span class="eyebrow">WEEK 01 / {esc(major.upper())}</span><h1>{name} · {role}</h1><p>{desc}</p></div>'
        if '$ProjectRoot' in md:
            intro+='<div class="reading-note">실행 명령은 본인 PC에서 사용해요. 먼저 PowerShell에서 <code>$ProjectRoot = \'C:\\경로\\jjeya\'</code>를 실제 팀 작업 폴더 경로로 바꾸어 설정하세요. 웹 링크는 가이드·결과·자료 안내로 연결됩니다.</div>'
        write(f'guides/{slug}.html',page(name+' 가이드','guides',intro+'<div class="doc-layout"><article class="document">'+body+f'<p><a href="{slug}.md" download>Markdown 가이드 내려받기</a></p></article>'+toc+'</div>',depth=1))
        write(f'guides/{slug}.md',md)
    result_body='<div class="page-head"><span class="eyebrow">VERIFIED BASELINES</span><h1>검증 결과와 비교 기준</h1><p>공식 기본 예제의 로컬 full 결과를 공개용 요약으로 정리했어요. 실행 환경은 과제별 원본 기록에 따라 다릅니다.</p></div>'+benchmarks()
    if LATEST:
        from public_results import banner
        result_body=banner(LATEST)+result_body
    for task in ['invsqrt','dqi','dfthcsos']:
        b=BASE[task];r=b['result']
        result_body+=f'<section class="result-section document" id="{task}"><h2>{LABELS[task]} <span class="pass">FULL PASS</span></h2><p>{SUBTITLES[task]} · 기록 {b["recorded_date"]}</p><div class="table-wrap"><table><thead><tr><th>항목</th><th>기록값</th></tr></thead><tbody>'
        values=[('프로필','full · 공식 기본 문제 크기·허용 오차·샷 수'),('공식 로컬 비용',r['score']),('검증 shots',f'{r["verified_shots"]:,}'),('큐비트',r['num_qubits']),('실행 시간(초)',b['elapsed_seconds'])]
        if task=='invsqrt':values += [('위상 오차 / 허용 오차',r['worst_error_over_tolerance']),('최악 입력 x',r['worst_x']),('실행 방식','Windows spawn · 원본 작업·배치·시드·검사 유지')]
        if task=='dqi':values += [('값 오류 / 위상 오류',f'{r["value_errors"]} / {r["phase_errors"]}'),('유효 오류율 상한',r['effective_error_rate']),('실행 환경','Ubuntu · Python 3.12.3 · 원본 검증기 4 workers')]
        if task=='dfthcsos':values += [(k,v) for k,v in r['metrics'].items()]+[('ANGLE 회로 수',r['num_circuits']),('각도 비트 / 단어 묶음',f'{r["brot"]} / {r["batch_size"]}')]
        result_body+=''.join('<tr><th>'+esc(k)+'</th><td class="tabular-nums">'+esc(v)+'</td></tr>' for k,v in values)+'</tbody></table></div>'
        result_body+='<details class="result-details"><summary>공식 결과 필드 펼치기</summary><pre><code>'+esc(json.dumps(r,indent=2,ensure_ascii=False))+'</code></pre></details></section>'
    result_body+='<section class="section reading-note">수치 모델 PASS, 축소 smoke PASS와 전체 full PASS를 구분하세요. 비용은 같은 과제 안에서 비교합니다. <a href="data/baselines.json">공개 요약 JSON 보기 →</a></section>'
    write('results.html',page('검증 결과','results',result_body))
    write('data/baselines.json',json.dumps(BASE,indent=2,ensure_ascii=False))
    if SYNC:write('data/sync-info.json',json.dumps(SYNC,indent=2,ensure_ascii=False))
    resources='''<div class="page-head"><span class="eyebrow">FILES & REPRODUCIBILITY</span><h1>자료와 실행 환경</h1><p>계획과 가이드는 이 사이트에서 읽고, 실제 실험은 팀 작업 폴더에서 진행해요.</p></div>
<div class="resource-list"><section class="resource-item" id="official-files"><h2>공식 실험 자료</h2><p>공식 예제 회로, NPZ, FCIDUMP와 검증 코드는 Kaggle 대회 Data에서 제공해요. 팀 공통 폴더에 이미 확보한 원본도 같은 구조로 보존되어 있습니다.</p><a class="button primary" href="https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data" target="_blank" rel="noopener noreferrer">Kaggle 공식 Data 열기 ↗</a><code>jjeya/seojin_work/week1/vendor/competition/</code><p>검증 코드: verifiers/ · 기준 회로: sample_submission/ · 공식 ZIP: data/competition.zip</p><p>가이드의 공식 파일 링크는 이 안내로 연결돼요. 공개 저장소에는 팀이 작성한 계획·가이드·검증 결과 요약을 담았습니다.</p></section>
<section class="resource-item" id="team-files"><h2>팀 작업 폴더</h2><p>공통 실행 도구와 원본 로그는 seojin_work/week1에, 개인 분석은 각자의 week1에 보관해요.</p><pre><code>jjeya/
  quantum-team-plan-share.html
  seojin_work/week1/       # 공통 환경 · scripts · reports · logs
  soyeon_work/week1/       # 검증 · 비교 기록
  jiwoo_work/week1/        # 수치 실험 분석
  yechan_work/week1/       # 역제곱근 분석
  seohee_work/week1/       # 화학 설명 · 지표표 · 검토 메모</code></pre><p>공통 파일: scripts/run_baselines.py, environment_check.py, verify_assets.py, invsqrt_lab.py, invsqrt_windows.py. 후보는 실험 ID와 생성 설정·입력 해시·full JSON·로그가 연결되게 남기세요.</p></section>
<section class="resource-item" id="environment"><h2>실행 환경</h2><p>Python 3.12 · kickmix 1.0.0 · NumPy 2.2.6 · SciPy 1.15.3을 기준으로 사용해요. 공유 가상환경에는 기반 Python이 바뀐 이력이 있으므로 각자 PC에 가상환경을 만들고 실제 버전을 확인하세요.</p><a class="button" href="guides/jiwoo.html#section-2">개인 PC 준비 명령 보기 →</a><p>가이드는 설치 없이 볼 수 있어요. 실제 실행 명령의 $ProjectRoot는 본인 PC의 jjeya 폴더 경로로 설정합니다. KMB 입력에는 영문 상대 경로를 사용하세요.</p></section>
<section class="resource-item"><h2>공식 출처</h2><p><a href="https://www.kaggle.com/code/metric/google-quantum-ai-metric" target="_blank" rel="noopener noreferrer">공식 평가 코드 ↗</a></p><p><a href="https://github.com/quantumlib/Qualtran/tree/main/kickmix" target="_blank" rel="noopener noreferrer">kickmix 소스 ↗</a></p><p><a href="https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/overview/evaluation" target="_blank" rel="noopener noreferrer">대회 평가·일정 ↗</a></p><p>팀 3주 일정은 실행 제안입니다. 공식 일정은 2026-11-07 확인 기록을 바탕으로 하며, 실제 제출 전 대회 페이지를 다시 확인하세요.</p></section></div>'''
    write('resources.html',page('자료 · 실행 안내','resources',resources))
    write('404.html',page('페이지 찾기','home','<div class="page-head"><h1>이 페이지를 찾을 수 없어요.</h1><p>대시보드에서 가이드와 자료를 다시 찾아주세요.</p></div><a class="button primary" href="index.html">대시보드로 이동 →</a>'))
    write('.nojekyll','')

    meetings_dir = ROOT / 'content/meetings'
    meeting_files = list(meetings_dir.glob('*.md')) if meetings_dir.exists() else []
    meeting_files.sort(key=lambda x: x.name, reverse=True)
    if meeting_files:
        meeting_list_html = '<div class="document"><ul>'
        for mf in meeting_files:
            parts = mf.stem.split('-', 3)
            date_str = '-'.join(parts[:3]) if len(parts) >= 3 else ''
            title_str = parts[3] if len(parts) > 3 else mf.stem
            
            md_content = mf.read_text(encoding='utf-8')
            html_content, _ = markdown(md_content)
            
            write(f'meetings/{mf.stem}.html', page(f'{date_str} 회의록', 'meetings', f'<div class="page-head"><span class="eyebrow">{esc(date_str)}</span><h1>{esc(title_str)}</h1></div><div class="document">{html_content}</div><div class="section"><a class="button" href="../meetings.html">← 목록으로</a></div>', depth=1))
            meeting_list_html += f'<li><a href="meetings/{mf.stem}.html"><strong>{esc(date_str)}</strong> - {esc(title_str)}</a></li>'
        meeting_list_html += '</ul></div>'
    else:
        meeting_list_html = '<div class="section reading-note"><p>아직 올라온 회의록이 없어요.</p></div>'

    meetings_body = f'<div class="page-head"><span class="eyebrow">MEETINGS</span><h1>팀 회의록</h1><p>회의록 요약과 결정 사항을 모아둡니다.</p></div>{meeting_list_html}'
    write('meetings.html', page('회의록', 'meetings', meetings_body))

    if PROGRESS_PATH.exists():
        from weekly_progress import build_progress
        build_progress(ROOT,OUT,page,PEOPLE,SUMMARY)
    validate()

class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ['href','src']:
            if key in a:self.links.append(a[key])
def validate():
    pages={}
    for path in OUT.rglob('*.html'):
        scan=Scan();text=path.read_text(encoding='utf-8');scan.feed(text)
        assert len(scan.ids)==len(set(scan.ids)),path
        assert not re.search(r'화학\s*담당|이름 미정|C:\\Users\\|file:///|H:\\내 드라이브|G:\\내 드라이브',text),path
        pages[path.resolve()]=scan
    links=0
    for path,scan in pages.items():
        for link in scan.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:
                assert u.scheme in ('https','http') and not u.username and not u.password,(path,link)
                continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            assert target.is_relative_to(OUT.resolve()),(path,link)
            assert target.is_file(),(path,link)
            if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(path,link)
            links+=1
    for path in OUT.rglob('*'):
        if path.is_file():assert path.stat().st_size<1024*1024,path
    print(f'Built {len(pages)} HTML pages; {links} internal links and anchors verified.')

if __name__=='__main__':build()
