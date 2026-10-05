"""Expanded specimen eligibility requires an explicit documentary material binding."""
import unittest
from scripts import pairing as p
from scripts import validate_tg_loi as v
import pandas as pd

def reviewed_resin():
 row=dict(DOI='10.1234/pet-resin-scope',sample_state='PET0_resin',washing_state='initial',atmosphere='N2',heating_rate_C_min='10',LOI_pct='22',Tmax1_C='420',composition='PET resin; no additives',material_form='moulded PET resin slab',material_form_TGA='moulded PET resin slab',material_form_LOI='moulded PET resin slab',pairing_status='verified_exact',numeric_evidence_type='tabulated',direct_numeric_use='yes',pairing_evidence='OwnTable1TGandTable2LOIidentifysameinitialPET0mouldedresinformulation.',source_url='https://doi.org/10.1234/pet-resin-scope',source_location='Methods2.1;Tables1/2',source_title='PET resin assays',source_preparation='PET0 moulded stock used for both assays',evidence_reviewed_by='fixture source reviewer',evidence_reviewed_at='2026-10-05',material_scope_class='fiber_forming_polymer',source_material_scope_evidence='PET is a fibre-forming polymer; user scope accepts own resin tests without textile-use prose.',source_material_scope_locator='Methods2.1PETidentity;Tables1/2ownresinspecimens',material_scope_reviewed_by='fixture material reviewer',material_scope_reviewed_at='2026-10-05')
 row['reviewed_measurement_fingerprint']=p.measurement_fingerprint(row);row['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(row);return row
class ExpandedMaterialEvidence(unittest.TestCase):
 def test_resin_requires_explicit_material_review_not_PET_keyword(self):
  row=reviewed_resin();row.pop('reviewed_material_scope_fingerprint');master,_,_,_=v.build_tables(pd.DataFrame([row]));self.assertTrue(master.empty);self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(row))
 def test_explicit_review_admits_same_resin_without_textile_use_statement(self):
  row=reviewed_resin();self.assertFalse(p.evidence_issues(row));master,_,_,report=v.build_tables(pd.DataFrame([row]));self.assertEqual((len(master),report['verified_exact_sample_states']),(1,1))
 def test_different_resin_and_film_forms_are_still_rejected(self):
  row=reviewed_resin();row['material_form_LOI']='PET film';row['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(row);self.assertIn('specimen_form_mismatch',p.evidence_issues(row))
 def test_recipe_preparation_and_documentary_changes_require_rereview(self):
  for field,value in [('composition','crosslinked epoxy'),('source_preparation','different cured composition'),('source_material_scope_locator','different table'),('source_material_scope_evidence','unreviewed capability claim')]:
   row=dict(reviewed_resin(),**{field:value});self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(row))
 def test_changed_measurements_gas_or_wash_remain_stale(self):
  for field,value in [('LOI_pct','30'),('Tmax1_C','450'),('atmosphere','air'),('washing_state','washed20cycles')]:
   row=dict(reviewed_resin(),**{field:value});row['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(row);self.assertIn('measurement_review_pending_or_stale',p.evidence_issues(row))
 def test_missing_reviewer_or_capability_evidence_is_not_approved(self):
  for field in ['material_scope_reviewed_by','material_scope_reviewed_at','source_material_scope_evidence','source_material_scope_locator']:
   row=reviewed_resin();row[field]='';row['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(row);self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(row))
 def test_city_use_or_arbitrary_class_does_not_replace_material_review(self):
  row=reviewed_resin();row['material_scope_class']='generic_city_plastic';row['reviewed_material_scope_fingerprint']=p.material_scope_fingerprint(row);self.assertIn('material_scope_review_pending_or_stale',p.evidence_issues(row))
if __name__=='__main__':unittest.main()
