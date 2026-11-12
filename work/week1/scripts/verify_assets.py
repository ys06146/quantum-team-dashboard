"""Check every supplied file against the downloaded competition ZIP, without editing it."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest_file(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    archive = ROOT / 'data/competition.zip'
    vendor = ROOT / 'vendor/competition'
    rows = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            with z.open(info) as f:
                expected = hashlib.file_digest(f, 'sha256').hexdigest()
            path = vendor / info.filename
            actual = digest_file(path) if path.is_file() else None
            rows.append({'path': info.filename, 'bytes': info.file_size,
                         'archive_sha256': expected, 'extracted_sha256': actual,
                         'status': 'PASS' if expected == actual else 'FAIL'})
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'source': 'https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data',
              'archive': 'data/competition.zip', 'archive_bytes': archive.stat().st_size,
              'archive_sha256': digest_file(archive), 'files_checked': len(rows),
              'status': 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'FAIL',
              'files': rows}
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/official_assets.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"Official archive integrity: {result['status']} ({len(rows)} files)")
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
