"""Run unmodified official verifiers, retaining commands, logs, hashes and results.

Default profile is FULL. Smoke is deliberately labelled incomplete coverage.
No submission is uploaded. Each verifier runs in its own process.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'vendor/competition'
VERIFIERS = VENDOR / 'verifiers'
TASKS = {'invsqrt': 'invsqrt/verify_submission_invsqrt.py',
         'dqi': 'dqi/verify_submission_dqi.py', 'dfthcsos': 'dfthcsos/verify.py'}

def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def relative(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(Path(path).resolve())

def fingerprint(paths):
    return [{'path': relative(p), 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in paths]

def execute(task, args, run_dir, log_dir):
    script = VERIFIERS / TASKS[task]
    submission = args.submission_root / (task if task == 'dfthcsos' else task + '.kmb')
    if task == 'invsqrt' and args.invsqrt_file:
        submission = args.invsqrt_file.resolve()
    # kickmix 1.0.0's Windows filename reader cannot open Unicode absolute
    # paths. ASCII relative paths retain the same files and verifier logic.
    command = [sys.executable, '-u', os.path.relpath(script, ROOT), os.path.relpath(submission, ROOT)]
    spawn_adapter = task == 'invsqrt' and args.invsqrt_workers > 1
    if spawn_adapter:
        command[2] = 'scripts/invsqrt_windows.py'
    if task in ('invsqrt', 'dqi'):
        command += ['--max-workers', str(args.invsqrt_workers if spawn_adapter else args.workers)]
    if args.profile == 'smoke':
        command += {'invsqrt': ['--max-x', '4096', '--shots-per-x', '64'],
                    'dqi': ['--num-shots', '4096'],
                    'dfthcsos': ['--shots-per-address', '1']}[task]
    log_file = log_dir / (task + '.log')
    result_file = run_dir / (task + '.json')
    record = {'task': task, 'profile': args.profile, 'status': 'RUNNING',
              'verification_scope': 'official default coverage' if args.profile == 'full' else 'reduced smoke coverage; not full verification',
              'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'command': command, 'working_directory': str(ROOT),
              'input': relative(submission), 'log': relative(log_file),
              'salt': '', 'seed': 'official hash-derived default',
              'python': sys.version, 'platform': platform.platform(),
              'original_verifier_modified': False,
              'execution_adapter': 'Windows spawn; identical official tasks and seeds' if spawn_adapter else None}
    def save():
        result_file.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    save()
    start = time.monotonic()
    try:
        files = sorted(submission.glob('*')) if submission.is_dir() else [submission]
        record['input_files'] = fingerprint([p for p in files if p.is_file()])
        source_files = sorted(VERIFIERS.rglob('*.py'))
        record['verifier_sources'] = fingerprint(source_files)
        if spawn_adapter:
            record['execution_adapter_source'] = fingerprint([ROOT / 'scripts/invsqrt_windows.py'])
        save()
        print(f'[{task}] starting {args.profile}; log={log_file}', flush=True)
        child_env = os.environ.copy()
        child_env.update(PYTHONUTF8='1', OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2')
        if spawn_adapter:
            progress = run_dir / 'invsqrt-progress'
            progress.mkdir()
            child_env['WEEK1_PROGRESS_DIR'] = str(progress)
        with log_file.open('w', encoding='utf-8') as log:
            proc = subprocess.Popen(command, cwd=ROOT, env=child_env, stdout=log, stderr=subprocess.STDOUT)
            record['pid'] = proc.pid
            save()
            returncode = proc.wait()
        record['exit_code'] = returncode
        output = log_file.read_text(encoding='utf-8', errors='replace')
        try:
            summary = json.loads(output)
        except json.JSONDecodeError:
            summary = {'status': 'ERROR', 'error': 'Verifier did not produce a JSON result. See the raw log.'}
        record['official_result'] = summary
        record['status'] = 'PASS' if returncode == 0 and summary.get('status') == 'PASS' else 'FAIL'
    except Exception as exc:
        record.update(status='ERROR', error=f'{type(exc).__name__}: {exc}')
    record['elapsed_seconds'] = round(time.monotonic() - start, 3)
    record['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    save()
    print(f'[{task}] {record["status"]} ({record["elapsed_seconds"]:.1f}s)', flush=True)
    return record

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tasks', nargs='+', choices=list(TASKS), default=list(TASKS))
    p.add_argument('--profile', choices=['full', 'smoke'], default='full')
    p.add_argument('--parallel', type=int, choices=[1, 2, 3], default=1)
    p.add_argument('--workers', type=int, default=1, help='Official verifier workers; Windows uses serial fallback.')
    p.add_argument('--invsqrt-workers', type=int, default=1, help='Use the optional spawn scheduler for invsqrt; original tasks/seeds preserved.')
    p.add_argument('--submission-root', type=Path, default=VENDOR / 'sample_submission')
    p.add_argument('--invsqrt-file', type=Path, help='Validate an invsqrt candidate; recorded as its actual path.')
    args = p.parse_args()
    if args.workers < 1 or args.invsqrt_workers < 1:
        p.error('--workers must be positive')
    args.submission_root = args.submission_root.resolve()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + args.profile
    run_dir, log_dir = ROOT / 'reports/runs' / run_id, ROOT / 'logs' / run_id
    run_dir.mkdir(parents=True)
    log_dir.mkdir(parents=True)
    index = {'run_id': run_id, 'profile': args.profile, 'tasks': args.tasks,
             'run_directory': relative(run_dir), 'status': 'RUNNING', 'results': []}
    latest = ROOT / 'reports' / ('latest-' + args.profile + '.json')
    def save_index():
        body = json.dumps(index, indent=2, ensure_ascii=False)
        (run_dir / 'index.json').write_text(body, encoding='utf-8')
        latest.write_text(body, encoding='utf-8')
    save_index()
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(execute, task, args, run_dir, log_dir) for task in dict.fromkeys(args.tasks)]
        for f in as_completed(futures):
            index['results'].append(f.result())
            save_index()
    index['status'] = 'PASS' if all(x['status'] == 'PASS' for x in index['results']) else 'FAIL'
    save_index()
    rows = ['# Verification run', '', f'Profile: **{args.profile}**. Status: **{index["status"]}**.', '',
            'These are local official-verifier results, not a Kaggle leaderboard score.', '',
            '| Task | Status | Official cost | Shots | Elapsed seconds |', '|---|---|---:|---:|---:|']
    for r in sorted(index['results'], key=lambda x: x['task']):
        s = r.get('official_result', {})
        rows.append(f'| {r["task"]} | {r["status"]} | {s.get("score", "—")} | {s.get("verified_shots", "—")} | {r["elapsed_seconds"]} |')
    if args.profile == 'smoke':
        rows += ['', '**Reduced test coverage. A smoke PASS is not a full PASS.**']
    (run_dir / 'summary.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'Results: {run_dir}', flush=True)
    return 0 if index['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
