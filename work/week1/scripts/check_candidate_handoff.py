"""Validate a candidate handoff manifest without inventing verification or reviewer approval."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(manifest,root=ROOT):
    if not __debug__:raise RuntimeError("Validation requires Python without -O/-OO")
    assert manifest["schema_version"]==1
    task=manifest["task"]
    assert task in ("invsqrt","dqi","dfthcsos")
    for key in ("experiment_id","producer","change","generation_command"):
        assert isinstance(manifest.get(key),str) and manifest[key].strip(),key
    root=root.resolve()
    files=manifest["files"]
    assert files and len({f["path"] for f in files})==len(files),"Missing or duplicate files"
    for item in files:
        path=(root/item["path"]).resolve()
        assert not Path(item["path"]).is_absolute() and path.is_relative_to(root),"File must stay in common workspace"
        assert path.is_file(),str(path)
        with path.open("rb") as f:actual=hashlib.file_digest(f,"sha256").hexdigest()
        assert actual==item["sha256"],"Hash mismatch: "+item["path"]
    v=manifest["verification"]
    assert v["stage"] in ("smoke","full","not_run"),"Model-only evidence is separate from official verification"
    assert v["status"] in ("PASS","FAIL","NOT_RUN")
    assert (v["stage"]=="not_run")== (v["status"]=="NOT_RUN"),"Stage/status mismatch"
    if v["status"]=="PASS":
        recpath=(root/v["record"]).resolve()
        assert recpath.is_relative_to(root),"Record outside workspace"
        rec=json.loads(recpath.read_text(encoding="utf-8"))
        assert rec["task"]==task and rec["profile"]==v["stage"] and rec["status"]=="PASS"
        assert rec["official_result"]["status"]=="PASS"
        assert rec["exit_code"]==0,"Failed process cannot supply PASS evidence"
        evidence={f["path"]:f["sha256"] for f in rec["input_files"]}
        assert {f["path"]:f["sha256"] for f in files}==evidence,"File bundle does not match PASS record"
    assert manifest["human_review"]["status"] in ("PENDING","APPROVED","REJECTED")
    if manifest["human_review"]["status"]!="PENDING":
        assert manifest["human_review"].get("reviewer") and manifest["human_review"].get("reviewed_at"),"Reviewer/date required"
    return {"status":"PASS","task":task,"experiment_id":manifest["experiment_id"],"files":len(files),
            "verification":v,"human_review":manifest["human_review"],
            "meaning":"Manifest consistency only. Human review status is supplied, not independently certified."}
def main():
    if not __debug__:raise RuntimeError("Validation requires Python without -O/-OO")
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest",type=Path)
    args=ap.parse_args()
    print(json.dumps(validate(json.loads(args.manifest.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
if __name__=="__main__":main()

