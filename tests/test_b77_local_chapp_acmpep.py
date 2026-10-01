"""Source-boundary regression checks prepared outside the publication checkout."""
import copy,csv,sys,unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import pairing
import validate_tg_loi as validator
FILE=ROOT/'data/incoming/verified_source_batch_20261001_b77_local_chapp_acmpep.csv'
def rows(suffix=None):
 with FILE.open(newline='') as f:a=list(csv.DictReader(f))
 return [r for r in a if suffix is None or r['DOI'].endswith(suffix)]
class OriginalSourceBoundaries(unittest.TestCase):
 def test_chapp_uncoated_and_condition_boundaries(self):
  a=rows('2019.108998');controls=[r for r in a if r['sample_state']=='Uncoated Polyester'];self.assertEqual(len(controls),2)
  for r in controls:self.assertFalse(r['LOI_pct']);self.assertFalse(r['Tmax1_C']);self.assertFalse(r['Tmax2_C'])
  g=next(r for r in a if r['sample_state']=='CH:GSM/APP-10BL' and r['atmosphere']=='nitrogen');self.assertFalse(g['Tmax2_C']);self.assertEqual(float(g['source_Tmax2_table_C']),390);self.assertEqual(float(g['source_Tmax2_prose_C']),385)
  air=next(r for r in a if r['sample_state']==g['sample_state'] and r['atmosphere']=='air');self.assertEqual(float(air['Tmax2_C']),385)
  for r in a:
   self.assertEqual(float(r['TG_prehold_temperature_C']),100);self.assertEqual(float(r['TG_prehold_duration_min']),30);self.assertEqual(float(r['residue_temp_C']),600);self.assertFalse(r.get('R850_pct'));self.assertIn('mL/s',r['TG_sample_purge_reported']);self.assertFalse(r.get('TG_gas_flow_mL_min'));self.assertFalse(r.get('Tonset_C'))
  self.assertFalse(any(r['atmosphere']=='nitrogen' and r['sample_state'] in ['CH/APP-25BL','CH:U/APP-10BL','CH:THU/APP-10BL'] for r in a))
 def test_acmpep_exact_initial30percent_and760c_residue(self):
  a=rows('2019.04.009');paired=[r for r in a if r['LOI_pct']];self.assertEqual(len(paired),4)
  for r in paired:
   self.assertEqual(float(r['residue_temp_C']),760);self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('Tonset_C'));self.assertEqual(float(r['heating_rate_C_min']),20);self.assertEqual(float(r['TG_start_C']),25)
   self.assertEqual(float(r['LOI_pct']),42 if r['sample_state'].startswith('30%') else 17.8)
   self.assertTrue(r['supplement_source_url'].endswith('S0141391019301272-mmc1.docx'))
  t=next(r for r in paired if r['sample_state'].startswith('30%') and r['atmosphere']=='nitrogen');self.assertEqual(float(t['ACMPEP_bath_wt_pct']),30);self.assertEqual(float(t['weight_gain_pct']),33.4);self.assertEqual(float(t['T50_C']),434);self.assertEqual(float(t['Tmax1_C']),296)
  for r in a:
   if r['sample_state']=='ACMPEP compound':self.assertFalse(r['LOI_pct']);self.assertFalse(r['residue_temp_C']);self.assertNotEqual(r['material_form'],t['material_form'])
  self.assertFalse(any('wash' in r['sample_state'] or r['sample_state'].startswith(('20%','25%')) for r in a))
 def test_viscose_bath_loading_and_printed_table(self):
  a=rows('2021.109620');self.assertEqual(len(a),8)
  t=next(r for r in a if r['sample_state']=='Viscose-TSPDP-20' and r['atmosphere']=='air');self.assertEqual(float(t['LOI_pct']),25.1);self.assertEqual(float(t['TSPDP_bath_wt_pct']),20);self.assertEqual(float(t['weight_gain_pct']),13);self.assertEqual(float(t['R700_pct']),13);self.assertEqual(float(t['residue_at_Tmax_pct']),82);self.assertEqual(float(t['Tmax1_C']),260)
  for r in a:
   self.assertEqual(float(r['residue_temp_C']),700);self.assertFalse(r.get('R800_pct'));self.assertFalse(r.get('LOI_repeats'));self.assertIn('allfive',r['supplement_review_status']);self.assertIn('1.36ppm',r['limitations']);self.assertIn('Figure4',r['LOI_locator'])
 def test_counts_and_publication_type(self):
  a=rows();_,_,_,p=validator.build_tables(pd.DataFrame(a),validator.issue_list());self.assertFalse(p['errors']);self.assertEqual(p['verified_exact_sample_states'],12);self.assertEqual(p['verified_exact_condition_records'],21);self.assertEqual(sum(not r['LOI_pct'] for r in a),4);self.assertEqual(p['verified_publication_type_counts']['journal_article'],dict(sources=3,sample_states=12,condition_records=21))
  for r in a:
   if r['LOI_pct']:self.assertFalse(pairing.evidence_issues(r))
 def test_changed_values_and_washes_invalidate_review(self):
  r=next(r for r in rows() if r['LOI_pct'])
  for field,value in [('LOI_pct','80'),('T10_C','600'),('washing_state','after50launderingcycles'),('atmosphere','nitrogen'),('heating_rate_C_min','20')]:
   x=copy.deepcopy(r);x[field]=value;self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(x))
if __name__=='__main__':unittest.main()
