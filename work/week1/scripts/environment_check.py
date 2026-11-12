"""Check the pinned runtime and save machine-readable environment information."""
import importlib.metadata as md
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    import kickmix as km
    import numpy as np
    import scipy
    expected = {'kickmix': '1.0.0', 'numpy': '2.2.6', 'scipy': '1.15.3'}
    versions = {name: md.version(name) for name in expected}
    assert versions == expected, (versions, expected)
    assert sys.version_info[:2] == (3, 12), sys.version
    # A real simulator operation, not just an import check.
    builder = km.CircuitBuilder()
    q = builder.create_quantum_register(1, name='x')
    builder.x(q)
    circuit = builder.finish_circuit()
    sim = km.Simulator(batch_size=64)
    sim.do(circuit)
    assert np.all(sim.read_across_shots(q))
    result = {'status': 'PASS', 'python': sys.version, 'executable': sys.executable,
              'platform': platform.platform(), 'packages': versions,
              'kickmix_module': km.__file__, 'simulator_test': 'X on 64 zero-initialized shots'}
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/environment.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    frozen = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True)
    (ROOT / 'requirements.lock.txt').write_text(frozen, encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
