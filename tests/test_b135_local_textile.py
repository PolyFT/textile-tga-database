"""Protect native gas/order/temperature semantics and unresolved source groups."""
import csv,sys,unittest
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;private=P.name=='work';R=P.parent/'repo'if private else P.parent
F=P/'staged-local-textile-b135/publication_proposed.csv'if private else R/'data/incoming/verified_source_batch_20261002_b135_local_textile.csv'
sys.path.insert(0,str(R/'scripts'));import pairing,validate_tg_loi as v
A='10.1016/j.porgcoat.2021.106271';B='10.1021/acssuschemeng.9b05523'
class TextileB135Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with F.open(newline='')as f:cls.rows=list(csv.DictReader(f))
 def source(self,d):return[r for r in self.rows if r['DOI']==d]
 def exact(self,d,s,g):return next(r for r in self.source(d)if r['sample_state']==s and r['atmosphere']==g and r['pairing_status']=='verified_exact')
 def reject(self,r,**kw):self.assertIn('measurement_review_pending_or_stale',pairing.evidence_issues(dict(r,**kw)))
 def test_sixstates_eightconditions_not18facts(self):
  z=v.build_tables(pd.DataFrame(self.rows).fillna(''),v.issue_list())[3];self.assertFalse(z['errors']);self.assertEqual((z['verified_exact_sample_states'],z['verified_exact_condition_records']),(6,8));self.assertEqual(len(self.rows),18)
 def test_tenholds_no_chosen_tg(self):
  rr=[r for r in self.rows if r['pairing_status']!='verified_exact'];self.assertEqual(len(rr),10);self.assertTrue(all(all(not r[k]for k in pairing.TG_FIELDS)for r in rr))
 def test_porg_only15_25_initialpaired(self):
  rr=[r for r in self.source(A)if r['pairing_status']=='verified_exact'];self.assertEqual(len(rr),4);self.assertEqual({r['sample_state']for r in rr},{'IP6_15PA66','IP6_25PA66'})
 def test_35_loiconflict_notresolved_by_tablepreference(self):
  rr=[r for r in self.source(A)if r['sample_state']=='IP6_35PA66'and r['treatment_state']=='Initial own native group'];self.assertEqual(len(rr),2);self.assertTrue(all(not r['LOI_pct']and r['source_raw_LOI_Table1_pct']=='32.3'and r['source_raw_LOI_prose_pct']=='32.2'and'conflict'in r['pairing_status']for r in rr))
 def test_possible_controlreuse_held_notcounted(self):
  rr=[r for r in self.source(A)if r['sample_state']=='UntreatedPA66'];self.assertEqual(len(rr),2);self.assertTrue(all('reuse_unresolved'in r['pairing_status']and'Possible'in r['source_control_reuse_adjudication']for r in rr))
 def test_reverse_table3_columnorder(self):
  x=self.exact(A,'IP6_15PA66','N2');y=self.exact(A,'IP6_25PA66','N2');self.assertEqual((x['T10_C'],y['T10_C']),('323.39','305.49'));self.reject(x,T10_C='291.01')
 def test_t10_not_t5_or_generic_onset(self):
  r=self.exact(A,'IP6_25PA66','air');self.assertEqual(r['T10_C'],'303.48');self.assertFalse(r['T5_C']);self.assertFalse(r['Tonset_C']);self.reject(r,T10_C='',T5_C='303.48')
 def test_gases_notmerged(self):
  n=self.exact(A,'IP6_15PA66','N2');a=self.exact(A,'IP6_15PA66','air');self.assertEqual((n['T10_C'],a['T10_C']),('323.39','329.51'));self.reject(n,atmosphere='air')
 def test_porg_char800_notcone(self):
  r=self.exact(A,'IP6_25PA66','N2');self.assertEqual((r['R800_pct'],r['residue_temp_C']),('24.8','800'));self.reject(r,R800_pct='37.9',residue_pct='37.9')
 def test_porg_method_notborrowing_ftirmarker(self):
  r=self.exact(A,'IP6_25PA66','air');self.assertEqual((r['heating_rate_C_min'],r['TG_start_C'],r['TG_end_C']),('10','100','800'));self.assertFalse(r['Tmax1_C']);self.reject(r,Tmax1_C='335')
 def test_sixwashed_states_no_tg(self):
  rr=[r for r in self.source(A)if r['source_native_wash_count']];self.assertEqual(len(rr),6);self.assertEqual({r['LOI_pct']for r in rr},{'20.4','31.8','20.8','26.6','19','24.3'});self.assertTrue(all(not r['material_form_TGA']for r in rr));self.reject(self.exact(A,'IP6_25PA66','N2'),LOI_pct='26.6',washing_state='20nativecycles;wateronly')
 def test_gpa_fourinitialgroups(self):
  rr=self.source(B);self.assertEqual(len(rr),4);self.assertTrue(all(r['pairing_status']=='verified_exact'and r['atmosphere']=='N2'for r in rr));self.assertEqual({r['LOI_pct']for r in rr},{'18','22.5','26','29'})
 def test_gpa_control_t5_waternot_dtgpeak(self):
  r=self.exact(B,'ControlCotton','N2');self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C']),('298','315','361'));self.assertIn('waterattribution',r['source_T5_T10_definition']);self.reject(r,Tmax1_C='298')
 def test_gpa_threeformulas_not_swapped(self):
  r=self.exact(B,'GPA3Cotton','N2');self.assertEqual((r['T5_C'],r['T10_C'],r['Tmax1_C']),('252','264','293'));self.reject(r,Tmax1_C='283')
 def test_gpa_r700_not_coneor800(self):
  r=self.exact(B,'GPA5Cotton','N2');self.assertEqual((r['R700_pct'],r['residue_temp_C']),('40','700'));self.assertFalse(r['R800_pct']);self.reject(r,R700_pct='35.82',residue_pct='35.82');self.reject(r,residue_temp_C='800')
 def test_gpa_missing_loimethod_notvertical(self):
  r=self.exact(B,'GPA4Cotton','N2');self.assertFalse(r['LOI_standard']);self.assertIn('unreported',r['source_LOI_method_limit']);self.assertIn('notborrowedLOI',r['source_LOI_method_limit'])
 def test_gpa_rate_notrmax_or_pipe(self):
  r=self.exact(B,'GPA4Cotton','N2');self.assertEqual((r['heating_rate_C_min'],r['source_TG_N2_flow_mL_min'],r['TG_end_C']),('10','50','700'));self.assertEqual(r['source_raw_Rmax_per_C'],'17.4');self.assertEqual(r['source_pipe_gas_cell_C'],'280');self.reject(r,heating_rate_C_min='17.4');self.reject(r,residue_temp_C='280')
 def test_invalid_specimen_rate_rejected(self):
  r=self.exact(B,'GPA5Cotton','N2');self.assertIn('specimen_form_mismatch',pairing.evidence_issues(dict(r,material_form_TGA='Neat GPA powder')));self.assertTrue(pairing.evidence_issues(dict(r,heating_rate_C_min='0')))
if __name__=='__main__':unittest.main()
