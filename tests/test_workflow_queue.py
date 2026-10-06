"""Protect the shared single-writer queue from silently dropping other workflow runs."""
import unittest
from pathlib import Path


class WorkflowQueueTests(unittest.TestCase):
    def test_all_data_writers_keep_pending_runs_without_parallel_writes(self):
        root = Path(__file__).resolve().parents[1]
        for name in [p.name for p in (root / '.github/workflows').glob('*.yml')
                     if 'contents: write' in p.read_text()]:
            with self.subTest(workflow=name):
                workflow = (root / '.github/workflows' / name).read_text()
                self.assertIn('  group: tg-loi-all-writes-v3\n  queue: max\n  cancel-in-progress: false', workflow)
                self.assertIn('git fetch origin main', workflow)
                self.assertIn('git rev-parse origin/main', workflow)

    def test_only_offline_validation_and_rebuild_are_active(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual({p.name for p in (root / '.github/workflows').glob('*.yml')},
                         {'tg_loi_validate.yml', 'tg_loi_rebuild.yml'})
        rebuild = (root / '.github/workflows/tg_loi_rebuild.yml').read_text()
        self.assertIn('python -m unittest discover -s tests -v', rebuild)
        self.assertIn('python scripts/validate_tg_loi.py', rebuild)
        self.assertIn('python scripts/textile_scope.py', rebuild)
        self.assertNotIn('harvest_tg_loi.py', rebuild)
        self.assertNotIn('review_b_tg_loi.py', rebuild)
        self.assertNotIn('extract_tg_loi.py', rebuild)
        for name in ['tg_loi_harvest.yml', 'tg_loi_process.yml']:
            self.assertTrue((root / 'docs/archive/workflows' / name).is_file())


if __name__ == '__main__':
    unittest.main()
