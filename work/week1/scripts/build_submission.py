"""Build and verify a submission ZIP, binding every entry to full-PASS evidence.
No upload is performed. The ZIP contains only official submission files; receipts stay outside it.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NPZ_KEYS={"U.npy","W.npy","H2_I.npy","H1_I.npy","Hsym_lower.npy","tree_edges.npy"}

def digest(stream):
    return hashlib.file_digest(stream,"sha256").hexdigest()

def layout(names):
    names=list(names)
    if len(names)!=len(set(names)) or len(names)!=len({n.casefold() for n in names}):
        raise ValueError("Duplicate or case-colliding archive names")
    for n in names:
        p=PurePosixPath(n)
        if "\\" in n or p.is_absolute() or ".." in p.parts or ":" in n or str(p)!=n:
            raise ValueError("Unsafe or noncanonical archive path: "+n)
    tops=[]
    for task in ("invsqrt","dqi"):
        found=[n for n in names if n in (task+".kmb",task+".kmx")]
        if len(found)!=1:
            raise ValueError("Exactly one circuit required for "+task)
        tops.extend(found)
    if "dfthcsos/submission.npz" not in names:
        raise ValueError("Missing dfthcsos/submission.npz")
    angles={}
    for n in names:
        match=re.fullmatch(r"dfthcsos/angle_k_(0|[1-9]\d*)\.(kmb|kmx)",n)
        if match:
            index=int(match[1])
            if index in angles: raise ValueError("Duplicate ANGLE index")
            angles[index]=n
    if not angles or sorted(angles)!=list(range(len(angles))):
        raise ValueError("ANGLE indices must be contiguous from zero")
    expected=set(tops+list(angles.values())+["dfthcsos/submission.npz"])
    if set(names)!=expected:
        raise ValueError("Unexpected submission members: "+str(sorted(set(names)-expected)))
    return {"angle_count":len(angles),"entry_count":len(names)}

def check_npz(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if len(z.namelist())!=len(set(z.namelist())):
            raise ValueError("Duplicate NPZ array")
        missing=NPZ_KEYS-set(z.namelist())
        if missing: raise ValueError("Missing NPZ arrays: "+str(sorted(missing)))
        bad=z.testzip()
        if bad: raise ValueError("Corrupt NPZ array: "+bad)

def evidence(manifest_path):
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    expected={}
    refs={}
    for task in ("invsqrt","dqi","dfthcsos"):
        record_path=(ROOT/manifest[task]["record"]).resolve()
        record=json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("profile")!="full" or record.get("status")!="PASS" or record.get("official_result",{}).get("status")!="PASS" or record.get("exit_code")!=0:
            raise ValueError("Not full PASS evidence: "+str(record_path))
        inputs=record.get("input_files",[])
        if not inputs: raise ValueError("Missing input fingerprints for "+task)
        for item in inputs:
            name=Path(item["path"]).name
            dest="dfthcsos/"+name if task=="dfthcsos" else name
            if dest in expected: raise ValueError("Duplicate evidence member")
            expected[dest]={"bytes":item["bytes"],"sha256":item["sha256"]}
        refs[task]={"record":manifest[task]["record"],"record_sha256":digest(record_path.open("rb")),
                    "status":"PASS","profile":"full"}
    layout(expected)
    return expected,refs

def inspect_zip(archive, expected=None):
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        if any(i.is_dir() or i.flag_bits & 1 or ((i.external_attr>>16)&0o170000)==0o120000 for i in infos):
            raise ValueError("Directories, encryption or symlinks are not accepted")
        info=layout(i.filename for i in infos)
        members={}
        for i in infos:
            if i.file_size<=0: raise ValueError("Empty member: "+i.filename)
            with z.open(i) as f: sha=digest(f) # also checks CRC at end of each stream
            members[i.filename]={"bytes":i.file_size,"sha256":sha}
        check_npz(z.read("dfthcsos/submission.npz"))
    if expected is not None and members!=expected:
        raise ValueError("Archive bytes differ from full-PASS evidence/receipt")
    return {**info,"members":members}

def build(args):
    src=args.source_root.resolve()
    all_files={p.relative_to(src).as_posix():p for p in src.rglob("*") if p.is_file()}
    ignored=[n for n in all_files if PurePosixPath(n).name.casefold() in {"desktop.ini","thumbs.db",".ds_store"}]
    members={n:p for n,p in all_files.items() if n not in ignored}
    layout(members)
    expected,refs=evidence(args.evidence)
    if set(members)!=set(expected): raise ValueError("Source members differ from full-PASS evidence")
    out=args.output.resolve()
    receipt=out.with_suffix(".manifest.json")
    if out.exists() or receipt.exists():
        raise ValueError("Output already exists; use a new versioned output name")
    out.parent.mkdir(parents=True,exist_ok=True)
    temp=out.with_suffix(".zip.partial")
    if temp.exists(): raise ValueError("A partial build already exists; inspect it before retrying")
    try:
        with zipfile.ZipFile(temp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            for name in sorted(members):
                path=members[name]
                zi=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
                zi.compress_type=zipfile.ZIP_DEFLATED
                zi.external_attr=0o100644<<16
                hasher=hashlib.sha256()
                size=0
                with path.open("rb") as inp,z.open(zi,"w",force_zip64=True) as target:
                    while block:=inp.read(1024*1024):
                        target.write(block);hasher.update(block);size+=len(block)
                if {"bytes":size,"sha256":hasher.hexdigest()}!=expected[name]:
                    raise ValueError("Source changed or is not validated: "+name)
        check=inspect_zip(temp,expected)
        sha=digest(temp.open("rb"))
        payload={"schema_version":1,"kind":args.kind,"status":"PASS",
                 "checked_at_utc":datetime.now(timezone.utc).isoformat(),
                 "archive":out.name,"archive_bytes":temp.stat().st_size,"archive_sha256":sha,
                 "full_verifier_evidence":refs,"excluded_os_metadata":ignored,**check,
                 "scope":"ZIP layout, CRC, NPZ required keys and exact full-PASS input hashes. No upload or leaderboard result.",
                 "official_submission_format":"https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/overview"}
        os.replace(temp,out)
        receipt.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps({k:v for k,v in payload.items() if k!="members"},ensure_ascii=False,indent=2))
    except BaseException:
        if temp.exists():temp.unlink() # only this invocation's partial file
        raise

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest="action",required=True)
    b=sub.add_parser("build")
    b.add_argument("--source-root",type=Path,default=ROOT/"vendor/competition/sample_submission")
    b.add_argument("--evidence",type=Path,default=ROOT/"reports/baseline_manifest.json")
    b.add_argument("--output",type=Path,required=True)
    b.add_argument("--kind",default="week1_baseline_draft",help="Descriptive receipt category; does not affect validation.")
    c=sub.add_parser("check")
    c.add_argument("archive",type=Path)
    c.add_argument("--manifest",type=Path,required=True)
    args=ap.parse_args()
    if args.action=="build":build(args)
    else:
        receipt=json.loads(args.manifest.read_text(encoding="utf-8"))
        actual=digest(args.archive.open("rb"))
        if actual!=receipt["archive_sha256"]:raise ValueError("ZIP SHA-256 mismatch")
        info=inspect_zip(args.archive,receipt["members"])
        print(json.dumps({"status":"PASS","archive_sha256":actual,"entry_count":info["entry_count"],"angle_count":info["angle_count"]}))
if __name__=="__main__":main()

