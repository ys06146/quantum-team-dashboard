"""Predeclared robustness draws; unchanged official verifier and full coverage."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SALTS=('jjeya-dqi-public-20261111-a','jjeya-dqi-public-20261111-b')
candidate=ROOT/'artifacts/candidates/dqi-public-syed-v11/dqi.kmb'
verifier=ROOT/'vendor/competition/verifiers/dqi/verify_submission_dqi.py'
out=ROOT/'reports/dqi-public-syed-v11-robustness'
out.mkdir(exist_ok=True)
plan={'salts':SALTS,'declared_at_utc':datetime.now(timezone.utc).isoformat(),'circuit_sha256':hashlib.file_digest(candidate.open('rb'),'sha256').hexdigest(),'verifier_sha256':hashlib.file_digest(verifier.open('rb'),'sha256').hexdigest(),'num_shots_each':102400,'purpose':'Independent predeclared draws, not seed selection; all results retained.'}
(out/'plan.json').write_text(json.dumps(plan,indent=2))
results=[]
for salt in SALTS:
    command=[sys.executable,'-u',str(verifier),str(candidate),'--max-workers','4','--salt',salt]
    start=time.monotonic()
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',MKL_NUM_THREADS='2')
    run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True)
    (out/(salt+'.log')).write_text(run.stdout+run.stderr)
    try: result=json.loads(run.stdout)
    except json.JSONDecodeError: result={'status':'ERROR','output':run.stdout[-1500:]}
    record={'salt':salt,'exit_code':run.returncode,'command':command,'elapsed_seconds':round(time.monotonic()-start,3),'official_result':result}
    (out/(salt+'.json')).write_text(json.dumps(record,indent=2))
    results.append(record)
    print(json.dumps({'salt':salt,**{k:result.get(k) for k in ('status','score','value_errors','phase_errors','verified_shots')}}),flush=True)
(out/'summary.json').write_text(json.dumps({'plan':plan,'results':results},indent=2))
raise SystemExit(0 if all(r['exit_code']==0 and r['official_result'].get('status')=='PASS' for r in results) else 1)
