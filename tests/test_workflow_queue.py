"""Protect the shared single-writer queue from silently dropping other workflow runs."""
import unittest
from pathlib import Path


class WorkflowQueueTests(unittest.TestCase):
    def test_all_data_writers_keep_pending_runs_without_parallel_writes(self):
        root = Path(__file__).resolve().parents[1]
        for name in ['tg_loi_harvest.yml', 'tg_loi_process.yml', 'tg_loi_rebuild.yml']:
            with self.subTest(workflow=name):
                workflow = (root / '.github/workflows' / name).read_text()
                self.assertIn('  group: tg-loi-all-writes-v3\n  queue: max\n  cancel-in-progress: false', workflow)
                self.assertIn('git fetch origin main', workflow)
                self.assertIn('git rev-parse origin/main', workflow)


if __name__ == '__main__':
    unittest.main()
