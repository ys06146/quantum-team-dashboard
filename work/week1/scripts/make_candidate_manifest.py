"""Create a provisional candidate handoff from a real smoke/full verification record."""
import argparse
import json
from pathlib import Path
from check_candidate_handoff import ROOT, validate

def main():
    if not __debug__:raise RuntimeError("Validation requires Python without -O/-OO")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--producer", required=True)
    parser.add_argument("--change", required=True)
    parser.add_argument("--generation-command", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    path = (ROOT / args.record).resolve()
    if not path.is_relative_to(ROOT):raise ValueError("Record outside workspace")
    rec = json.loads(path.read_text(encoding="utf-8"))
    body = {"schema_version": 1, "experiment_id": args.id, "task": rec["task"], "producer": args.producer,
            "change": args.change, "generation_command": args.generation_command,
            "files": rec["input_files"], "environment": {k: rec[k] for k in ("python", "platform")},
            "model_evidence": [], "verification": {"stage": rec["profile"], "status": rec["status"], "record": args.record},
            "human_review": {"status": "PENDING", "reviewer": None, "reviewed_at": None},
            "interface_agreement": "PROVISIONAL_UNTIL_2026-11-15"}
    validate(body)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(body, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(args.output)

if __name__ == "__main__":main()
