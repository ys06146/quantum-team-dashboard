"""Run the official invsqrt CLI with Windows spawn scheduling.

Only _run_parallel scheduling is replaced. Each child invokes the same original
CLI, reconstructs the original closure, checks the exact task tuples (including
RNG seeds), then runs a disjoint slice. The parent official verifier aggregates
the original ordered results. No checks, shots, batches or cost formulas change.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor/competition/verifiers/invsqrt'))
CLI_ARGS = []

class SliceDone(BaseException):
    def __init__(self, results):
        self.results = results

def run_slice(job):
    import verify_submission_invsqrt as official
    cli, start, stop, expected = job
    sys.argv = ['verify_submission_invsqrt.py', *cli]
    progress = os.environ.get('WEEK1_PROGRESS_DIR')
    def capture(fn, tasks, max_workers):
        selected = tasks[start:stop]
        if selected != expected:
            raise RuntimeError('Worker tasks or seeds differ from the original parent verifier')
        results = []
        def save():
            if progress:
                Path(progress, f'worker-{start}.json').write_text(json.dumps({
                    'pid': os.getpid(), 'first_chunk': start, 'stop_chunk': stop,
                    'completed_chunks': len(results), 'total_chunks': len(selected)
                }), encoding='utf-8')
        save()
        for task in selected:
            results.append(fn(task))
            if len(results) % 8 == 0:
                save()
        save()
        raise SliceDone(results)
    official._run_parallel = capture
    try:
        official.main()
    except SliceDone as done:
        return done.results
    raise RuntimeError('Worker did not reach official verification scheduler')

def spawn_parallel(fn, tasks, max_workers):
    workers = min(len(tasks), max_workers or 1)
    if workers <= 1:
        return [fn(t) for t in tasks]
    jobs = []
    for i in range(workers):
        start, stop = len(tasks) * i // workers, len(tasks) * (i + 1) // workers
        jobs.append((CLI_ARGS, start, stop, tasks[start:stop]))
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('spawn')) as pool:
        slices = list(pool.map(run_slice, jobs))
    return [result for part in slices for result in part]

def main():
    global CLI_ARGS
    import verify_submission_invsqrt as official
    CLI_ARGS = sys.argv[1:]
    official._run_parallel = spawn_parallel
    official.main()

if __name__ == '__main__':
    main()
