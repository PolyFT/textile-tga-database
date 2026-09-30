"""Protect source semantics, exclusions and observation-scoped review in batch48."""
import csv,hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.pairing import evidence_issues,measurement_fingerprint
from scripts.validate_tg_loi import build_tables,numeric_errors
R=Path(__file__).resolve().parents[1]
M=R/'data/curation/source_review_manifest_20260930_b48.json'
def rows():
    result=[]
    for f in json.loads(M.read_text())['files']:
        with (R/f['file']).open(newline='') as h:result.extend(csv.DictReader(h))
    return result
def paper(doi):return [x for x in rows() if x['DOI'].lower()==doi.lower()]
class Batch48(unittest.TestCase):
    def test_counts_and_observation_binding(self):
        data=rows();self.assertEqual(len(data),23)
        self.assertEqual(len({(x['DOI'],x['sample_state'],x['washing_state']) for x in data}),22)
        for x in data:
            self.assertFalse(evidence_issues(x));self.assertEqual(measurement_fingerprint(x),x['reviewed_measurement_fingerprint'])
        self.assertIn('measurement_review_pending_or_stale',evidence_issues(dict(data[0],LOI_pct='99')))
        master,_,_,report=build_tables(pd.DataFrame(data));self.assertEqual(len(master),23);self.assertEqual(report['verified_exact_sample_states'],22)
        self.assertFalse(numeric_errors(pd.DataFrame(data)))
    def test_input_hashes(self):
        for f in json.loads(M.read_text())['files']:
            self.assertEqual(hashlib.sha256((R/f['file']).read_bytes()).hexdigest(),f['published_input_sha256'])
    def test_silk_control_not_treated_or_DTA(self):
        d=paper('10.1016/j.arabjc.2023.105497');self.assertEqual(len(d),2)
        self.assertEqual({x['sample_state'] for x in d},{'Untreated silk'})
        self.assertEqual({(x['atmosphere'],x['LOI_pct'],x['Tmax1_C'],x['R600_pct']) for x in d},{('N2','24.4','324.6','30.8'),('air','24.4','325.2','5.7')})
    def test_carrageenan_fiber_residues_not_cone_or_gas_peaks(self):
        d=paper('10.1039/c7ra01076a');self.assertEqual(len(d),3)
        self.assertEqual({(x['sample_state'],x['LOI_pct'],x['R700_pct']) for x in d},{('AGF','18.5','25'),('ALF','46','35'),('CAF','52','45')})
        self.assertTrue(all(x['material_form_TGA']=='fiber' and x['material_form_LOI']=='fiber' and x['heating_rate_C_min']=='20' for x in d))
        self.assertFalse(any(x.get('Tmax1_C') for x in d))
    def test_lttfd_onset_is_T10_and_endset_held(self):
        d=paper('10.32474/LTTFD.2023.05.000213');self.assertEqual(len(d),2)
        self.assertEqual({x['T10_C'] for x in d},{'336.97','306.17'})
        self.assertFalse(any(x.get('Tonset_C') or x.get('T95_C') or x.get('TG_endset_C') for x in d))
        self.assertTrue(all(x['atmosphere']=='N2' and x['heating_rate_C_min']=='10' for x in d))
    def test_phosphazene_generic_residue_and_zero_method_start(self):
        d=paper('10.14504/ajr.1.6.3');self.assertEqual(len(d),7)
        self.assertTrue(all(x['tga_start_temperature_C']=='0' and not x.get('TG_start_C') and not x.get('residue_temp_C') and not x.get('R600_pct') for x in d))
        self.assertEqual({x['sample_state'] for x in d},{'Control','non-scCO2 6 wt%','non-scCO2 9 wt%','non-scCO2 22 wt%','scCO2 9 wt%','scCO2 12 wt%','scCO2 22 wt%'})
        self.assertFalse(next(x for x in d if x['sample_state']=='Control')['Tonset_C'])
    def test_coconut_correction_and_conflict_holds(self):
        d=paper('10.1021/acs.chas.4c00050');self.assertEqual({x['sample_state'] for x in d},{'S2','S3','S4'})
        self.assertTrue(all(x['TG_end_C']=='600' and x['heating_rate_C_min']=='10' and 'PMC11938338' in x['correction_url'] for x in d))
        s2=next(x for x in d if x['sample_state']=='S2');self.assertEqual(s2['R400_pct'],'15');self.assertFalse(s2['residue_pct']);self.assertFalse(s2['residue_temp_C'])
        self.assertEqual({(x['sample_state'],x['residue_temp_C'],x['residue_pct']) for x in d if x['sample_state']!='S2'},{('S3','450','12'),('S4','450','29')})
    def test_casein_source_labels_and_dual_onsets(self):
        d={x['sample_state']:x for x in paper('10.11648/j.ijmsa.20200904.11')};self.assertEqual(len(d),6)
        self.assertEqual({(k,x['LOI_pct'],x['R600_pct']) for k,x in d.items()},{('Control','18','13.9'),('PDC-1','22','26.9'),('PDC-2','23','29.5'),('PDC-3','29','33.1'),('SC-1','35','33.8'),('SC-2','40','36.1')})
        self.assertFalse(d['PDC-2']['add_on_pct']);self.assertFalse(d['SC-2']['add_on_pct']);self.assertFalse(d['PDC-1']['Tonset_C'])
        self.assertEqual((d['SC-1']['source_onset1_C'],d['SC-1']['source_onset2_C']),('143.8','268.8'))
        self.assertTrue(all(x['atmosphere']=='N2' and not x.get('Tmax1_C') for x in d.values()))
    def test_held_sources_not_admitted(self):
        dois={x['DOI'].lower() for x in rows()}
        self.assertTrue(dois.isdisjoint({'10.1177/1528083718813527','10.1039/c7ra13228j','10.3390/ma15144791','10.1016/j.polymdegradstab.2009.03.017'}))
        holds=json.loads((R/'data/curation/source_review_holds_20260930_b48.json').read_text())
        self.assertTrue(any(h.get('DOI')=='10.1021/acs.chas.4c00050' and h.get('hold_scope')=='S5 entire TG-LOI pair' for h in holds))
