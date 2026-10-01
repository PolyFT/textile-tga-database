import csv
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pairing import sample_state_id,evidence_issues,measurement_fingerprint

class B100TextileEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={p.stem.split('_b100_',1)[1]:list(csv.DictReader(p.open())) for p in ROOT.glob('data/incoming/verified_source_batch_20261001_b100_*.csv')}
    def test_state_count_and_independent_review_binding(self):
        rows=[r for rs in self.rows.values() for r in rs]
        self.assertEqual((len(rows),len({sample_state_id(r) for r in rows})),(19,19))
        self.assertEqual(len({r['DOI'] for r in rows}),5)
        for r in rows:
            self.assertFalse(evidence_issues(r))
            self.assertEqual(r['reviewed_measurement_fingerprint'],measurement_fingerprint(r))
            self.assertEqual(r['publication_type'],'journal_article')
    def test_ramie_conflicting_residues_stay_raw(self):
        rows={r['source_sample_label']:r for r in self.rows['ramie_multilayer2016']}
        self.assertEqual(set(rows),{'Ramie/BZ','MARamie/BZ','PARamie/BZ'})
        for label,value in [('Ramie/BZ','4'),('MARamie/BZ','7')]:
            self.assertFalse(rows[label]['R600_pct'])
            self.assertFalse(rows[label].get('residue_pct'))
            self.assertEqual(rows[label]['source_conflicting_R600_pct'],value)
        self.assertEqual(rows['PARamie/BZ']['R600_pct'],'24')
    def test_siloxane_air_and_cone_residue_conflict(self):
        rows={r['source_sample_label']:r for r in self.rows['aramid_siloxane2026']}
        self.assertEqual(set(rows),{'0%','20%','40%','60%','80%'})
        self.assertEqual(rows['40%']['source_conflicting_abstract_R1000_pct'],'56.8')
        for key in ['R1000_pct','residue_pct','residue_temp_C']:
            self.assertFalse(rows['40%'][key])
        for r in rows.values():
            self.assertEqual(r['atmosphere'],'air')
            self.assertEqual(r['heating_rate_C_min'],'10')
            self.assertIn('rinsing',r['washing_state'])
        self.assertEqual(rows['0%']['R1000_pct'],'2.50')
    def test_uv_aramid_unknown_recipe_and_char_temperature(self):
        rows={r['source_sample_label']:r for r in self.rows['aramid_uv2011']}
        self.assertEqual(set(rows),{'Untreated','UV-irradiated','Grafted','Dyed'})
        self.assertEqual([rows[k]['Tmax1_C'] for k in ['Untreated','UV-irradiated','Grafted','Dyed']],['607.7','608.7','609.0','607.8'])
        for r in rows.values():
            self.assertEqual(r['LOI_pct'],'28.9')
            self.assertEqual(r['TG_end_C'],'800')
            self.assertFalse(r['residue_temp_C'])
            self.assertFalse(r.get('R800_pct'))
            self.assertFalse(r.get('T5_C'))
            self.assertTrue(r['source_T98_C'])
            self.assertIn('remain unknown',r['limitations'])
        self.assertIn('no separate colorfastness wash',rows['Dyed']['washing_state'])
    def test_jute_soy_only_measured_loi_and_residues(self):
        rows={r['source_sample_label']:r for r in self.rows['jute_soy2013']}
        self.assertEqual(set(rows),{'S/J','S/J/G30','S/J/G50','S/J/G70','S/J/G50/M1','S/J/G50/M5'})
        self.assertEqual((rows['S/J/G50/M5']['LOI_pct'],rows['S/J/G50/M5']['R600_pct']),('56','31'))
        for r in rows.values():
            self.assertEqual(r['residue_temp_C'],'600')
            self.assertEqual(r['residue_pct'],r['R600_pct'])
            self.assertFalse(r.get('Tmax1_C'))
            self.assertFalse(r.get('Tmax2_C'))
            self.assertFalse(r.get('LOI_sd'))
    def test_recycled_aramid_retains_mixed_gas_program(self):
        r,=self.rows['recycled_aramid2013']
        self.assertEqual((r['LOI_pct'],r['residue_pct'],r['residue_temp_C']),('19.9','12.77','539'))
        self.assertEqual(r['atmosphere'],'N2')
        self.assertEqual(r['heating_rate_C_min'],'30')
        self.assertEqual(r['TG_end_C'],'800')
        self.assertIn('O2 from600 to800',r['source_TG_atmosphere_program'])
        self.assertIn('precedes the gas switch',r['TGA_specimen_preparation'])
        self.assertFalse(r.get('Tmax1_C'))
        self.assertFalse(r.get('R800_pct'))
    def test_public_holds_exclude_private_paths(self):
        t=(ROOT/'data/curation/source_review_holds_20261001_b100.json').read_text()
        for marker in ['/workspace/','/tmp/','new-textile-cache/','new-textile-prep/']:
            self.assertNotIn(marker,t)

if __name__=='__main__':unittest.main()
