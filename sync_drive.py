"""One bounded Drive-to-Pages sync run, invoked by Windows Task Scheduler."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
import argparse
import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

from drive_sources import VERSION, import_documents, snapshot

SITE = Path(__file__).resolve().parent
STATE = SITE / '.sync-state'
CACHE = Path(os.environ.get('LOCALAPPDATA', tempfile.gettempdir())) / 'QuantumTeamDashboard' / 'builds'
REMOTE = 'https://github.com/ys06146/quantum-team-dashboard.git'
PUBLIC = 'https://ys06146.github.io/quantum-team-dashboard/'
# pythonw has no console, so each console child (git.exe) would otherwise flash a new cmd window.
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16}|AIza[A-Za-z0-9_-]{30,}')

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)

def git(*args, cwd=None):
    executable = shutil.which('git') or str(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/cmd/git.exe')
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
    result = subprocess.run([executable, *args], cwd=cwd or SITE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120, creationflags=NO_WINDOW)
    if result.returncode:
        raise RuntimeError('git ' + args[0] + ' failed: ' + (result.stderr or result.stdout)[-1600:])
    return result.stdout.strip()

@contextmanager
def exclusive_lock(path):
    with path.open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        try:
            yield True
        finally:
            lock.seek(0)
            if os.name == 'nt':
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)

def hashes(current):
    return {path: value['hash'] for path, value in current.items()}

def engine_hash():
    files = [SITE / name for name in ('build.py', 'drive_sources.py', 'sync_drive.py', 'public_results.py', 'weekly_progress.py')] + sorted((SITE / 'assets').glob('*'))
    return hashlib.sha256(b''.join(p.read_bytes() for p in files if p.is_file() and p.name != 'desktop.ini')).hexdigest()

def run_build(checkout):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(checkout / 'build.py')], cwd=checkout, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60, creationflags=NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Document validation failed: ' + (result.stderr or result.stdout)[-1600:])
    for parent in ['content', 'docs']:
        for path in (checkout / parent).rglob('*'):
            if path.is_file() and path.suffix in ('.html', '.md', '.json', '.js', '.css'):
                if SECRET.search(path.read_text(encoding='utf-8')):
                    raise ValueError('A credential-like value was found; publication stopped: ' + path.relative_to(checkout).as_posix())
    return result.stdout.strip()

def prepare_checkout(checkout, current, state):
    selected = import_documents(checkout, current, state)
    validation = run_build(checkout)
    return selected, validation

def reconcile_repo():
    if git('branch', '--show-current') != 'main':
        raise RuntimeError('Switch the dashboard repository back to main before auto-sync.')
    if git('remote', 'get-url', 'origin') != REMOTE:
        raise RuntimeError('The configured GitHub destination has changed; sync stopped.')
    if git('status', '--porcelain'):
        raise RuntimeError('The dashboard repository has uncommitted edits. Commit or resolve them; Drive originals are untouched.')
    git('fetch', '--quiet', 'origin', 'main')
    ahead, behind = map(int, git('rev-list', '--left-right', '--count', 'HEAD...origin/main').split())
    if ahead:
        raise RuntimeError('The dashboard repository has unpushed commits. Push them before auto-sync.')
    if behind:
        git('merge', '--ff-only', 'origin/main')
        return False  # Reload a possibly changed importer on the next scheduled run.
    return True

def sync(publish=False, force=False):
    previous_path = STATE / 'state.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
    current = snapshot(SITE.parent)
    time.sleep(2)  # A second content read protects against partially written/syncing files.
    if hashes(current) != hashes(snapshot(SITE.parent)):
        return {'status': 'waiting_for_stable_files'}
    current_hashes, engine = hashes(current), engine_hash()
    same = current_hashes == previous.get('hashes') and engine == previous.get('engine')
    if same and not force:
        result = {'status': 'unchanged', 'last_commit': previous.get('last_commit'), 'pages_confirmed': previous.get('pages_confirmed', False)}
        if previous.get('revision') and not result['pages_confirmed']:
            with urlopen(Request(PUBLIC + 'data/sync-info.json', headers={'Cache-Control': 'no-cache'}), timeout=20) as response:
                live = json.load(response)
            if live.get('revision') == previous['revision']:
                previous['pages_confirmed'] = True
                atomic_json(previous_path, previous)
                result['pages_confirmed'] = True
                logging.info('GitHub Pages confirmed: %s', previous.get('last_commit'))
            else:
                result['status'] = 'waiting_for_pages'
        return result
    if publish and not reconcile_repo():
        return {'status': 'repository_updated_retry_next_run'}
    CACHE.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.TemporaryDirectory(prefix='build-', dir=CACHE)
    candidate = Path(temporary.name).resolve()
    assert candidate.is_relative_to(CACHE.resolve()), 'Temporary cleanup must stay inside the local build cache.'
    with temporary:
        checkout = candidate / 'site'
        if publish:
            git('clone', '--quiet', '--no-hardlinks', str(SITE), str(checkout))
            git('remote', 'set-url', 'origin', REMOTE, cwd=checkout)
            for key in ('user.name', 'user.email'):
                git('config', key, git('config', '--get', key), cwd=checkout)
        else:
            checkout.mkdir()
            for name in ('assets', 'content'):
                shutil.copytree(SITE / name, checkout / name, ignore=shutil.ignore_patterns('desktop.ini'))
            shutil.copyfile(SITE / 'build.py', checkout / 'build.py')
            shutil.copyfile(SITE / 'drive_sources.py', checkout / 'drive_sources.py')
            for name in ('public_results.py', 'weekly_progress.py'):
                if (SITE / name).is_file():
                    shutil.copyfile(SITE / name, checkout / name)
        selected, validation = prepare_checkout(checkout, current, previous)
        changes = git('status', '--porcelain', '--', 'content', 'docs', cwd=checkout) if publish else 'preview'
        commit, revision = previous.get('last_commit'), previous.get('revision')
        if publish and changes:
            revision = hashlib.sha256(json.dumps(current_hashes, sort_keys=True).encode() + engine.encode()).hexdigest()
            info = {'updated_at': now(), 'revision': revision, 'source': 'Google Drive team documents', 'guide_formats': {slug: Path(source).suffix[1:] for slug, source in selected.items()}}
            atomic_json(checkout / 'content/sync-info.json', info)
            validation = run_build(checkout)
            # Re-read immediately before committing; do not publish an older in-flight save.
            if current_hashes != hashes(snapshot(SITE.parent)):
                return {'status': 'waiting_for_stable_files'}
            git('add', '--', 'content', 'docs', cwd=checkout)
            git('commit', '--quiet', '-m', 'Sync plan and guides from Drive', cwd=checkout)
            commit = git('rev-parse', 'HEAD', cwd=checkout)
            # A normal push rejects concurrent remote changes. There is no force push.
            git('push', 'origin', 'HEAD:main', cwd=checkout)
            logging.info('Published source commit %s; %s', commit, validation)
            if not git('status', '--porcelain'):
                git('fetch', '--quiet', 'origin', 'main')
                git('merge', '--ff-only', 'origin/main')
        if publish:
            atomic_json(previous_path, {'version': VERSION, 'hashes': current_hashes, 'selected': selected, 'engine': engine,
                                      'last_commit': commit, 'revision': revision, 'pages_confirmed': not bool(changes) and previous.get('pages_confirmed', False), 'completed_at': now()})
        return {'status': ('pushed_waiting_for_pages' if changes else 'source_checked_no_page_change') if publish else 'preview_passed',
                'selected': selected, 'validation': validation, 'last_commit': commit}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Commit validated document changes and push to GitHub.')
    parser.add_argument('--force', action='store_true', help='Rebuild even if source hashes have not changed.')
    parser.add_argument('--status', action='store_true', help='Print the last local status without running sync.')
    args = parser.parse_args()
    STATE.mkdir(exist_ok=True)
    if args.status:
        path = STATE / 'status.json'
        if sys.stdout:
            print(path.read_text(encoding='utf-8') if path.exists() else '{"status":"not_run"}')
        return 0
    logging.basicConfig(level=logging.INFO, handlers=[RotatingFileHandler(STATE / 'sync.log', maxBytes=1_000_000, backupCount=2, encoding='utf-8')], format='%(asctime)s %(levelname)s %(message)s')
    with exclusive_lock(STATE / 'sync.lock') as acquired:
        if not acquired:
            return 0
        try:
            result = sync(args.publish, args.force)
            result['checked_at'] = now()
            atomic_json(STATE / 'status.json', result)
            if sys.stdout:
                print(json.dumps(result, ensure_ascii=False))
            return 0
        except Exception as error:
            message = str(error)
            logging.error('%s', message)
            atomic_json(STATE / 'status.json', {'status': 'error', 'checked_at': now(), 'error': message})
            if sys.stderr:
                print(message, file=sys.stderr)
            return 1

if __name__ == '__main__':
    raise SystemExit(main())
