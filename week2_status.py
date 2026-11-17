"""Render the week-2 status page from content/week2-status.json plus the shared plan and progress."""
from datetime import date
from html import escape
import json
import re
import shutil

TASK_LABELS = {'invsqrt': 'INVSQRT', 'dqi': 'DQI', 'dfthcsos': 'DFTHC-SOS'}
PREFIX = {'소연': 's', '지우': 'j', '예찬': 'y', '서진': 'e', '서희': 'c'}
WEEKDAYS = '월화수목금토일'
WEEK = 2


def composite(tasks):
    """Geometric mean of the per-task improvement ratios (the official composite score)."""
    product = 1.0
    for task in tasks:
        product *= task['ratio']
    return product ** (1 / 3)


def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported week2 status schema')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data.get('updated_at', '')):
        raise ValueError('Missing week2 update date')
    tasks = data.get('tasks', [])
    if [t.get('task') for t in tasks] != list(TASK_LABELS):
        raise ValueError('Tasks must be invsqrt, dqi, dfthcsos in that order')
    for task in tasks:
        ratio = task.get('ratio')
        if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or ratio <= 0:
            raise ValueError('Task ratio must be a positive number: ' + task['task'])
    score = data.get('score', {})
    public = score.get('public_score')
    if not isinstance(public, (int, float)) or public <= 0:
        raise ValueError('Missing public score')
    if abs(composite(tasks) - public) > 1e-3:
        raise ValueError(f'Task ratios give {composite(tasks):.5f}, not the public score {public}')
    history = score.get('history', [])
    if not history or history[-1].get('public_score') != public:
        raise ValueError('Score history must end at the current public score')
    for row in history:
        date.fromisoformat(row['date'])
    deadlines = data.get('deadlines', [])
    if not deadlines:
        raise ValueError('At least one deadline is required')
    days = [date.fromisoformat(row['date']) for row in deadlines]
    if days != sorted(days):
        raise ValueError('Deadlines must be in date order')
    for row in deadlines:
        if row.get('time') and not re.fullmatch(r'\d{2}:\d{2}', row['time']):
            raise ValueError('Deadline time must be HH:MM')
    return data


def day_label(iso):
    d = date.fromisoformat(iso)
    return f'{d.month}/{d.day}({WEEKDAYS[d.weekday()]})'


def fmt_ratio(value):
    return f'×{value:,.2f}'


def build_week2(root, out, page, people):
    data = validate(json.loads((root / 'content/week2-status.json').read_text(encoding='utf-8')))
    tasks = json.loads((root / 'content/tasks.json').read_text(encoding='utf-8'))
    progress = json.loads((root / 'content/progress.json').read_text(encoding='utf-8'))
    score = data['score']
    lb = data.get('leaderboard')

    body = (f'<div class="page-head"><span class="eyebrow">WEEK 02 / STATUS</span><h1>2주차 현황</h1>'
            f'<p>점수, 과제별 배율, 마감, 팀원 진행을 한 화면에서 봐요. {escape(data["period"])}</p></div>')

    body += (f'<section class="section reading-note" aria-label="현재 점수"><span class="eyebrow">현재 공개 점수 · '
             f'{escape(score["checked_at"].replace("-", "."))} 확인</span><h2>{score["public_score"]:.5f}</h2>'
             '<p>종합 점수는 세 과제의 (공식 기준 비용 ÷ 제출 비용)을 기하평균한 값이에요. '
             '한 과제가 2배 좋아지면 종합 점수는 약 1.26배가 돼요.</p>')
    if lb:
        body += (f'<p class="section-note">리더보드 참고 ({escape(lb["snapshot_utc"])} UTC, {lb["teams"]:,}팀): '
                 f'1위 {lb["first"]:.5f} · 10위 {lb["tenth"]:.5f} · 100위 {lb["hundredth"]:.5f} · '
                 f'중앙값 {lb["median"]:.5f}. {escape(lb["source_note"])}</p>')
    body += '</section>'

    cards = ''
    for task in data['tasks']:
        cards += (f'<article class="bench-card"><div class="bench-top"><strong>{TASK_LABELS[task["task"]]}</strong>'
                  f'<span class="pass">제출본</span></div><div class="bench-value">{fmt_ratio(task["ratio"])}</div>'
                  f'<div class="bench-caption">{escape(task["basis"])}</div>'
                  f'<div class="bench-bottom"><span>비용 = {escape(task["cost_formula"])}</span></div></article>')
    body += ('<section class="section"><div class="section-title"><div><h2>과제별 현재 배율</h2>'
             '<p>마지막 제출본 기준이에요. ×1.00은 공식 기준본과 같은 비용이에요.</p></div>'
             '<a href="results.html">기준 기록 →</a></div><div class="bench-grid">' + cards + '</div>'
             '<p class="section-note">기하평균이라 가장 약한 과제가 전체 점수를 끌어내려요.</p></section>')

    rows = ''
    for row in data['deadlines']:
        when = day_label(row['date']) + (' ' + row['time'] if row.get('time') else '')
        rows += (f'<tr><th scope="row" class="tabular-nums">{escape(when)}</th><td>{escape(row["what"])}</td>'
                 f'<td class="tabular-nums" data-deadline="{escape(row["date"])}">{escape(row["date"].replace("-", "."))}</td></tr>')
    body += ('<section class="section"><div class="section-title"><div><h2>마감</h2>'
             '<p>시간은 미국 중부(CT) 기준이에요.</p></div></div><div class="table-wrap"><table>'
             '<thead><tr><th>날짜</th><th>할 일</th><th>남은 기간</th></tr></thead><tbody>' + rows + '</tbody></table></div></section>')

    people_html = ''
    for slug, name, role, *_ in people:
        key = PREFIX[name] + str(WEEK)
        task = tasks[key]
        done = progress['tasks'][key]['completed']
        percent = len(done) * 25
        title = task[0].split('—', 1)[-1].strip()
        people_html += (f'<article class="person-card"><div class="person-top"><span class="avatar" aria-hidden="true">{name[-1]}</span>'
                        f'<h3>{name}</h3></div><div class="person-role">{escape(title)}</div>'
                        f'<p class="person-desc">{escape(task[2])}</p>'
                        f'<p class="bench-caption">산출물<br>{escape(task[3])}</p>'
                        f'<p class="bench-caption">검토 · {escape(task[1])} · 진행 {percent}%</p>'
                        f'<div class="progress-track" role="progressbar" aria-label="{name} 2주차 진행률" aria-valuemin="0" '
                        f'aria-valuemax="100" aria-valuenow="{percent}"><span style="width:{percent}%"></span></div>'
                        f'<a href="progress.html#check-{slug}-{WEEK}" aria-label="{name} 2주차 체크리스트 보기">체크리스트 <span aria-hidden="true">→</span></a></article>')
    body += ('<section class="section"><div class="section-title"><div><h2>팀원별 2주차 과제</h2>'
             f'<p>3주 계획의 2주차 과제와 진행도 기록이에요. 진행도 갱신 {escape(progress["updated_at"].replace("-", "."))}</p></div>'
             '<a href="progress.html">진행도 전체 →</a></div><div class="team-grid">' + people_html + '</div></section>')

    hist = ''
    previous = None
    for row in score['history']:
        change = '—' if previous is None else f'{row["public_score"] / previous:.3f}배'
        hist += (f'<tr><th scope="row" class="tabular-nums">{escape(row["date"].replace("-", "."))}</th>'
                 f'<td class="tabular-nums">{row["public_score"]:.5f}</td><td class="tabular-nums">{change}</td>'
                 f'<td>{escape(row["label"])}</td></tr>')
        previous = row['public_score']
    body += ('<section class="section"><div class="section-title"><div><h2>제출 이력</h2>'
             '<p>Kaggle 공개 점수 기준이에요.</p></div><a href="week1.html">1주차 결과 →</a></div>'
             '<div class="table-wrap"><table><thead><tr><th>날짜</th><th>공개 점수</th><th>직전 대비</th><th>내용</th></tr></thead>'
             '<tbody>' + hist + '</tbody></table></div></section>')

    if data.get('rules'):
        body += ('<section class="section reading-note"><h2>채택 원칙</h2><ul>'
                 + ''.join(f'<li>{escape(rule)}</li>' for rule in data['rules']) + '</ul></section>')

    extra = '<link rel="stylesheet" href="assets/progress.css"><script src="assets/week2.js" defer></script>'
    (out / 'week2.html').write_text(page('2주차 현황', 'week2', body, extra_script=extra), encoding='utf-8')
    for name in ['progress.css', 'week2.js']:
        shutil.copyfile(root / 'assets' / name, out / 'assets' / name)
    (out / 'data').mkdir(exist_ok=True)
    (out / 'data/week2-status.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def banner(data):
    """Short home-page section pointing at the week-2 page."""
    nxt = data['deadlines'][0]
    when = day_label(nxt['date']) + (' ' + nxt['time'] if nxt.get('time') else '')
    return (f'<section class="section reading-note" aria-label="이번 주 현황"><span class="eyebrow">2주차 · '
            f'{escape(data["period"])}</span><h2>현재 공개 점수 {data["score"]["public_score"]:.5f}</h2>'
            f'<p>다음 마감은 {escape(when)} · {escape(nxt["what"])}</p>'
            '<div class="hero-actions"><a class="button primary" href="week2.html">2주차 현황 보기</a>'
            '<a class="button" href="progress.html">진행도</a></div></section>')
