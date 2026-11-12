import copy, hashlib, json, tempfile, unittest
from pathlib import Path
from check_candidate_handoff import validate

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "circuit.kmb").write_bytes(b"test circuit")
        self.item = {"path": "circuit.kmb", "sha256": hashlib.sha256(b"test circuit").hexdigest()}
        self.record = {"task": "dqi", "profile": "full", "status": "PASS", "exit_code": 0,
                       "official_result": {"status": "PASS"}, "input_files": [self.item]}
        self.save_record()
        self.manifest = {"schema_version": 1, "task": "dqi", "experiment_id": "test", "producer": "test",
                         "change": "fixture", "generation_command": "fixture", "files": [copy.deepcopy(self.item)],
                         "verification": {"stage": "full", "status": "PASS", "record": "record.json"},
                         "human_review": {"status": "PENDING"}}
    def save_record(self):
        (self.root / "record.json").write_text(json.dumps(self.record), encoding="utf-8")
    def rejected(self):
        with self.assertRaises(AssertionError):validate(self.manifest, self.root)
    def test_evidence(self):self.assertEqual(validate(self.manifest, self.root)["status"], "PASS")
    def test_changed_bytes(self):
        (self.root / "circuit.kmb").write_bytes(b"changed")
        self.rejected()
    def test_smoke_cannot_be_full(self):
        self.record["profile"] = "smoke"
        self.save_record()
        self.rejected()
    def test_failed_exit(self):
        self.record["exit_code"] = 1
        self.save_record()
        self.rejected()
    def test_different_input(self):
        self.record["input_files"] = []
        self.save_record()
        self.rejected()
    def test_outside_path(self):
        self.manifest["files"][0]["path"] = "../outside.kmb"
        self.rejected()
    def test_review_needs_name(self):
        self.manifest["human_review"]["status"] = "APPROVED"
        self.rejected()
    def test_model_is_not_official_pass(self):
        self.manifest["verification"]["stage"] = "model"
        self.rejected()

if __name__ == "__main__":unittest.main()
