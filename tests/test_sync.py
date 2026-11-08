"""Contract and local bare-Git integration tests. Never contact GitHub."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import drive_sources as sources
import sync_drive as sync

PLAN = '''<div id="quantum-team-plan"><header class="q-title">제안 일정 2026.11.09–11.29</header>
<div class="q-phase"><div class="text-small">W1 · 11/09–11/15</div><h3>기준 검증</h3><div class="text-small">기준 확보</div></div>
<button data-task="c1">서희 작업</button><script>
const tasks = {
 c1: ['서희 · 1주차', '지우', '화학 지표 읽기', '검토서', '대조 완료', '팀 전달']
};
throw new Error('Must never execute source scripts');
</script>
  
</div>'''

class ImportTests(TestCase):
    def test_windows_line_endings_are_normalized_before_generation(self):
        with TemporaryDirectory(prefix='quantum-newline-test-') as folder:
            root = Path(folder).resolve()
            assert root.name.startswith('quantum-newline-test-')
            (root / sources.PLAN).write_bytes(b'one\r\ntwo\r\n')
            self.assertEqual(sources.snapshot(root)[sources.PLAN]['text'], 'one\ntwo\n')

    def test_plan_data_is_parsed_without_executing_javascript(self):
        fragment, tasks, summary = sources.parse_plan(PLAN)
        self.assertNotIn('<script', fragment)
        self.assertEqual(tasks['c1'][2], '화학 지표 읽기')
        self.assertEqual(summary['phases'][0]['title'], '기준 검증')
        self.assertEqual(summary['schedule'], '2026.11.09–11.29')

    def test_broken_task_contract_stops_import(self):
        with self.assertRaises(ValueError):
            sources.parse_plan(PLAN.replace('data-task="c1"', 'data-task="missing"'))

    def test_literal_parser_rejects_code(self):
        with self.assertRaises((ValueError, SyntaxError)):
            sources.parse_plan(PLAN.replace("'화학 지표 읽기'", "__import__('os').getcwd()"))

    def test_html_edits_are_preserved_but_active_content_is_removed(self):
        content = '<main><h2>새 지표</h2><p onclick="bad()">갱신된 본문</p><script>bad()</script><a href="../../quantum-team-plan-share.html">계획</a></main>'
        result = sources.html_guide(content, 'seohee_work/week1/SEOHEE_GUIDE.html')
        self.assertIn('갱신된 본문', result)
        self.assertIn('id="section-1"', result)
        self.assertIn('href="../plan.html"', result)
        self.assertNotIn('onclick', result)
        self.assertNotIn('bad()', result)

    def test_unsafe_link_stops_publication(self):
        with self.assertRaises(ValueError):
            sources.html_guide('<main><a href="javascript:bad()">bad link with sufficient content</a></main>', 'guide.html')

    def test_last_changed_format_wins_and_is_remembered(self):
        base = 'folder/GUIDE'
        current = {base + '.md': {'hash': 'one', 'mtime': 100}, base + '.html': {'hash': 'two', 'mtime': 10}}
        self.assertEqual(sources.choose_guide(base, current, {}, None), base + '.md')
        self.assertEqual(sources.choose_guide(base, current, {base + '.md': 'one', base + '.html': 'old'}, None), base + '.html')
        self.assertEqual(sources.choose_guide(base, current, {base + '.md': 'old', base + '.html': 'old'}, None), base + '.md')
        self.assertEqual(sources.choose_guide(base, current, {p: x['hash'] for p, x in current.items()}, base + '.html'), base + '.html')

class GitIntegrationTests(TestCase):
    def test_publish_then_reject_invalid_and_dirty_inputs_without_overwriting(self):
        with TemporaryDirectory(prefix='quantum-sync-test-') as folder:
            work = Path(folder).resolve()
            assert work.name.startswith('quantum-sync-test-')  # Bound cleanup to this owned temp directory.
            site, remote = work / 'team/site', work / 'remote.git'
            site.mkdir(parents=True)
            for name in ('build.py', 'drive_sources.py', 'sync_drive.py', '.gitignore'):
                shutil.copyfile(ROOT / name, site / name)
            shutil.copytree(ROOT / 'assets', site / 'assets', ignore=shutil.ignore_patterns('desktop.ini'))
            (site / 'content/guides').mkdir(parents=True)
            shutil.copyfile(ROOT / 'content/baselines.json', site / 'content/baselines.json')
            (site.parent / sources.PLAN).write_text(PLAN, encoding='utf-8')
            for base in sources.GUIDES.values():
                source = site.parent / (base + '.md')
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text('# 테스트 가이드\n\n## 첫 항목\n\n본문\n\n## 환경\n\n기준 내용\n', encoding='utf-8')
            sync.git('init', '--bare', str(remote), cwd=work)
            sync.git('init', '-b', 'main', cwd=site)
            sync.git('config', 'user.name', 'Sync Test', cwd=site)
            sync.git('config', 'user.email', 'test@example.invalid', cwd=site)
            sync.git('add', '.', cwd=site)
            sync.git('commit', '-m', 'fixture', cwd=site)
            sync.git('remote', 'add', 'origin', str(remote), cwd=site)
            sync.git('push', '-u', 'origin', 'main', cwd=site)
            state = site / '.sync-state'; state.mkdir()
            with patch.multiple(sync, SITE=site, STATE=state, REMOTE=str(remote), CACHE=work / 'build-cache'):
                published = sync.sync(publish=True)
                self.assertEqual(published['status'], 'pushed_waiting_for_pages')
                self.assertIn('기준 내용', (site / 'docs/guides/seohee.html').read_text(encoding='utf-8'))
                first_commit = sync.git('rev-parse', 'HEAD')
                # Verify HTML changes take effect and subsequent invalid input cannot reach the remote.
                source = site.parent / (sources.GUIDES['seohee'] + '.html')
                source.write_text('<main><h2 id="section-1">첫 항목</h2><p>HTML 변경 내용</p><h2 id="section-2">환경</h2></main>', encoding='utf-8')
                second = sync.sync(publish=True)
                self.assertNotEqual(first_commit, second['last_commit'])
                self.assertIn('HTML 변경 내용', (site / 'docs/guides/seohee.html').read_text(encoding='utf-8'))
                commit = sync.git('rev-parse', 'HEAD')
                plan_path = site.parent / sources.PLAN
                plan_path.write_text('incomplete save', encoding='utf-8')
                with self.assertRaises(ValueError):
                    sync.sync(publish=True)
                self.assertEqual(sync.git('rev-parse', 'refs/heads/main', cwd=remote), commit)
                plan_path.write_text(PLAN.replace('기준 검증', '수정된 계획'), encoding='utf-8')
                (site / 'user-note.txt').write_text('keep this work', encoding='utf-8')
                with self.assertRaisesRegex(RuntimeError, 'uncommitted'):
                    sync.sync(publish=True)
                self.assertEqual(sync.git('rev-parse', 'refs/heads/main', cwd=remote), commit)
                self.assertEqual((site / 'user-note.txt').read_text(), 'keep this work')

if __name__ == '__main__':
    main()
