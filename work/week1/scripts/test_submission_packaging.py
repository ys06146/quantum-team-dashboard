"""Guardrail tests for malformed submission archives; uses tiny synthetic payloads."""
import io,tempfile,unittest,zipfile
from pathlib import Path
from build_submission import layout,inspect_zip,NPZ_KEYS
def npz():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        for n in NPZ_KEYS:z.writestr(n,b"fixture-key-check-only")
    return b.getvalue()
class SubmissionTests(unittest.TestCase):
    def good(self):return ["invsqrt.kmb","dqi.kmb","dfthcsos/submission.npz","dfthcsos/angle_k_0.kmb"]
    def test_valid_layout(self):self.assertEqual(layout(self.good())["angle_count"],1)
    def test_missing_root(self):
        with self.assertRaises(ValueError):layout(self.good()[1:])
    def test_angle_gap(self):
        with self.assertRaises(ValueError):layout(self.good()+["dfthcsos/angle_k_2.kmb"])
    def test_duplicate_circuit_formats(self):
        with self.assertRaises(ValueError):layout(self.good()+["invsqrt.kmx"])
    def test_duplicate_member(self):
        with self.assertRaises(ValueError):layout(self.good()+["dqi.kmb"])
    def test_path_traversal(self):
        with self.assertRaises(ValueError):layout(self.good()+["../outside"])
    def test_unexpected_file(self):
        with self.assertRaises(ValueError):layout(self.good()+["desktop.ini"])
    def archive(self,path,missing_npz=False):
        with zipfile.ZipFile(path,"w") as z:
            for n in self.good():z.writestr(n,b"invalid-npz" if missing_npz and n.endswith(".npz") else npz() if n.endswith(".npz") else b"fixture")
    def test_archive_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"tiny.zip";self.archive(f)
            record=inspect_zip(f)["members"];record["dqi.kmb"]["sha256"]="0"*64
            with self.assertRaises(ValueError):inspect_zip(f,record)
    def test_corrupt_npz(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"tiny.zip";self.archive(f,True)
            with self.assertRaises(zipfile.BadZipFile):inspect_zip(f)
if __name__=="__main__":unittest.main(verbosity=2)

