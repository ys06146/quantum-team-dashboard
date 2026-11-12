"""Guard the shared progress calculation and initialization contract."""
from pathlib import Path
from unittest import TestCase
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from weekly_progress import completion,validate_data

class ProgressTests(TestCase):
    def test_completion_counts_unique_confirmed_items(self):
        self.assertEqual(completion([])['percent'],0)
        self.assertEqual(completion(['work'])['percent'],25)
        self.assertEqual(completion(['work','validation'])['percent'],50)
        self.assertEqual(completion(['work','output','validation','handoff'])['percent'],100)

    def test_invalid_or_duplicate_items_cannot_inflate_percentage(self):
        for value in [['work','work'],['unknown'],None,'work',[True]]:
            with self.assertRaises(ValueError):completion(value)

    def test_board_requires_all_fifteen_assignments(self):
        data=json.loads((ROOT/'content/progress.json').read_text(encoding='utf-8'))
        plan=json.loads((ROOT/'content/tasks.json').read_text(encoding='utf-8'))
        people=[(slug,name) for slug,name in [('soyeon','소연'),('jiwoo','지우'),('yechan','예찬'),('seojin','서진'),('seohee','서희')]]
        validate_data(data,plan,people)
        self.assertEqual(len(data['tasks']),15)
        invalid=copy.deepcopy(data);del invalid['tasks']['e3']
        with self.assertRaises(ValueError):validate_data(invalid,plan,people)
