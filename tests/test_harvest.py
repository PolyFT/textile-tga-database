"""Offline regression coverage for discovery and evidence queue identity."""

from contextlib import ExitStack, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from scripts import harvest_tg_loi as harvest


def work(doi, identifier, title="Cotton fabric TGA and LOI"):
    return {
        "doi": doi,
        "id": identifier,
        "title": title,
        "publication_year": 2024,
        "primary_location": {
            "landing_page_url": "https://example.invalid/article",
            "source": {"display_name": "Fixture Journal"},
        },
    }


class HarvestTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out_dir = self.root / "data" / "automation"
        self.out_dir.mkdir(parents=True)
        self.out = self.out_dir / "candidate_extractions.csv"
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in {
            "ROOT": self.root,
            "OUT_DIR": self.out_dir,
            "OUT": self.out,
            "STATE": self.out_dir / "harvest_state.json",
            "SEARCH_TERMS": ["fixture query"],
        }.items():
            self.stack.enter_context(patch.object(harvest, name, value))
        self.stack.enter_context(patch.object(harvest.time, "sleep"))
        # Any unmocked HTTP request must fail rather than contact a live source.
        self.stack.enter_context(patch.object(
            harvest.requests.sessions.Session, "request",
            side_effect=AssertionError("Live network access is forbidden in harvest tests"),
        ))

    def run_harvest(self, works, *args):
        with (
            patch("sys.argv", ["harvest_tg_loi.py", "--queries-per-run", "1", *args]),
            patch.object(harvest, "openalex_search", return_value=(works, None)),
            patch.object(harvest, "europe_pmc_fulltext", return_value=(
                "Cotton fabric TGA. LOI 30%. Tmax 350 C. Residue 20%.",
                "https://example.invalid/fulltext",
            )) as fulltext,
            patch.object(harvest, "fetch_open_html", return_value=("", [], [])),
            patch.object(harvest, "fetch_supplements", return_value=("", [])),
            redirect_stdout(StringIO()),
        ):
            harvest.main()
        return fulltext

    def read_queue(self):
        return pd.read_csv(self.out, dtype=str).fillna("")

    def test_source_candidate_and_master_dois_do_not_suppress_discovery(self):
        paths = ["candidate_pool.csv", "literature_sources.csv", "tg_loi_master.csv"]
        dois = ["10.1234/candidate", "10.1234/source", "10.1234/master"]
        original = {}
        for filename, doi in zip(paths, dois):
            path = self.root / "data" / filename
            pd.DataFrame([{"DOI": doi, "sample_id": "partial-existing-state"}]).to_csv(path, index=False)
            original[path] = path.read_bytes()
        fulltext = self.run_harvest([
            work(f"https://doi.org/{doi}", f"https://openalex.org/W{i}")
            for i, doi in enumerate(dois)
        ])
        self.assertEqual(set(self.read_queue()["DOI"]), set(dois))
        self.assertEqual(fulltext.call_count, 3)
        for path, content in original.items():
            self.assertEqual(path.read_bytes(), content)

    def test_normalized_queue_dois_skip_fetch_and_deduplicate(self):
        pd.DataFrame([
            {"DOI": " HTTPS://DX.DOI.ORG/10.1234/QUEUED. ", "candidate_score": 20, "title": "Retained evidence"},
            {"DOI": "doi:10.1234/queued", "candidate_score": 8, "title": "Weaker evidence"},
        ]).to_csv(self.out, index=False)
        fulltext = self.run_harvest([
            work("10.1234/queued", "https://openalex.org/W1"),
            work("10.1234/new", "https://openalex.org/W2"),
        ])
        fulltext.assert_called_once_with("10.1234/new")
        queue = self.read_queue()
        self.assertEqual(len(queue), 2)
        retained = queue[queue["DOI"].map(harvest.norm_doi) == "10.1234/queued"].iloc[0]
        self.assertEqual(retained["title"], "Retained evidence")

    def test_doi_less_works_remain_distinct_and_skip_repeat_fetch(self):
        works = [
            work(None, "https://openalex.org/W1", "Cotton fabric TGA LOI one"),
            work(None, "https://openalex.org/W2", "Cotton fabric TGA LOI two"),
            work(None, "", "Cotton fabric TGA LOI title fallback"),
        ]
        first = self.run_harvest(works + [dict(works[0])])
        self.assertEqual(first.call_count, 3)
        self.assertEqual(len(self.read_queue()), 3)
        second = self.run_harvest(works)
        second.assert_not_called()
        self.assertEqual(len(self.read_queue()), 3)

    def test_unidentifiable_historical_rows_are_not_collapsed(self):
        previous = pd.DataFrame([
            {"DOI": None, "candidate_score": 5, "note": "first legacy row"},
            {"DOI": "", "candidate_score": 6, "note": "second legacy row"},
        ])
        queue = harvest.merge_candidates(previous, pd.DataFrame())
        self.assertEqual(len(queue), 2)
        self.assertEqual(set(queue["note"]), {"first legacy row", "second legacy row"})

    def test_identity_normalizes_doi_and_uses_openalex_then_title(self):
        self.assertEqual(harvest.norm_doi(float("nan")), "")
        self.assertEqual(
            harvest.candidate_key({"DOI": "doi: 10.1234/EXAMPLE;"}),
            harvest.candidate_key({"doi": "https://doi.org/10.1234/example"}),
        )
        self.assertEqual(
            harvest.candidate_key({"DOI": "", "openalex_id": "https://openalex.org/W123/"}),
            harvest.candidate_key({"doi": None, "id": "w123"}),
        )
        self.assertEqual(
            harvest.candidate_key({"title": " Cotton  fabric TGA ", "year": "2024"}),
            harvest.candidate_key({"title": "cotton fabric tga", "publication_year": 2024}),
        )

    def test_explicit_refresh_is_bounded_and_updates_one_snapshot(self):
        works = [work("10.1234/one", "W1"), work("10.1234/two", "W2")]
        self.run_harvest(works)
        refreshed = self.run_harvest(works, "--refresh-existing", "--max-new", "1")
        refreshed.assert_called_once_with("10.1234/one")
        queue = self.read_queue().set_index("DOI")
        self.assertEqual(len(queue), 2)
        self.assertEqual(queue.loc["10.1234/one", "harvest_run"], "2")
        self.assertEqual(queue.loc["10.1234/two", "harvest_run"], "1")

    def test_refresh_retains_prior_evidence_if_new_snapshot_loses_a_field(self):
        original = {
            "DOI": "10.1234/one", "candidate_score": 12,
            "fulltext_url": "https://example.invalid/original",
            "table_candidates": '["sample,LOI,Tmax\\ncotton,30,350"]',
            "LOI_numeric_evidence": '["LOI 30%"]',
            "harvest_run": 1,
        }
        for field in ("table_candidates", "fulltext_url", "LOI_numeric_evidence"):
            with self.subTest(field=field):
                refreshed = {**original, "candidate_score": 99, "harvest_run": 2, field: ""}
                queue = harvest.merge_candidates(pd.DataFrame([original]), pd.DataFrame([refreshed]))
                self.assertEqual(queue.iloc[0].to_dict(), original)

    def test_failed_refresh_attempts_are_also_bounded(self):
        works = [work("10.1234/one", "W1"), work("10.1234/two", "W2")]
        self.run_harvest(works)
        before = self.out.read_bytes()
        with patch.object(harvest, "score_candidate", return_value=(6, [], [])):
            refreshed = self.run_harvest(works, "--refresh-existing", "--max-new", "1")
        refreshed.assert_called_once_with("10.1234/one")
        self.assertEqual(self.out.read_bytes(), before)

    def test_refresh_keeps_curator_columns_and_accepts_complete_new_snapshot(self):
        original = {
            "DOI": "10.1234/one", "candidate_score": 12,
            "fulltext_url": "https://example.invalid/original",
            "table_candidates": '["old table"]', "curator_note": "Check sample state",
        }
        refreshed = {
            "DOI": "10.1234/one", "candidate_score": 14,
            "fulltext_url": "https://example.invalid/refreshed",
            "table_candidates": '["new complete table"]',
        }
        queue = harvest.merge_candidates(pd.DataFrame([original]), pd.DataFrame([refreshed]))
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue.iloc[0]["table_candidates"], refreshed["table_candidates"])
        self.assertEqual(queue.iloc[0]["fulltext_url"], refreshed["fulltext_url"])
        self.assertEqual(queue.iloc[0]["curator_note"], original["curator_note"])


if __name__ == "__main__":
    unittest.main()
