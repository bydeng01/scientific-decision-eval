"""Offline bookkeeping from supplied semantic Choices; never loads references.

This module is not connected to an experimental runner. Unknown scientific
quantities remain None. Review outcomes and model-format errors are separate.
"""


def compare(observed, claimed):
    if observed is None:
        return "insufficient_evidence"
    return "consistent" if observed == claimed else "inconsistent"


def compose(clauses):
    if "inconsistent" in clauses.values():
        return "inconsistent"
    if "insufficient_evidence" in clauses.values():
        return "insufficient_evidence"
    return "consistent"


def derive(problem, answers):
    """Accept a complete question-ID -> option-ID map for one group.

    Missing keys and illegal options are input errors, not missing source
    evidence. Scientific fallback answers stop composition for this group;
    conflicts take precedence, then unlisted answers, then insufficient evidence.
    """
    expected = {q["question_id"]: q for q in problem["questions"]}
    if set(answers) != set(expected):
        raise ValueError("Supply exactly the questions belonging to this group")
    for qid, choice in answers.items():
        if choice not in expected[qid]["options"]:
            raise ValueError(f"Unknown option for {qid}: {choice}")
    for choice, status in [("conflicting", "evidence_conflict"),
                           ("other", "candidate_completion_required"),
                           ("not_stated", "insufficient_evidence")]:
        if choice in answers.values():
            return {"status": status, "counts": None, "clauses": None,
                    "final_label": None}

    pid = problem["problem_id"]
    a, b = [answers[q["question_id"]] for q in problem["questions"]]
    records, claimed = problem["records"], problem["declared_counts"]
    if pid == "B001":
        rows = [r for r in records["census"]
                if r["lineage"] == "Dioxin" and r["generation"] == 3]
        if len(rows) != 1:
            raise ValueError("Expected one selected F3 Dioxin census row")
        pups = sum(r["female_pups"] + r["male_pups"] for r in rows)
        litters = sum(r["weaned_litters"] for r in rows)
        injected = pups if a in {"each_generation", "f3_animals"} else 0
        # The future generation of the fetal germ cells is an explicit semantic
        # mapping, not an arithmetic question delegated to a model.
        reach = {"maternal_soma_only": [0],
                 "mother_and_fetal_soma_only": [0, 1],
                 "mother_embryo_and_fetal_germline": [0, 1, 2],
                 "all_descendants": None}[b]
        first_beyond = max(reach) + 1 if reach is not None else None
        counts = {"F3_pups": pups, "F3_weaned_litters": litters,
                  "newly_injected_F3_animals": injected,
                  "first_generation_beyond_original_window": first_beyond,
                  "distinct_F0_ancestors": None}
        clauses = {"new_F3_injections": compare(injected, claimed["newly_injected_F3_animals"]),
                   "first_generation_beyond_window": ("inconsistent" if reach is None else
                       compare(first_beyond, claimed["first_generation_beyond_original_window"]))}
    elif pid == "B002":
        series = {r["experiment"]: r for r in records["series"]}
        n = {key: len(r["resistant_colonies"]) for key, r in series.items()}
        grouping = {"shared_then_separate": (False, True),
                    "separate_then_shared": (True, False),
                    "both_separate": (True, True), "both_shared": (False, False)}[a]
        histories = {key: n[key] if separate else int(n[key] > 0)
                     for key, separate in zip(("11a", "11"), grouping)}
        counts = {"platings": n, "growth_histories": histories,
                  "colony_totals": {k: sum(r["resistant_colonies"]) for k, r in series.items()},
                  "exact_mutation_origins": None}
        identity = {"one_origin_per_cell": "consistent", "clonal_descendants": "inconsistent",
                    "selection_creates_each_origin": "consistent",
                    "repeated_image": "inconsistent"}[b]
        clauses = {"independent_histories_11a": compare(histories["11a"], claimed["independent_growth_histories_11a"]),
                   "one_colony_one_origin": identity}
    elif pid == "B003":
        selected = [p for p in records["pools"] if p["pool_size"] == records["select_pool_size"]]
        if len({p["pool_id"] for p in selected}) != len(selected):
            raise ValueError("Duplicate pool record")
        contributors = set().union(*(set(p["contributors"]) for p in selected))
        genotypes = sorted({p["genotype"] for p in selected})
        by_group = {g: len(set().union(*(set(p["contributors"]) for p in selected if p["genotype"] == g)))
                    for g in genotypes}
        profiles = {"pool_aggregate": 0,
                    "all_individuals_resolved": sum(len(p["contributors"]) for p in selected),
                    "some_individuals_resolved": None, "new_single_animal": 0}[b]
        counts = {"selected_libraries": len(selected), "distinct_contributors": len(contributors),
                  "distinct_contributors_by_genotype": by_group,
                  "contributor_appearances": sum(len(p["contributors"]) for p in selected),
                  "separately_observed_contributor_profiles": profiles}
        clauses = {"distinct_mice": compare(len(contributors), claimed["distinct_mice"]),
                   "individual_profiles": compare(profiles, claimed["separately_observed_mouse_profiles"]),
                   "pooling_only_after_individual_measurement":
                       "consistent" if a == "numerical_average_only" else "inconsistent"}
    elif pid == "B004":
        counts = {"deep_sequenced_hybrid_founders": records["deep_sequenced_hybrid_founders"],
                  "reported_mutant_alleles": records["reported_mutant_alleles_at_threshold"],
                  "validated_new_germline_lines": None}
        uniform = {"within_founder_mosaicism": "inconsistent",
                   "uniform_one_allele_pair": "insufficient_evidence",
                   "one_founder_per_allele": "insufficient_evidence",
                   "no_edit_detected": "inconsistent"}[a]
        # A uniform #30 alone would not establish the claim about EVERY founder.
        # Q02 distinguishes the marker, not a count of successfully bred lines.
        clauses = {"every_albino_founder_uniform": uniform,
                   "separately_injected_founders": compare(counts["deep_sequenced_hybrid_founders"], claimed["separately_injected_founders_in_deep_sequencing_subset"]),
                   "validated_new_germline_lines": "insufficient_evidence",
                   "albino_offspring_uniquely_identify_new_allele": {
                       "preexisting_albino_allele": "inconsistent",
                       "unique_new_allele_marker": "consistent",
                       "no_germline_possible": "inconsistent",
                       "all_hybrid_alleles_verified": "insufficient_evidence"}[b]}
    else:
        raise ValueError(f"Unknown group: {pid}")
    return {"status": "derived", "semantic_choices": [a, b], "counts": counts,
            "clauses": clauses, "final_label": compose(clauses)}
