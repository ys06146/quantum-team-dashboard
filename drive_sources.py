"""Import only the explicitly mapped Drive documents; never execute their scripts."""
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import ast
import hashlib
import html
import json
import posixpath
import re

VERSION = 1
PLAN = 'quantum-team-plan-share.html'
GUIDES = {
    'soyeon': 'seojin_work/week1/SOYEON_GUIDE',
    'jiwoo': 'seojin_work/week1/JIWOO_GUIDE',
    'yechan': 'seojin_work/week1/YECHAN_GUIDE',
    'seojin': 'seojin_work/week1/SEOJIN_GUIDE',
    'seohee': 'seohee_work/week1/SEOHEE_GUIDE',
}
VOID = {'br', 'hr', 'img', 'meta', 'link', 'input', 'wbr', 'source', 'area', 'base', 'embed', 'param', 'col'}
ALLOWED = set('div section article header footer aside nav p h1 h2 h3 h4 h5 h6 span strong b em i code pre a ul ol li table thead tbody tfoot tr th td caption dl dt dd details summary button style br hr blockquote'.split())
DROP = {'script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select', 'svg', 'math', 'link', 'meta', 'img'}

@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def find(self, tag=None, **attrs):
        result = []
        for c in self.children:
            if not isinstance(c, Node):
                continue
            if (tag is None or c.tag == tag) and all(
                (v in c.attrs.get('class', '').split() if k == 'class_' else c.attrs.get(k) == v)
                for k, v in attrs.items()
            ):
                result.append(c)
            result.extend(c.find(tag, **attrs))
        return result

class Tree(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

def names(text):
    text = re.sub(r'화학\s*담당', '서희', text)
    text = re.sub(r'이름 확정 전까지 [‘\']서희[’\'](?:으)?로 표시한다\.', '', text)
    for old, new in [('서희은', '서희는'), ('서희이', '서희가'), ('서희과', '서희와'),
                     ('Chemistry · 이름 미정', 'Chemistry'), ('5인 역할안', '5인 팀'), ('chemistry_work/', 'seohee_work/')]:
        text = text.replace(old, new)
    return text

def target_for(logical, prefix=''):
    stem = Path(logical).stem
    for slug, source in GUIDES.items():
        if stem == Path(source).name:
            return prefix + 'guides/' + slug + '.html'
    if logical.endswith(PLAN):
        return prefix + 'plan.html'
    if '/reports/' in logical:
        for task in ('dfthcsos', 'invsqrt', 'dqi'):
            if logical.endswith('/' + task + '.json'):
                return prefix + 'results.html#' + task
        return prefix + 'results.html'
    if '/vendor/competition/' in logical:
        return prefix + 'resources.html#official-files'
    if logical.endswith('README.md'):
        return prefix + 'resources.html#environment'
    return prefix + 'resources.html#team-files'

def remap_url(url, source, depth):
    url = html.unescape(url).strip()
    parsed = urlsplit(url)
    if parsed.scheme in ('https', 'http'):
        if parsed.username or parsed.password:
            raise ValueError('A document link contains embedded credentials.')
        return url
    if parsed.scheme or parsed.netloc:
        raise ValueError('Unsupported link scheme in a source document.')
    if url.startswith('#'):
        return url
    logical = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path)))
    target = target_for(logical, '../' * depth)
    if depth and target.startswith('../guides/'):
        target = target[len('../guides/'):]
    if parsed.fragment and '#' not in target and 'resources' not in target and 'results' not in target:
        target += '#' + parsed.fragment
    return target

def portable(text):
    text = names(text)
    text = re.sub(r"Set-Location -LiteralPath '[A-Z]:\\내 드라이브\\jjeya\\([^']+)'",
                  lambda m: "Set-Location -LiteralPath (Join-Path $ProjectRoot '" + m[1] + "')", text)
    text = re.sub(r'[A-Z]:\\내 드라이브\\jjeya', '<팀 작업 폴더>', text)
    text = re.sub(r'C:\\Users\\[^\\\s\'"<>]+', '<사용자 폴더>', text)
    text = text.replace('첫 줄의 G를 본인 PC에 맞게 바꾼다.', '`$ProjectRoot`에 본인 PC의 jjeya 폴더 경로를 지정한다.')
    text = text.replace('첫 줄의 경로를 본인 PC에 맞게 바꾼다.', '`$ProjectRoot`에 본인 PC의 jjeya 폴더 경로를 지정한다.')
    return text

def render(node, source, depth=0, allow_style=False):
    if isinstance(node, str):
        return html.escape(portable(node), quote=False)
    if node.tag in DROP or (node.tag == 'style' and not allow_style):
        return ''
    body = ''.join(render(c, source, depth, allow_style) for c in node.children)
    if node.tag not in ALLOWED:
        return body
    attrs = {}
    for key, value in node.attrs.items():
        if key in {'id', 'class', 'role', 'lang', 'scope', 'colspan', 'rowspan', 'type', 'tabindex', 'hidden', 'open', 'title', 'data-task'} or key.startswith('aria-'):
            attrs[key] = value
        if key == 'href':
            attrs[key] = remap_url(value, source, depth)
    opening = '<' + node.tag + ''.join(' ' + k + ('="' + html.escape(v, quote=True) + '"' if v is not None else '') for k, v in attrs.items()) + '>'
    if node.tag == 'style':
        # CSS remains inside the site CSP; no executable source JavaScript is copied.
        body = node.text()
    result = opening + body + ('' if node.tag in VOID else '</' + node.tag + '>')
    if node.tag == 'code' and 'data-local-file' in node.attrs:
        url = target_for(node.attrs['data-local-file'], '../' * depth)
        result = '<a href="' + html.escape(url, quote=True) + '">' + result + '</a>'
    return result

def parse_plan(text):
    tree = Tree(names(text)).root
    frames = tree.find('iframe', id='codex-visualization')
    if frames:
        inner = frames[0].attrs.get('data-srcdoc') or frames[0].attrs.get('srcdoc')
        if not inner:
            raise ValueError('The plan iframe is missing its document.')
        tree = Tree(names(inner)).root
    roots = tree.find('div', id='quantum-team-plan')
    if len(roots) != 1:
        raise ValueError('Expected one quantum-team-plan section.')
    root = roots[0]
    code = '\n'.join(n.text() for n in root.find('script'))
    match = re.search(r'const\s+tasks\s*=\s*(\{[\s\S]*?\n\s*\});', code)
    if not match:
        raise ValueError('The plan task definitions are missing.')
    literal = re.sub(r'(?m)^(\s*)([a-z]\d+):', r"\1'\2':", match[1])
    tasks = ast.literal_eval(literal)
    if not isinstance(tasks, dict) or not tasks or any(not isinstance(v, (list, tuple)) or len(v) != 6 or any(not isinstance(x, str) for x in v) for v in tasks.values()):
        raise ValueError('Each plan task must contain six text fields.')
    button_ids = {n.attrs['data-task'] for n in root.find('button') if 'data-task' in n.attrs}
    if button_ids != set(tasks):
        raise ValueError('Plan buttons and task details disagree.')
    phases = []
    for phase in root.find(class_='q-phase'):
        small = phase.find(class_='text-small')
        headings = phase.find('h3')
        if len(small) >= 2 and headings:
            phases.append({'label': small[0].text(), 'title': headings[0].text(), 'detail': small[-1].text()})
    people = {}
    for role in root.find(class_='q-role'):
        headers = role.find('header')
        if not headers or not headers[0].find('h3'):
            continue
        header = headers[0]
        label = header.find('h3')[0].text()
        spans = header.find('span')
        fields = dict(zip((n.text() for n in role.find('dt')), (n.text() for n in role.find('dd'))))
        people[label] = {'role': spans[-1].text() if spans else '', 'description': fields.get('주 책임', '')}
    for matrix in root.find('table', class_='q-matrix'):
        for row in matrix.find('tr'):
            th, td = row.find('th'), row.find('td')
            if not th or not td:
                continue
            label = ''.join(c for c in th[0].children if isinstance(c, str)).strip()
            outputs = td[0].find('span')
            if label in people and outputs:
                people[label]['output'] = re.sub(r'^산출물\s*·\s*', '', outputs[-1].text())
    title = root.find('header', class_='q-title')
    schedule = re.search(r'제안 일정\s+([^ ·]+)', title[0].text()) if title else None
    meta = {'phases': phases, 'people': people, 'schedule': schedule[1] if schedule else ''}
    return render(root, PLAN, allow_style=True), tasks, meta

def markdown_guide(text, source, slug):
    text = portable(text)
    text = text.replace('이 PC에서는 설치를 다시 할 필요가 없다.', '개인 PC의 Python 3.12 환경을 먼저 확인한다.')
    text = text.replace('환경은 Python 3.12.4, kickmix 1.0.0, NumPy 2.2.6, SciPy 1.15.3으로 고정돼 있다.', '초기 기준 환경은 Python 3.12.4, kickmix 1.0.0, NumPy 2.2.6, SciPy 1.15.3이었다. 공유 가상환경에는 기반 Python 버전 변경 이력이 있으므로 지우 가이드 2절대로 개인 PC의 Python 3.12 환경을 준비하고 $Py를 사용한다.')
    if slug == 'yechan':
        text = text.replace('이 PC의', '공통 작업 폴더의').replace('.\\.venv\\Scripts\\python.exe', '& $Py')
        text = text.replace('## 2. 지금 바로 실행하기', '## 2. 지금 바로 실행하기\n\n먼저 [지우 가이드의 환경 준비](JIWOO_GUIDE.html#section-2)로 개인 Python 3.12 환경과 `$Py`를 설정한다. 아래 명령은 그 PowerShell 창에서 실행한다.')
        text = text.replace('coef16_model.kmb', 'coef16_model_new.kmb')
    text = text.replace('드라이브 문자가 달라도 `jjeya` 안의 폴더 배치를 유지하면 상대 링크를 그대로 사용할 수 있다.', '웹 링크는 공개 가이드·결과·자료 안내로 연결된다. 실제 실험에서는 `jjeya` 폴더 배치를 유지한다.')
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: '[' + m[1] + '](' + remap_url(m[2], source, 1) + ')', text)

def html_guide(text, source):
    tree = Tree(names(text)).root
    mains = tree.find('main')
    if len(mains) != 1:
        raise ValueError('HTML guides must have one main content element.')
    main = mains[0]
    for i, heading in enumerate(main.find('h2'), 1):
        heading.attrs.setdefault('id', 'section-' + str(i))
    body = ''.join(render(c, source, 1) for c in main.children)
    if len(body.strip()) < 30:
        raise ValueError('The HTML guide body is empty.')
    return body

def snapshot(root):
    paths = [PLAN] + [p + ext for p in GUIDES.values() for ext in ('.md', '.html')]
    result = {}
    for relative in paths:
        path = root / relative
        if not path.exists():
            if relative == PLAN:
                raise FileNotFoundError(relative)
            continue
        raw = path.read_bytes()
        if len(raw) > 2_000_000:
            raise ValueError('Source document is unexpectedly large: ' + relative)
        normalized = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
        result[relative] = {'text': normalized, 'hash': hashlib.sha256(raw).hexdigest(), 'mtime': path.stat().st_mtime_ns}
    return result

def choose_guide(base, current, previous, selected):
    candidates = [base + ext for ext in ('.md', '.html') if base + ext in current]
    if not candidates:
        raise FileNotFoundError(base + ' (.md or .html)')
    changed = [p for p in candidates if p in previous and current[p]['hash'] != previous[p]]
    added = [p for p in candidates if previous and p not in previous]
    if changed or added:
        return max(changed + added, key=lambda p: (current[p]['mtime'], p.endswith('.md')))
    if selected in candidates:
        return selected
    return candidates[0]  # First installation imports Markdown when both formats exist.

def import_documents(site, current, state):
    content = site / 'content'
    (content / 'guides').mkdir(parents=True, exist_ok=True)
    plan, tasks, meta = parse_plan(current[PLAN]['text'])
    (content / 'plan.html').write_text(plan, encoding='utf-8')
    for name, data in [('tasks.json', tasks), ('plan-summary.json', meta)]:
        (content / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    selected = {}
    for slug, base in GUIDES.items():
        source = choose_guide(base, current, state.get('hashes', {}), state.get('selected', {}).get(slug))
        selected[slug] = source
        md_path, html_path = content / 'guides' / (slug + '.md'), content / 'guides' / (slug + '.html')
        if source.endswith('.md'):
            md_path.write_text(markdown_guide(current[source]['text'], source, slug), encoding='utf-8')
            html_path.unlink(missing_ok=True)  # Only a generated file inside the isolated build checkout.
        else:
            body = html_guide(current[source]['text'], source)
            html_path.write_text(body, encoding='utf-8')
            md_path.write_text('<!-- HTML 원본에서 동기화한 CommonMark HTML 문서 -->\n\n' + body, encoding='utf-8')
    return selected
