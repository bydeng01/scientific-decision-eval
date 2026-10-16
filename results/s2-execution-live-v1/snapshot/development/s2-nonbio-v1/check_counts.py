"""Offline S2 counting checks on manually reviewed/oracle relations, not text extraction."""

import unittest


# Figure 2.6, rows 1-6 only: cutter 1, wear scars 1A and 1B.
# Manually transcribed (PART, PART ID, OPERATOR); not automatic PDF extraction.
C02_SCAN_ROWS = (
    (1, "1A", "O1"),
    (1, "1A", "O1"),
    (1, "1A", "O1"),
    (1, "1B", "O3"),
    (1, "1B", "O3"),
    (1, "1B", "O3"),
)


def check_count(unit_ids, declared_count):
    """Count a complete mapping for the declared scope; missing is not zero."""
    if not unit_ids or any(unit_id is None for unit_id in unit_ids):
        return "insufficient", None
    actual_count = len(set(unit_ids))
    label = "supported" if actual_count == declared_count else "inconsistent"
    return label, actual_count


def check_model_branch(unit_ids, declared_count, *, candidate_covered):
    """Candidate coverage gates only a branch that actually needs model output."""
    if not candidate_covered:
        return "complete_candidates", None
    return check_count(unit_ids, declared_count)


class CountingChecks(unittest.TestCase):
    # Relations are supplied manually; IDs are source transcriptions or local aliases.
    def test_d01_batch_prism_and_half_scopes(self):
        halves = ["P1a", "P1b", "P2a", "P2b", "P3a", "P3b"]
        parent_prisms = ["P1", "P1", "P2", "P2", "P3", "P3"]
        parent_batches = ["B1"] * len(halves)
        self.assertEqual(check_count(halves, 6), ("supported", 6))
        self.assertEqual(check_count(parent_prisms, 3), ("supported", 3))
        self.assertEqual(check_count(parent_batches, 6), ("inconsistent", 1))
        self.assertEqual(check_count(parent_batches, 1), ("supported", 1))

    def test_d01_missing_candidate_blocks_downstream_count(self):
        self.assertEqual(
            check_model_branch(["B1"] * 6, 6, candidate_covered=False),
            ("complete_candidates", None),
        )

    def test_code_path_does_not_depend_on_model_candidates(self):
        self.assertEqual(check_count(["B1"] * 6, 6), ("inconsistent", 1))
        self.assertEqual(
            check_model_branch(["B1"] * 6, 6, candidate_covered=True),
            ("inconsistent", 1),
        )

    def test_d02_specimens_share_one_build(self):
        specimen_to_build = {"7": "build_1", "8": "build_1", "9": "build_1"}
        self.assertEqual(check_count(list(specimen_to_build), 3), ("supported", 3))
        self.assertEqual(check_count(list(specimen_to_build.values()), 3), ("inconsistent", 1))
        self.assertEqual(check_count(list(specimen_to_build.values()), 1), ("supported", 1))

    def test_d03_unknown_curing_runs(self):
        self.assertEqual(check_count([None, None, None], 3), ("insufficient", None))

    def test_c01_factor_specific_units(self):
        # The first of four bath runs; low current is assigned to its first two strips.
        strips = ["S1", "S2", "S3", "S4"]
        bath_runs = ["bath_1"] * len(strips)
        self.assertEqual(check_count(bath_runs, 4), ("inconsistent", 1))
        self.assertEqual(check_count(strips[:2], 2), ("supported", 2))

    def test_duplicate_rows_do_not_add_units(self):
        self.assertEqual(check_count(["B1", "B2", "B1", "B2"], 2), ("supported", 2))

    def test_incomplete_mapping_does_not_produce_exact_count(self):
        self.assertEqual(check_count(["B1", None], 1), ("insufficient", None))
        self.assertEqual(check_count([], 0), ("insufficient", None))

    def test_h01_factor_specific_scope(self):
        # IDs from Table 2; shared parent sample is a manually supplied source relation.
        columns = ["1", "10", "16", "19", "24"]
        treated_samples = ["SR870_sample"] * len(columns)
        self.assertEqual(check_count(columns, 5), ("supported", 5))
        self.assertEqual(check_count(treated_samples, 5), ("inconsistent", 1))

    def test_c02_wear_events_are_not_scans_or_cutter_count(self):
        # Pool O1 and O3 for the selected scars, not all records for cutter 1.
        wear_ids = [wear_id for _, wear_id, _ in C02_SCAN_ROWS]
        cutter_ids = [part for part, _, _ in C02_SCAN_ROWS]
        self.assertEqual(len(C02_SCAN_ROWS), 6)
        self.assertEqual(check_count(wear_ids, 6), ("inconsistent", 2))
        self.assertEqual(check_count(wear_ids, 2), ("supported", 2))
        self.assertEqual(check_count(cutter_ids, 1), ("supported", 1))

    def test_c02_operator_scope_is_applied_before_counting(self):
        for operator, expected_wear_id in (("O1", "1A"), ("O3", "1B")):
            with self.subTest(operator=operator):
                wear_ids = [
                    wear_id
                    for part, wear_id, assigned_operator in C02_SCAN_ROWS
                    if part == 1 and assigned_operator == operator
                ]
                self.assertEqual(wear_ids, [expected_wear_id] * 3)
                self.assertEqual(check_count(wear_ids, 6), ("inconsistent", 1))
                self.assertEqual(check_count(wear_ids, 2), ("inconsistent", 1))
                self.assertEqual(check_count(wear_ids, 1), ("supported", 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
