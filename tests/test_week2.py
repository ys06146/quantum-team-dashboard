"""Guard the week-2 status data: ratios must reproduce the public score and dates must parse."""
from pathlib import Path
from unittest import TestCase
import copy, json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from week2_status import composite, validate

DATA = json.loads((ROOT / 'content/week2-status.json').read_text(encoding='utf-8'))


class Week2Tests(TestCase):
    def test_current_data_is_valid(self):
        validate(copy.deepcopy(DATA))

    def test_ratios_reproduce_public_score(self):
        self.assertAlmostEqual(composite(DATA['tasks']), DATA['score']['public_score'], places=3)

    def test_wrong_ratio_is_rejected(self):
        bad = copy.deepcopy(DATA)
        bad['tasks'][2]['ratio'] = 2.0
        with self.assertRaises(ValueError):
            validate(bad)

    def test_missing_task_is_rejected(self):
        bad = copy.deepcopy(DATA)
        del bad['tasks'][1]
        with self.assertRaises(ValueError):
            validate(bad)

    def test_unsorted_deadlines_are_rejected(self):
        bad = copy.deepcopy(DATA)
        bad['deadlines'].reverse()
        with self.assertRaises(ValueError):
            validate(bad)
