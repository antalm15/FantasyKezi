import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sync_mksz import extract_fixtures

class SyncTests(unittest.TestCase):
    def test_one_fixture(self):
        t='''2026.10.17. 18:00 | 7. forduló
K&H Férfi Liga | Aréna | ETO University HT Budai Farkasok-Rév | - | OnlineJegyzőkönyv
2026.10.22. 18:00 | 8. forduló
K&H Férfi Liga | x'''
        a=extract_fixtures(t,'2026-10-12')
        self.assertEqual(len(a),1)
        self.assertEqual({a[0]['home'],a[0]['away']},{'ETO','BFR'})
    def test_no_womens_fixtures(self):
        t='2026.10.17. 18:00\nK&H Női Liga | NEKA FTC | 34:30'
        self.assertEqual(extract_fixtures(t,'2026-10-12'),[])
    def test_no_future(self):
        t='2026.10.24. 18:00\nK&H Férfi Liga | ONE Veszprém HC PICK Szeged'
        self.assertEqual(extract_fixtures(t,'2026-10-12'),[])
    def test_no_unknown_team(self):
        t='2026.10.17. 18:00\nK&H Férfi Liga | Unknown Squad PICK Szeged'
        self.assertEqual(extract_fixtures(t,'2026-10-12'),[])
    def test_not_monday(self):
        with self.assertRaises(ValueError):extract_fixtures('', '2026-10-13')

if __name__=='__main__':unittest.main()
