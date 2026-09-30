"""Offline regressions for conservative Grade-B method recovery and retries."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pairing
import review_b_tg_loi as review

NOW=datetime(2026,9,30,12,tzinfo=timezone.utc)
METHOD=('Thermogravimetric analysis (TGA) was performed using a NETZSCH analyzer '
        'under nitrogen (flow rate 60 mL/min), from 30 to 800 °C at a heating rate '
        'of 10 °C/min. Differential scanning calorimetry (DSC) used 20 °C/min.')


def candidate(**overrides):
    row={'DOI':'10.1000/cotton','title':'Flame retardant cotton fabric',
         'sample_state':'Cotton-A','sample_norm':'cotton-a','washing_state':'',
         'LOI_pct':'28.0','Tmax1_C':'355','atmosphere':'','heating_rate_C_min':'',
         'grade':'B','extractor_version':'6','extracted_at_utc':NOW.isoformat(),
         'source_url':'https://europepmc.org/articles/PMC123',
         'source_location':'LOI table: Table 2; TG table: Table 3',
         'evidence':'Label matching only; independent specimen review pending.'}
    row.update(overrides)
    return row


class MethodExtractionTests(unittest.TestCase):
    def test_realistic_method_is_detected_not_literal_backslashes(self):
        windows=review.tg_windows(METHOD)
        self.assertTrue(windows)
        value,context=review.infer_rate(METHOD)
        self.assertEqual(value,10)
        self.assertIn('NETZSCH',context)
        self.assertNotIn('DSC',context)
        self.assertEqual(review.RATE_BARE.findall('heating rate of 10.5 °C/min'),['10.5'])

    def test_method_boundary_is_honored_even_near_start(self):
        value,_=review.infer_rate('TGA tests. DSC used 20 °C/min in nitrogen.')
        self.assertIsNone(value)

    def test_inverse_and_slash_units(self):
        for unit in ['°C/min','℃ per minute','K min−1','°C·min⁻¹','K min^-1']:
            with self.subTest(unit=unit):
                value,_=review.infer_rate(f'TGA used a heating rate of 10 {unit} under nitrogen.')
                self.assertEqual(value,10)

    def test_rate_lists_ranges_and_multiple_methods_stay_ambiguous(self):
        for text in [
            'TGA used heating rates of 5, 10 and 20 °C/min under nitrogen.',
            'TGA used heating rates of 5–20 °C/min under nitrogen.',
            'TGA used 5 °C/min and 20 °C/min under nitrogen.',
            'TGA used 10 °C/min under nitrogen. DSC results. '
            'Thermogravimetry used 20 °C/min under air.',
        ]:
            with self.subTest(text=text):
                self.assertIsNone(review.infer_rate(text)[0])

    def test_unitless_and_non_tga_rates_do_not_become_conditions(self):
        for text in ['TGA used heating rate 10 under nitrogen.',
                     'DSC used 20 °C/min under nitrogen.',
                     'TGA used a heating rate of 0 °C/min under nitrogen.']:
            self.assertIsNone(review.infer_rate(text)[0])

    def test_fixed_textile_word_boundaries(self):
        self.assertFalse(review.valid_textile(candidate(source_location='TG of cotton paper')))
        self.assertFalse(review.valid_textile(candidate(title='PET blends',source_location='Table 3')))
        self.assertTrue(review.valid_textile(candidate(title='PET woven fabric')))

    def test_conflicting_existing_atmospheres_are_unresolved(self):
        self.assertEqual(review.infer_atm({'atmosphere':'air and N2'},METHOD,METHOD),('',''))

    def test_loi_atmosphere_does_not_contaminate_tga_context(self):
        row=candidate(source_location='LOI table: oxygen index in air; TG table: Table 3')
        self.assertEqual(review.infer_atm(row,METHOD,review.infer_rate(METHOD)[1])[0],'N2')

    def test_exact_loi_and_finite_tg_are_required(self):
        for loi in ['20–30','>28','28 +/- 1','nan','101']:
            self.assertEqual(review.preliminary_reason(candidate(LOI_pct=loi)),'invalid_loi')
        self.assertEqual(review.preliminary_reason(candidate(Tmax1_C='nan')),'no_valid_tg')
        self.assertEqual(review.preliminary_reason(candidate(LOI_pct='')),'missing_loi')


class FingerprintTests(unittest.TestCase):
    def test_helpers_use_conservative_shared_identity(self):
        self.assertNotEqual(review.ns('A+B'),review.ns('AB'))
        self.assertEqual(review.norm_key('https://doi.org/10.1000/TEST',' A+B ','','N₂','10.0'),
                         pairing.normalized_pair_key('10.1000/test','a+b','','nitrogen',10))

    def test_fingerprint_ignores_order_and_attempt_timestamps(self):
        first=candidate()
        second=candidate(sample_state='B',sample_norm='b')
        changed=dict(first,extracted_at_utc='2030-01-01T00:00:00Z',_ts='internal')
        self.assertEqual(review.input_fingerprint([first,second]),
                         review.input_fingerprint([second,changed]))
        self.assertNotEqual(review.input_fingerprint([first]),
                            review.input_fingerprint([dict(first,Tmax1_C='365')]))

    def test_parser_version_and_input_invalidate_cache(self):
        previous=review.review_state({},'fingerprint',['non_textile'],NOW)
        self.assertFalse(review.should_review(previous,'fingerprint',NOW+timedelta(days=100)))
        self.assertTrue(review.should_review(previous,'new fingerprint',NOW))
        with patch.object(review,'PARSER_VERSION','next'):
            self.assertTrue(review.should_review(previous,'fingerprint',NOW))

    def test_cooldown_and_attempt_counter(self):
        previous=review.review_state({},'fingerprint',['fetch_failed'],NOW)
        self.assertEqual(previous['attempts'],1)
        self.assertFalse(review.should_review(previous,'fingerprint',NOW+timedelta(hours=1)))
        self.assertTrue(review.should_review(previous,'fingerprint',NOW+review.FETCH_RETRY))
        after=review.review_state(previous,'fingerprint',['rate_unresolved'],NOW+review.FETCH_RETRY)
        self.assertEqual(after['attempts'],2)
        self.assertEqual(after['next_retry_utc'],(NOW+review.FETCH_RETRY+review.REVIEW_RETRY).isoformat())

    def test_latest_version_selected_before_grade(self):
        rows=[candidate(extractor_version='5'),candidate(grade='C'),
              candidate(DOI='10.1000/legacy',extractor_version='')]
        self.assertTrue(review.latest_b_rows(pd.DataFrame(rows)).empty)

    def test_latest_rows_preserve_label_punctuation_and_different_atmospheres(self):
        rows=[candidate(sample_state='A+B',sample_norm='ab'),
              candidate(sample_state='AB',sample_norm='ab'),
              candidate(sample_state='AB',sample_norm='ab',atmosphere='air')]
        self.assertEqual(len(review.latest_b_rows(pd.DataFrame(rows))),3)


class ReviewIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        data=root/'data'; auto=data/'automation'; inc=data/'incoming'
        auto.mkdir(parents=True); inc.mkdir()
        self.paths={'ROOT':root,'DATA':data,'AUTO':auto,'INC':inc,
                    'REVIEW':auto/'review_queue.csv','MASTER':data/'tg_loi_master.csv',
                    'STATE':auto/'b_review_state.json','REVIEWS':data/'curation'/'pair_reviews.csv'}
        self.patch=patch.multiple(review,**self.paths)
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.registry=patch.object(pairing,'REVIEWS',self.paths['REVIEWS'])
        self.registry.start(); self.addCleanup(self.registry.stop)
        self.no_network=patch.object(review.requests,'get',side_effect=AssertionError('Network is forbidden in tests'))
        self.no_network.start(); self.addCleanup(self.no_network.stop)

    def queue(self,rows=None):
        pd.DataFrame(rows or [candidate()]).to_csv(review.REVIEW,index=False)

    def run_review(self,text=METHOD,now=NOW):
        with patch.object(review,'utc_now',return_value=now), \
             patch.object(review,'get_text',return_value=(text,'https://europepmc.org/articles/PMC123' if text else '')) as fetch, \
             patch.dict('os.environ',{'B_REVIEW_MAX_DOIS':'30'}),contextlib.redirect_stdout(io.StringIO()):
            review.main()
        return fetch

    def state(self):
        return json.loads(review.STATE.read_text())['processed']

    def audit(self):
        return pd.read_csv(review.AUTO/'b_review_audit.csv',dtype=str).fillna('')

    def test_label_only_pair_is_pending_and_original_input_untouched(self):
        self.queue()
        original=review.REVIEW.read_bytes()
        self.run_review()
        self.assertEqual(review.REVIEW.read_bytes(),original)
        self.assertEqual(list(review.INC.iterdir()),[])
        self.assertEqual(self.audit().iloc[-1].reason_code,'evidence_review_required')
        resolved=pd.read_csv(review.AUTO/'b_review_resolved.csv',dtype=str).fillna('')
        self.assertEqual(resolved.iloc[0]['source_location'],candidate()['source_location'])
        self.assertEqual(resolved.iloc[0]['extraction_source_url'],candidate()['source_url'])
        self.assertEqual(float(resolved.iloc[0]['heating_rate_C_min']),10)
        self.assertEqual(resolved.iloc[0]['grade'],'B')
        self.assertNotIn('pairing_status',resolved.columns)

    def test_human_evidence_review_wait_does_not_redownload_on_a_timer(self):
        self.queue()
        self.run_review()
        before=review.STATE.read_bytes()
        self.assertEqual(self.run_review(now=NOW+timedelta(days=100)).call_count,0)
        self.assertEqual(review.STATE.read_bytes(),before)
        self.assertEqual(self.state()['10.1000/cotton']['status'],'awaiting_evidence_review')

    def test_permanent_rejection_skips_fetch_and_noop_preserves_all_bytes_and_mtimes(self):
        self.queue([candidate(title='Polymer resin',source_location='Molded resin plaque')])
        self.assertEqual(self.run_review().call_count,0)
        before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in review.AUTO.iterdir()}
        self.assertEqual(self.run_review(now=NOW+timedelta(days=30)).call_count,0)
        after={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in review.AUTO.iterdir()}
        self.assertEqual(before,after)
        self.assertEqual(self.state()['10.1000/cotton']['attempts'],1)

    def test_fetch_failure_cools_down_then_retries_and_preserves_history(self):
        self.queue()
        self.assertEqual(self.run_review(text='').call_count,1)
        self.assertEqual(self.audit().iloc[-1].reason_code,'fetch_failed')
        self.assertEqual(self.run_review(text='',now=NOW+timedelta(hours=1)).call_count,0)
        self.assertEqual(self.run_review(now=NOW+review.FETCH_RETRY).call_count,1)
        self.assertEqual(self.state()['10.1000/cotton']['attempts'],2)
        self.assertEqual(self.audit().reason_code.tolist(),['fetch_failed','evidence_review_required'])

    def test_ambiguous_method_cooldown(self):
        self.queue()
        text='TGA used heating rates of 5 and 20 °C/min under nitrogen.'
        self.run_review(text=text)
        self.assertEqual(self.audit().iloc[-1].reason_code,'rate_unresolved')
        self.assertEqual(self.run_review(now=NOW+timedelta(hours=12)).call_count,0)
        self.assertEqual(self.run_review(now=NOW+review.REVIEW_RETRY).call_count,1)

    def test_changed_input_and_parser_version_are_reprocessed_immediately(self):
        self.queue()
        self.run_review(text='')
        self.queue([candidate(source_url='https://europepmc.org/articles/PMC456')])
        self.assertEqual(self.run_review().call_count,1)
        with patch.object(review,'PARSER_VERSION','new'):
            self.assertEqual(self.run_review().call_count,1)
        self.assertEqual(self.state()['10.1000/cotton']['attempts'],3)

    def test_timestamp_only_change_does_not_invalidate_state(self):
        self.queue()
        self.run_review(text='')
        self.queue([candidate(extracted_at_utc=(NOW+timedelta(minutes=10)).isoformat())])
        self.assertEqual(self.run_review().call_count,0)

    def test_permanent_rows_in_mixed_doi_are_not_reaudited_on_cooldown(self):
        self.queue([candidate(sample_state='Resin',sample_norm='resin',source_location='resin plaque'),
                    candidate()])
        self.run_review(text='')
        self.run_review(now=NOW+review.FETCH_RETRY)
        self.assertEqual(self.audit().reason_code.tolist().count('non_textile'),1)
        self.assertEqual(len(self.audit()),3)

    def test_missing_loi_receives_cooldown_without_network(self):
        self.queue([candidate(LOI_pct='')])
        self.assertEqual(self.run_review().call_count,0)
        entry=self.state()['10.1000/cotton']
        self.assertEqual(entry['reason_codes'],['missing_loi'])
        self.assertIsNotNone(entry['next_retry_utc'])

    def test_registry_change_invalidates_pending_cache_and_only_exact_review_promotes(self):
        self.queue()
        self.run_review()
        resolved=pd.read_csv(review.AUTO/'b_review_resolved.csv',dtype=str).fillna('').iloc[0].to_dict()
        approval={**resolved,'pairing_status':'verified_exact',
                  'pairing_evidence':'Tables 2 and 3 specify the same Cotton-A fabric and unchanged washing state.',
                  'material_form_TGA':'fabric','material_form_LOI':'fabric',
                  'numeric_evidence_type':'tabulated','evidence_reviewed_by':'test reviewer'}
        approval['measurement_fingerprint']=pairing.measurement_fingerprint(resolved)
        review.REVIEWS.parent.mkdir()
        pd.DataFrame([approval]).to_csv(review.REVIEWS,index=False)
        self.assertEqual(self.run_review(now=NOW+timedelta(minutes=1)).call_count,1)
        promoted=list(review.INC.glob('verified_breview_*.csv'))
        self.assertEqual(len(promoted),1)
        out=pd.read_csv(promoted[0],dtype=str).fillna('')
        self.assertEqual(out.iloc[0]['pairing_status'],'verified_exact')
        self.assertEqual(self.audit().iloc[-1].reason_code,'promoted')
        # A parser change must not append the same observation a second time.
        with patch.object(review,'PARSER_VERSION','next'):
            self.run_review(now=NOW+timedelta(minutes=2))
        self.assertEqual(len(pd.read_csv(promoted[0])),1)

    def test_empty_queue_is_a_noop(self):
        review.REVIEW.write_text('\n')
        self.assertEqual(self.run_review().call_count,0)
        self.assertFalse(review.STATE.exists())

    def test_corrupt_state_is_not_overwritten(self):
        self.queue()
        review.STATE.write_text('{not valid JSON')
        with self.assertRaises(json.JSONDecodeError):
            self.run_review()
        self.assertEqual(review.STATE.read_text(),'{not valid JSON')


if __name__=='__main__':
    unittest.main()
