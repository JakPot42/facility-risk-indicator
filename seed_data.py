"""seed_data.py — fictional demo facility scenarios. None of these
facilities exist; no field below identifies any person -- see models.py.
"""
from __future__ import annotations

from models import FacilityInputs

DEMO_FACILITIES: dict[str, FacilityInputs] = {
    "well_run": FacilityInputs(
        facility_label="Fictional Demo Facility A -- \"Cedar Ridge Systems\" (well-run baseline)",
        months_since_last_self_inspection=4,
        self_inspection_certified_current_year=True,
        fso_tenure_months=36,
        open_violation_count=1,
        violation_categories={"data_spill": 1},
        open_vulnerability_count=1,
        months_since_last_dcsa_review=10,
        possesses_classified_it_systems_onsite=True,
        stores_classified_material_onsite=True,
    ),
    "moderate_risk": FacilityInputs(
        facility_label="Fictional Demo Facility B -- \"Ashford Precision Components\" (moderate risk)",
        months_since_last_self_inspection=15,
        self_inspection_certified_current_year=True,
        fso_tenure_months=3,
        open_violation_count=4,
        violation_categories={"data_spill": 2, "improper_storage": 2},
        open_vulnerability_count=2,
        months_since_last_dcsa_review=20,
        possesses_classified_it_systems_onsite=True,
        stores_classified_material_onsite=True,
    ),
    "high_risk": FacilityInputs(
        facility_label="Fictional Demo Facility C -- \"Harlow Defense Fabrication\" (high risk)",
        months_since_last_self_inspection=27,
        self_inspection_certified_current_year=False,
        fso_tenure_months=None,
        open_violation_count=8,
        violation_categories={"data_spill": 2, "physical_loss": 5, "improper_storage": 1},
        open_vulnerability_count=7,
        months_since_last_dcsa_review=None,
        possesses_classified_it_systems_onsite=True,
        stores_classified_material_onsite=True,
    ),
    "naesoc_tier": FacilityInputs(
        facility_label="Fictional Demo Facility D -- \"Bright Path Logistics\" (lower-complexity/NAESOC-eligible)",
        months_since_last_self_inspection=6,
        self_inspection_certified_current_year=True,
        fso_tenure_months=18,
        open_violation_count=0,
        violation_categories={},
        open_vulnerability_count=0,
        months_since_last_dcsa_review=14,
        possesses_classified_it_systems_onsite=False,
        stores_classified_material_onsite=False,
    ),
}
