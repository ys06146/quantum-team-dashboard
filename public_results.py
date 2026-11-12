"""Build the explicitly published result snapshot alongside baseline records."""
import json, shutil
from html import escape

def banner(data):
    score=f"{data['public_score']:.5f}"
    return f'''<section class="section reading-note" aria-label="최신 제출 결과">
<span class="eyebrow">1주차 작업 결과 · {escape(data['updated_at'])} 공개</span>
<h2>실제 공개 점수 1.00000 → {score}</h2>
<p>DQI 개선본 통합 제출의 채점이 완료됐어요. DQI 비용은 약 65.19배 개선됐고, 다른 두 과제는 공식 기준본을 유지했습니다.</p>
<div class="hero-actions"><a class="button primary" href="week1.html">작업 결과와 검증 근거</a><a class="button" href="meeting/jjeya-week1-meeting.html">12장 발표 자료</a><a class="button" href="speaker-notes.html">발표 대본</a></div>
<p class="section-note">점수 확인 2026.11.11 · 팀원별 결과와 독립 재현은 15일 미팅에서 확인</p></section>'''

def build_public_results(root,out,page,markdown):
    for dirname in ['records','meeting']:
        for source in (root/'content'/dirname).rglob('*'):
            if not source.is_file():continue
            target=out/dirname/source.relative_to(root/'content'/dirname)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
    latest=json.loads((root/'content/latest-results.json').read_text(encoding='utf-8'))
    report=(root/'content/week1-results.md').read_text(encoding='utf-8')
    body,_=markdown(report)
    intro='<div class="page-head"><span class="eyebrow">WEEK 01 / RESULTS</span><h1>1주차 작업 결과</h1><p>검증부터 실제 채점까지 확인한 서진의 준비 결과입니다.</p></div>'
    (out/'week1.html').write_text(page('1주차 작업 결과','latest',intro+banner(latest)+'<article class="document">'+body+'</article>'),encoding='utf-8')
    script=(root/'content/meeting/jjeya-week1-speaker-notes.md').read_text(encoding='utf-8')
    notes,_=markdown(script)
    (out/'speaker-notes.html').write_text(page('발표 대본','latest','<div class="page-head"><span class="eyebrow">1주차 미팅 / 약 15분</span><h1>12장 발표 대본</h1><p><a href="meeting/jjeya-week1-meeting.html">발표 자료 열기</a> · <a href="meeting/jjeya-week1-speaker-notes.md" download>대본 내려받기</a></p></div><article class="document">'+notes+'</article>'),encoding='utf-8')
    (out/'data/latest-results.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
