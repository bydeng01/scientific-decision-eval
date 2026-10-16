"""Build an initial, unreviewed development package.

This historical preparation recipe contains the initial proposed answer key. Current review status is in evaluation.json and review_decisions.json. Never pass this recipe to a model as input.
Do not rerun after user review without preserving and incorporating review decisions.
"""
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ACCESS = "2026-09-21 (UTC); 2026-09-20 (America/New_York)"
STATUS = "user_prepared_pending_review"
SOURCES = []
PROBLEMS = []


def source(sid, title, url, version, family, files, locations, limitations, doi=None, related=None):
    SOURCES.append(dict(source_id=sid, title=title, url=url, doi=doi,
                        version=version, access_date=ACCESS, source_family=family,
                        local_files=files, inspected_locations=locations,
                        limitations=limitations, related_sources=related or []))


def evidence(sid, location, text):
    return dict(source_id=sid, location=location, kind="source_faithful_adaptation", text=text)


def question(qid, instruction, options, reference, rationale, role, partial=False):
    # These coverage/binary dependence questions have no remaining substantive
    # outside category. Other unit/mechanism questions may have one.
    include_other = qid not in {"E004-Q02", "E007-Q02", "E009-Q01", "E010-Q02"}
    tail = " Select exactly one option. "
    if include_other:
        tail += "Use other only when the evidence establishes an answer outside the substantive alternatives. "
    tail += ("Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. "
            "Use conflicting only for unresolved incompatible evidence about this same judgment and scope.")
    if partial:
        tail += " Use partial_identification when some required provenance is established but the requested complete assignment is unavailable; this takes precedence over not_stated. A known mixture is not itself a conflict."
    opts = dict(options)
    if include_other:
        opts['other']="The evidence establishes a different substantive answer from those listed."
    opts.update(not_stated="The supplied evidence does not establish the requested judgment.",
                conflicting="The supplied evidence contains unresolved incompatible accounts of this judgment and scope.")
    return dict(question_id=qid, instruction=instruction+tail, options=opts,
                reference_option=reference, evidence_rationale=rationale,
                downstream_role=role, review_status=STATUS, prepared_by="user",
                approved_by_user=False, approval_evidence=None)


def problem(pid, title, sids, target, scope, ev, claim, qs, significance, code, issues, closest, difference, signature, records=None):
    PROBLEMS.append(dict(problem_id=pid, title=title, source_ids=sids,
                         target_treatment=target, scope=scope, evidence=ev,
                         scientific_claim=claim, claim_origin="benchmark_constructed; not attributed to the source authors",
                         questions=qs, scientific_significance=significance,
                         deterministic_work=code, review_issues=issues,
                         closest_existing_problem_ids=closest, substantive_difference=difference,
                         structure_without_domain_nouns=signature,
                         records=records or {}, review_status=STATUS))


source("N-STRIP", "NIST/SEMATECH e-Handbook: 5.5.5. How can I account for nested variation (restricted randomization)?",
       "https://www.itl.nist.gov/div898/handbook/pri/section5/pri55.htm", "Undated live handbook page, archived at access", "NIST-HANDBOOK",
       ["evidence/NIST-pri55.html", "evidence/NIST-pri55.txt", "evidence/NIST-figure-5-16.gif", "evidence/NIST-figure-5-16.png"],
       ["Strip-Plot Designs: wafer-processing example", "Figure 5.16 and surrounding execution-order paragraphs", "Three sizes of experimental units", "Replication"],
       ["Authoritative methodological illustration, not a reported empirical wafer dataset.",
        "The D/E/F stage is annealing. An operation-label typo in the source is normalized to 'annealed' in the benchmark adaptation, consistently with the factor definitions and diagram. Original source files retain their original wording for provenance."],
       related=["Existing source N and problem C01 use the same handbook page, but the electroplating example."])
source("WIND-2021", "Results from a wake-steering experiment at a commercial wind plant: investigating the wind speed dependence of wake-steering performance",
       "https://wes.copernicus.org/articles/6/1427/2021/", "Final article, 12 November 2021, Wind Energy Science 6, 1427-1453", "SMV-WAKE-STEERING",
       ["evidence/wind.html", "evidence/wind.pdf", "evidence/wind.txt", "evidence/wind-p06.png", "evidence/wind-p09.png", "evidence/wind-p10.png"],
       ["Sections 2.1-2.2, pp. 1430-1432 (PDF 4-6)", "Figure 5, p. 1432 (PDF 6)", "Sections 4.1-4.3, pp. 1435-1436 (PDF 9-10)"],
       ["Hourly toggling is documented; independent random allocation of each hour is not established.", "The paper reports resampling one-minute observations. That analysis description is retained; the present question concerns assignment, not a verdict on all confidence intervals.", "No timestamped campaign log is included in this package; no total number of eligible hourly applications is inferred."],
       doi="10.5194/wes-6-1427-2021")
source("CAT-2020", "Copper nanoparticles on controlled pore glass (CPG) as highly efficient heterogeneous catalysts for 'click reactions'",
       "https://www.nature.com/articles/s41598-020-77629-3", "Scientific Reports 10, 20547, 25 November 2020", "CU-CPG-RECYCLING",
       ["evidence/catalyst.html", "evidence/catalyst.pdf", "evidence/catalyst.txt", "evidence/catalyst-p03.png", "evidence/catalyst-p05.png", "evidence/catalyst-p06.png"],
       ["Results and discussion, PDF p. 3", "Figures 2 and 3, PDF p. 5", "Procedure for recycling, PDF pp. 3 and 6"],
       ["Figure 2 endpoint conversion does not establish unchanged kinetics: Figure 3 and the text report slowing after two cycles.", "The recycling procedure uses two hours; the three-hour general procedure is a different scope.", "No independent synthesis-series replication or atom-by-atom recovery mass balance is established by these eight cycle records."], doi="10.1038/s41598-020-77629-3")
source("POW-2023", "Effective Ti-6Al-4V Powder Recycling in LPBF Additive Manufacturing Considering Powder History",
       "https://researchonline.jcu.edu.au/86205/7/86205.pdf", "Repository copy with final Sustainability 2023, 15, 15582 headers; published 2 November 2023", "TI64-POWDER-HISTORY",
       ["evidence/powder.pdf", "evidence/powder.txt", "evidence/powder-repository.html", "evidence/powder-repository.txt", "evidence/powder-p05.png", "evidence/powder-p06.png"],
       ["Section 2.3, PDF pp. 4-6", "Figures 1-2, PDF pp. 5-6", "Build-8 top-up paragraph and final paragraph, PDF p. 6"],
       ["The repository PDF visibly overprints earlier text on portions of pp. 5-6, including older peer-review headers. The build-8 statement and final sampling paragraph remain readable; the overprint is saved, not silently repaired.", "The bulk index assumes degradation related to material built and no interactions. It is not a particle-level lineage ledger.", "Exact input-lot IDs, fractions, and per-particle exposure histories are not established by the supplied methods. This is an evidence-coverage statement, not a claim that the investigators never kept such records.", "Publisher HTML returned HTTP 403 during acquisition; the repository copy was inspected."], doi="10.3390/su152115582")
source("FAT-2022", "Bayesian Optimised Collection Strategies for Fatigue Strength Testing",
       "https://arxiv.org/pdf/2107.02685v3", "arXiv:2107.02685v3, 21 September 2022; 27-page preprint", "304L-FATIGUE-STRATEGIES",
       ["evidence/fatigue-2107.02685v3.pdf", "evidence/fatigue-2107.02685v3.txt", "evidence/fatigue-2107.02685v3-p03.png", "evidence/fatigue-2107.02685v3-p17.png", "evidence/fatigue-2107.02685v3-p18.png"],
       ["Table 2, PDF p. 3", "Section 4 and Table 3, PDF p. 17", "Figure 11(a) and caption, PDF p. 18"],
       ["The regular staircase in Figure 11(a) is the selected protocol. The step tests in Figure 11(c,d) repeatedly load the same specimen and must not be merged into this scope.", "Random specimen extraction and randomized protocol order do not imply randomized stress selection.", "No digitized stress-by-specimen dataset is asserted; no exact count at a chosen stress is estimated from plot pixels.", "Figure 11(a)'s visible stress spacing appears smaller than the 30 MPa increment stated in Table 3 and the figure caption. The achieved numerical step is unresolved here; the next-specimen and outcome-dependent allocation descriptions remain explicit."], doi="10.48550/arXiv.2107.02685")
source("COS-2018", "Statistical properties of paired fixed fields",
       "https://arxiv.org/pdf/1806.01871v1", "arXiv:1806.01871v1, submitted 5 June 2018; PDF draft dated 7 June 2018", "PAIRED-FIXED-COSMOLOGY",
       ["evidence/paired-fixed-1806.01871v1.pdf", "evidence/paired-fixed-1806.01871v1.txt", "evidence/paired-fixed-1806.01871v1-p02.png", "evidence/paired-fixed-1806.01871v1-p04.png"],
       ["Section 2: fixed and paired fields, PDF pp. 2-3", "Section 3.1 and Table 1, PDF pp. 3-4", "Section 3.2, Equation 10 and discussion of cross-correlation, PDF p. 5"],
       ["Phase reversal is a deterministic initial-field relationship; it does not mean every final observable is perfectly anticorrelated.", "The N1000 paired-fixed subset is separate from the 100 standard realizations and the N20/H200/H20 sets.", "The published article DOI 10.3847/1538-4357/aae52b is a related version, not a second source or an audited replacement for v1."], doi="10.48550/arXiv.1806.01871")
source("LENS2-DOC", "CESM2 Large Ensemble Community Project (LENS2)",
       "https://www.cesm.ucar.edu/community-projects/lens2", "Undated official project documentation, live snapshot at access", "CESM2-LENS2",
       ["evidence/lens2.html", "evidence/lens2.txt"],
       ["Initialization descriptions for members 1-10, 11-90, and 91-100", "Modifications incorporated in the second half of the LENS2 simulations, all paragraphs"],
       ["The SMBB half also contains emission and carbon-flux code corrections; a between-half contrast does not isolate smoothing alone.", "The project reports no significant model-solution or climate-changing impacts from the respective corrections. That report does not establish identical implementations.", "The local snapshot is authoritative for this problem; a future website update could change the documentation."], related=["The project cites Rodgers et al. (2021); the paper is not counted as another independently inspected source here."])
source("FOLD-2025", "Powerful Foldover Designs",
       "https://arxiv.org/pdf/2507.14648v1", "arXiv:2507.14648v1, submitted 19 July 2025; PDF cover dated 22 July 2025", "ETHYLENE-FOLDOVER",
       ["evidence/foldover-2507.14648.pdf", "evidence/foldover-2507.14648.txt", "evidence/foldover-2507.14648-p22.png", "evidence/foldover-2507.14648-p23.png", "evidence/foldover-table7.png"],
       ["Introduction: sign-reversing foldover, PDF p. 2", "Section 6, Ethylene Experiment, PDF pp. 22-23", "Table 7 and caption, PDF p. 23", "Table 8 caption, PDF p. 23"],
       ["The caption describes foldover pairs, while the preceding paragraph explicitly mentions both replicates and foldover pairs. The full matrix resolves which are equal conditions; no incompatible assignment remains.", "The preprint labels process factors 1-8 without a complete physical factor-name/level dictionary. The judgment is limited to its coded design, not chemical equivalence outside that design.", "Later publication is not substituted for the inspected preprint."], doi="10.48550/arXiv.2507.14648")
source("N-FOLD", "NIST/SEMATECH e-Handbook: 5.3.3.8.1. Mirror-image foldover designs",
       "https://www.itl.nist.gov/div898/handbook/pri/section3/pri3381.htm", "Undated live handbook page, archived at access", "NIST-HANDBOOK",
       ["evidence/NIST-foldover.html", "evidence/NIST-foldover.txt"],
       ["Foldover design definition and alias explanation"],
       ["Methodological corroboration only; the ethylene treatment records come from FOLD-2025."], related=["N-STRIP and existing source N belong to the same handbook."])
source("MET-2016", "Extensive Comparison between INRIM and a Secondary Calibration Laboratory using a Multifunction Electrical Calibrator",
       "https://arxiv.org/pdf/1510.07866v3", "arXiv:1510.07866v3, 21 April 2016; downloaded PDF has 7 pages", "INRIM-MFC-ILC",
       ["evidence/metrology-1510.07866v3.pdf", "evidence/metrology-1510.07866v3.txt", "evidence/metrology-1510.07866v3-p03.png", "evidence/metrology-1510.07866v3-p04.png"],
       ["Section III.A, PDF p. 2", "Sections IV-V, Figure 3 and Equations 1-5, PDF p. 3", "Table II, PDF p. 4", "Conclusions, PDF p. 6"],
       ["The preprint retains a template identification header; this is not a second experiment.", "The source takes precautions against possible drift and reports instrument stability; a bracketing design does not establish observed drift.", "Shared traceability creates particular correlated uncertainty contributions. Separate laboratory executions remain real; the question does not declare all uncertainty components identical or all errors perfectly correlated."], doi="10.48550/arXiv.1510.07866")
source("CLOUD-2018", "Evaluation of the Wyoming Weather Modification Pilot Project (WWMPP) Using Two Approaches: Traditional Statistics and Ensemble Modeling",
       "https://www.researchgate.net/publication/328180082_Evaluation_of_the_Wyoming_Weather_Modification_Pilot_Project_WWMPP_Using_Two_Approaches_Traditional_Statistics_and_Ensemble_Modeling",
       "Rasmussen et al., Journal of Applied Meteorology and Climatology 57 (2018), 2639-2660; author-uploaded full text, 26 December 2018", "WWMPP",
       [], ["Section 2, pp. 2640-2642", "Figure 1 caption and complementary-shading explanation, pp. 2641-2642", "Section 2a, Table 1 and Figure 2, pp. 2642-2643", "Section 2 statistical discussion"],
       ["Actual full article text was inspected through the author-uploaded ResearchGate page; PDF retrieval and the publisher endpoint returned HTTP 403. The local evidence adaptation and the investigators' 2014 presentation preserve the selected design evidence.", "The prose calls the winters 2008-13, while Table 1 uses 2008/09-2013/14. The present scope is the explicitly reported 118 retained EUs, not reconstructed dates.", "Wind-direction criteria differ between the introductory account and Section 2b; this does not change the documented complementary assignment.", "Cross-range exposure evidence used in E010 comes from CLOUD-2014 slides 24 and 29, not an independently replicated experiment.", "The paper's p-value gloss is not adopted as a probability that the null hypothesis is true; significance testing is outside this problem."],
       doi="10.1175/JAMC-D-17-0335.1", related=["CLOUD-2014 is the same experiment, not independent source replication."])
source("CLOUD-2014", "Wyoming Weather Modification Pilot Project: Final Results Presentation",
       "https://crwua.org/wp-content/uploads/2024/01/WWMPP-CRWUA-Dec-2014.pdf", "Investigators' December 2014 results presentation; 50-slide public copy hosted in a 2024 directory", "WWMPP",
       ["evidence/cloud-2014-report.pdf", "evidence/cloud-2014-report.txt", "evidence/cloud-2014-report-p16.png", "evidence/cloud-2014-report-p17.png", "evidence/cloud-2014-report-p18.png", "evidence/cloud-2014-report-p24.png", "evidence/cloud-2014-report-p29.png"],
       ["Slides 16-18: paired design, measurements, and 118-case assignment plot", "Slides 24 and 29: possible cross-range contamination"],
       ["The slide plot labels Medicine Bow, whereas the 2018 Figure 1 plot labels Sierra Madre. Their colors must not be joined as though they identify the same target.", "The PDF has malformed object offsets tolerated by the PDF readers; rendered slides were checked.", "The slide p-value wording is not used as a statistical reference."], related=["CLOUD-2018 reports the same WWMPP trial."])


problem("E001", "Wafer regrouping across two processing stages", ["N-STRIP"],
        "Joint implant-factor (A, B, C) and anneal-factor (D, E, F) settings in NIST Figure 5.16.",
        "The single illustrated block: implant combinations 1-8 and anneal combinations 1-8. Each figure cell is one wafer. Combination numbers are treatment codes, not persistent wafer serial numbers.",
        [evidence("N-STRIP", "Strip-Plot Designs; Figure 5.16 and execution paragraphs", "Each implant setting processes eight wafers together. After all implant batches, every anneal batch receives one wafer from each implant batch and is annealed at its assigned D/E/F setting. Thus annealing regroups the wafers. The first implant setting executed is 3 and the first anneal setting executed is 5; treatment codes are not execution-order indices."),
         evidence("N-STRIP", "Three sizes of experimental units; Replication", "The handbook assigns implant effects to implant batches, anneal effects to anneal batches, and cross-stage interactions to individual wafers. The figure is one block or replicate. Without replicated blocks, it describes using A*B*C and D*E*F as error terms only under models excluding those three-factor interactions; each then supplies one degree of freedom.")],
        "Within the illustrated block, each complete implant-by-anneal setting combination has eight separately processed wafer replicates.",
        [question("E001-Q01", "For this block, how are the wafer memberships of implant batches related to those of anneal batches?",
                  [("same_partition", "Each implant batch remains intact as one corresponding anneal batch."),
                   ("anneal_nested", "Each anneal batch is wholly contained within one implant batch, and at least one implant batch supplies multiple anneal batches."),
                   ("implant_nested", "Each implant batch is wholly contained within one anneal batch, and at least one anneal batch contains multiple implant batches."),
                   ("crossed_regrouping", "Each anneal batch combines wafers from multiple implant batches, and each implant batch supplies multiple anneal batches.")],
                  "crossed_regrouping", "The source explicitly sends one wafer from each implant batch to each anneal setting; neither stage's batch partition contains the other.",
                  "Selects a two-stage membership representation before code groups complete treatment combinations."),
         question("E001-Q02", "Which experimental unit does the source assign to interaction effects involving both an implant factor and an anneal factor in this block?",
                  [("implant_batch", "The group of wafers processed together in one implant operation."),
                   ("anneal_batch", "The group of wafers processed together in one anneal operation."),
                   ("wafer", "An individual wafer receiving one implant setting and one anneal setting."),
                   ("whole_block", "The complete block containing all implant and anneal setting combinations.")],
                  "wafer", "The handbook explicitly identifies the single wafer as the unit for cross-stage interaction effects.",
                  "Determines the relevant level for the joint-treatment replication claim; it does not count wafers or blocks.")],
        "A one-parent batch identifier loses one treatment stage. The correct grouping prevents eight different joint settings from being treated as eight repeats of one joint setting.",
        dict(resolution_status="established_for_supplied_structured_evidence", judgment="Interpret the crossed membership and the effect-specific experimental unit.",
             code="Enumerate the source-described Cartesian grid, group wafers by both setting codes, and compare per-cell replication with the claim. Keep full-block replication separate. Source explanations make a zero-model-call route valid.",
             expected_outcome=dict(claim_assessment="inconsistent", implant_batches=8, anneal_batches=8, wafer_records=64, full_setting_combinations=64, wafers_per_full_setting=1, complete_blocks=1),
             inference_boundary="One wafer per cell is not a claim of 64 mutually independent errors or replicated whole blocks."),
        ["Confirm that an authoritative, explicitly illustrative semiconductor design is admissible alongside empirical studies.", "The isolated D/E/F operation-label slip is resolved by the repeated definition and figure, not a basis for a conflicting reference."],
        ["C01", "D01"], "C01 has nested whole-plot and strip treatments. Here the same objects are regrouped between stages, producing crossed memberships and an intersection unit. A single parent tree no longer represents the assignment.",
        "Objects first share one partition, then are redistributed across another; effects depend on either partition or their intersections.",
        records=dict(implant_setting_codes=list(range(1,9)), anneal_setting_codes=list(range(1,9)), wafers_per_intersection=1, illustrated_blocks=1))

problem("E002", "Controller applications across hourly switches", ["WIND-2021"],
        "Baseline versus wake-steering controller mode on upstream turbine SMV6, with SMV5 downstream.",
        "The reported SMV experiment's hourly mode toggles and one-minute analysis records; no new turbine deployment or complete campaign count is inferred.",
        [evidence("WIND-2021", "Sections 2.1-2.2 and Figure 5, PDF pp. 4-6", "Measurements are downsampled to one-minute records. Figure 5 switches SMV6 between baseline and wake-steering control hourly. The offset within controlled periods follows the wind-dependent controller schedule; hourly mode assignment is different from instantaneous yaw offset."),
         evidence("WIND-2021", "Sections 4.1-4.3, PDF pp. 9-10", "After operational and power-curve filtering, the first ten minutes after each mode switch are removed for yaw-controller transients. Further power and lidar-availability filters apply to yaw analyses. The authors bootstrap one-minute observations at least 2,000 times, by wind-direction bin where applicable, resampling baseline and controlled observations separately.")],
        "Each retained one-minute observation represents a separately assigned controller-mode application.",
        [question("E002-Q01", "What defines the reported allocation of baseline versus wake-steering mode on SMV6?",
                  [("fixed_turbine", "Each turbine receives a fixed controller mode for the whole experiment."), ("hourly_switch", "Controller mode alternates across hourly periods on the same turbine."),
                   ("minute_randomization", "Each one-minute measurement receives a new independently randomized controller mode."), ("analysis_bin", "Post hoc wind-direction bins define separate controller-mode assignments.")],
                  "hourly_switch", "Figure 5 explicitly gives an hourly toggle on SMV6; one-minute sampling and wind bins do not reassign the controller mode.", "Defines the application boundary before timestamps are grouped."),
         question("E002-Q02", "What is the role of the first ten minutes after a controller-mode switch in the reported analysis?",
                  [("transition_exclusion", "They are a transition segment of the switched application, excluded to allow for controller transients."),
                   ("separate_treatment", "They are a separately assigned third controller treatment."), ("baseline_relabel", "They are relabeled as baseline observations regardless of the switched mode."),
                   ("new_replication", "They are independent repeat applications retained to estimate controller replication.")],
                  "transition_exclusion", "Section 4.1 removes this interval because of yaw-controller transients; it does not create or relabel an assignment.", "Tells code how to retain application identity while excluding transition observations.")],
        "Replicating time samples does not replicate controller assignments. The transition rule also prevents a new mode's early response from being mistaken for a separately applied treatment.",
        dict(resolution_status="established_for_scoped_claim; full_campaign_count_unassessed", judgment="Interpret the switch boundary and transition segment.", code="With timestamped records, attach observations to hourly mode periods, apply the source filters, and count retained applications separately from rows. No actual log is supplied, so no campaign total is generated. The present claim is resolved by the explicit protocol.",
             expected_outcome=dict(claim_assessment="inconsistent", actual_eligible_application_count=None, minute_rows_are_new_assignments=False),
             inference_boundary="Alternation does not establish randomization or temporal independence of successive periods."),
        ["The case records the authors' minute-bootstrap method; its uncertainty estimates are not reassessed."],
        ["D03", "C02"], "D03 lacks execution boundaries; these boundaries are explicit temporal switches with a transient exclusion. C02 repeatedly measures a completed event, whereas SMV6 actually changes treatment during reuse.",
        "One carrier receives changing interventions over time; observations must inherit switch-period identity after a transition filter.")

problem("E003", "Catalyst recovery across reaction cycles", ["CAT-2020"],
        "Cu-AmP-CPG catalyst 1 used for benzyl azide 2a plus propargyl alcohol 3a to produce 4a.",
        "The eight consecutive recycling cycles in Figure 2; Figure 3's C1-C3 kinetic curves provide context. The different-substrate series in Table 3 is excluded.",
        [evidence("CAT-2020", "Recycling procedure, PDF pp. 3 and 6; Figure 2, PDF p. 5", "The recycling reaction uses 2a (0.25 mmol), 3a (0.38 mmol), catalyst (10 mg, 5 mol%), and t-BuOH/water (1:1) at 70 degrees C for two hours. Solids are separated, washed, and the recovered catalyst is used in the next cycle. Figure 2 reports eight consecutive cycles with high endpoint conversion."),
         evidence("CAT-2020", "Results, PDF p. 3; Figure 3, PDF p. 5", "The source reports that reaction rates begin to decrease after two cycles, despite completion before the two-hour endpoint. Figure 3 distinguishes C1, C2, and C3. Catalyst synthesis is described separately from recovery and reuse.")],
        "The eight Figure 2 cycles are eight independent preparations of fresh catalyst 1 tested once each.",
        [question("E003-Q01", "What material relationship connects the catalyst used in consecutive Figure 2 reaction cycles?",
                  [("fresh_preparation", "Each cycle uses catalyst from a newly performed synthesis, with no recovered catalyst carried forward."),
                   ("recovered_carryover", "Catalyst recovered from the preceding reaction is carried into the next reaction cycle."),
                   ("fresh_aliquots", "Each cycle uses a previously unused aliquot split from one preparation before any reaction."),
                   ("one_reaction_samples", "The cycle labels identify repeated samples of one uninterrupted reaction mixture.")],
                  "recovered_carryover", "The recycling method recovers, washes, and reuses the solid in the next experimental cycle. These are new reaction operations with inherited catalyst history.", "Distinguishes reuse-performance evidence from fresh-preparation replication before code labels the claim.")],
        "Cycle results address retained activity of a reused catalyst. They cannot estimate variation across eight independent catalyst syntheses, and equal endpoint conversions do not remove the observed kinetic history.",
        dict(resolution_status="established_for_supplied_protocol", judgment="Identify material carryover across separately initiated reactions.", code="Represent the eight stated cycles as a chronological reuse chain, retain reaction-operation and catalyst-preparation levels separately, and reject the fresh-preparation interpretation. This explicit method is code-resolvable; no model call is required.",
             expected_outcome=dict(claim_assessment="inconsistent", reported_reaction_cycles=8, documented_recycling_series=1, independent_synthesis_count_established_by_cycles=None),
             inference_boundary="One described reuse series is not proof that the entire study performed only one synthesis or one series."),
        ["Recovery does not establish an exact atom-level mass balance; the reference is procedural carryover, not perfect conservation."],
        ["D01", "C02"], "D01's descendants are freshly split specimens; C02's scans remeasure a finished event. Here new reaction operations alter and reuse the same catalyst over an ordered history, with documented kinetic change.",
        "A material carrier is recovered after an operation and reused in a new operation; later outcomes inherit earlier exposure.")

problem("E004", "Powder top-up and incomplete lineage coverage", ["POW-2023"],
        "Recycling history of Ti-6Al-4V feedstock used in the LPBF top-up process.",
        "Section 2.3's build-8-and-later top-up regime through build 10. The question concerns feedstock provenance, not the number of tensile specimens or scan tracks.",
        [evidence("POW-2023", "Section 2.3 and Figures 1-2, PDF pp. 4-6", "The process refreshes recovered powder with added powder. From build 8, the authors add previously reused powder with different extents of recycling. The R index aggregates powder consumption and input history; its assumptions relate degradation to material built and exclude interactions. The paper explains why a simple reuse-cycle number is inadequate."),
         evidence("POW-2023", "Section 2.3 final paragraphs, PDF p. 6", "Characterized R values 0.00, 0.04, 0.15, 0.24, and 0.40 refer to virgin powder and the starts of builds 1, 3, 6, and 10, respectively, with top-up as necessary. R can increase during a build as powder is converted into solid material. The build-8 paragraph describes the addition of previously reused powder of various recycling extents.")],
        "Build 8 feedstock can be represented as one parent lot whose particles all have the same prior recycling history; its exact parent-lot assignments can be recovered from the reported bulk history alone.",
        [question("E004-Q01", "Which membership pattern is established for the prior recycling histories of powder entering the build-8-and-later top-up regime?",
                  [("one_common_history", "All entering powder shares one identical prior recycling history."), ("mixed_histories", "Entering powder combines portions with different prior recycling histories."),
                   ("virgin_replacement", "Each build replaces all recovered powder with unused virgin powder."), ("separate_unmixed", "Different-history portions are processed separately without mixing in a build's feedstock.")],
                  "mixed_histories", "The build-8 paragraph explicitly adds previously reused powder with different extents of recycling. This is a known mixture, not ambiguous membership.", "Selects a multiple-parent history representation; it supplies no exact parent count."),
         question("E004-Q02", "How completely does the supplied evidence identify every input portion's original lot, mixture fraction, and prior-build history for build 8?",
                  [("complete_assignment", "All requested lot identities, mixture fractions, and prior-build histories are established for every input portion."),
                   ("partial_identification", "Some provenance is established, including the presence of different reuse histories, but the complete requested input-portion assignment is unavailable.")],
                  "partial_identification", "The protocol establishes the mixed-history origin, but supplies no complete lot/fraction/exposure mapping. R does not uniquely invert to that mapping.",
                  "Prevents code from turning a broad mixture category into an exact count or allocation of source lots.", partial=True)],
        "A bulk recycling index can support a process-level comparison while failing to identify particle or lot-level replication. Lineage merges require both membership structure and coverage checks.",
        dict(resolution_status="established_for_mixture_and_coverage; exact_lineage_not_estimable_from_supplied_evidence", judgment="Separate a known mixed-origin structure from the completeness of its assignments.", code="Retain a multiple-parent relation with unresolved lot assignments. Do not create one parent per history label, invert R into reuse counts, or replace unknown counts with zero.",
             expected_outcome=dict(claim_assessment="inconsistent_single_history; insufficient_exact_assignments", exact_parent_lot_count=None, complete_assignment_available=False),
             inference_boundary="Missing supplied assignments do not establish missing experimental replication or missing records in the actual study."),
        ["The public PDF's visible overprint is a source-quality issue for review; both rendered pages are saved.", "The partial-identification option refers to exhaustive provenance coverage, not uncertainty about whether mixing occurred."],
        ["D01", "D03"], "D01 is a one-parent split; D03 lacks assignment knowledge. Here a many-parent history merge is positively known while its exhaustive lot allocation remains unavailable. Known mixed membership and incomplete identification lead to separate outputs.",
        "Several previously exposed material streams merge; the merge is known but a bulk summary does not identify every ancestor or fraction.")

problem("E005", "Outcome-dependent stress assignment in a staircase", ["FAT-2022"],
        "Applied fatigue stress in the regular staircase test of 304L stainless-steel foil specimens.",
        "Table 2's staircase/up-down protocol as implemented in Section 4 and Figure 11(a). Figure 11(b-d) are other protocols, not additional observations of the selected allocation rule.",
        [evidence("FAT-2022", "Table 2, PDF p. 3", "In the staircase protocol, the first specimen receives the starting stress. The next specimen receives a stress step down after failure or a step up after runout of the preceding specimen. Each specimen contributes one test. In the separately described step protocol, the same specimen is retested at increasing stress after runout."),
         evidence("FAT-2022", "Section 4 and Table 3, PDF p. 17; Figure 11(a), PDF p. 18", "The experimental material is 304L foil. Specimens were extracted randomly across the foil and assigned to protocols in randomized order to reduce time effects. Table 3 states a 325 MPa start and 30 MPa steps. Figure 11(a) plots the regular staircase sequence; the caption also states 30 MPa increments. The rendered table and figure accompany this evidence.")],
        "Because specimen selection and protocol order were randomized, the stresses in the regular staircase were independently randomized across specimens.",
        [question("E005-Q01", "What determines the next specimen's applied stress in the selected regular staircase protocol?",
                  [("independent_randomization", "A fresh random draw selects stress independently of preceding outcomes."), ("response_adaptive", "The preceding specimen's failure or runout determines an upward or downward stress step."),
                   ("fixed_level", "The initial stress is retained unchanged for every specimen."), ("preordered_schedule", "A preassigned stress sequence is followed regardless of preceding outcomes.")],
                  "response_adaptive", "Table 2 specifies the outcome-dependent update. Randomization of specimen extraction and protocol order is a different operation.", "Identifies dependence in treatment allocation before code reconstructs a stress sequence."),
         question("E005-Q02", "When this regular staircase advances after an outcome, which physical specimen receives the next stress setting?",
                  [("new_specimen", "A new specimen receives the next setting, and the preceding specimen's single test is complete."), ("same_specimen", "The same specimen receives the next setting as another step in its loading history."),
                   ("whole_foil", "The complete foil receives the next setting collectively before specimens are extracted.")],
                  "new_specimen", "The staircase row says next specimen and classifies the protocol as a single test per specimen. Retesting the same specimen belongs to the separate step protocol.", "Separates adaptive dependence between assignments from repeated exposure of one specimen.")],
        "New physical specimens do not make treatment allocation independent of prior outcomes. This distinction changes how repeated stress-level observations enter a fatigue-strength analysis.",
        dict(resolution_status="established_for_explicit_protocol; observed_sequence_reconstruction_unassessed", judgment="Identify the allocation dependency and the specimen boundary.", code="Apply the documented up/down rule to outcome records if available; group equal stresses by code. The 30 MPa increment and grouping operations are computed in code. The offline check verifies the rule's arithmetic at the documented starting value only, not a reconstructed dataset.",
             expected_outcome=dict(claim_assessment="inconsistent", next_stress_after_initial_failure_MPa=295, next_stress_after_initial_runout_MPa=355, observed_replicates_at_any_fixed_stress=None),
             inference_boundary="This is about conditional allocation, not proof that physical specimen failures have a particular correlation."),
        ["The physical specimen boundary and the adaptive assignment are different judgments; approval of one question does not approve the other.", "No stress-level count is digitized or inferred from Figure 11.", "Resolve the apparent plot/parameter spacing discrepancy before any numeric extension. The offline 325 +/- 30 calculation checks only the stated protocol."],
        ["D03", "H01"], "Those problems concern level/run assignment or treatments within a pre-existing specimen. Here the preceding outcome determines a later new specimen's treatment, so the assignment graph includes an outcome-to-treatment link.",
        "A new object is treated at a level chosen from the preceding object's response; object separation and allocation independence diverge.",
        records=dict(starting_stress_MPa=325, step_MPa=30))

problem("E006", "Two executions within one paired-fixed realization", ["COS-2018"],
        "Paired-fixed initialization for the N1000 cosmological N-body simulation set.",
        "Only the 100 paired-fixed realizations in Table 1's N1000 row; exclude its 100 standard realizations and all other simulation sets. One paired-fixed realization contains two phase-related executions.",
        [evidence("COS-2018", "Section 2, PDF pp. 2-3; Table 1, PDF p. 4", "The two fixed fields of a pair use the same fixed Fourier amplitudes, with phases shifted by pi between them. Table 1 lists 100 N1000 paired-fixed realizations and states that each corresponds to two simulations. The simulations are separate executions, not two output snapshots of one execution."),
         evidence("COS-2018", "Section 3.2, PDF p. 5, Equation 10 and cross-correlation discussion", "The authors first average the two simulations' values for a paired-fixed realization, then calculate statistics across realizations. They explicitly analyze the cross-correlation within pairs. Phase flipping does not imply that every evolved observable has perfect negative correlation.")],
        "The N1000 paired-fixed subset supplies 200 independently drawn initial phase fields because it contains 200 separately executed simulations.",
        [question("E006-Q01", "How are the initial phase fields of the two simulations within one paired-fixed realization related?",
                  [("independent_draws", "Both phase fields are independently drawn from the specified phase distribution."), ("phase_reversed", "One phase field is obtained from the other by a pi phase shift, with the same fixed amplitudes."),
                   ("identical_field", "Both simulations use the identical phase field without phase reversal."), ("output_resampling", "The pair is produced by resampling outputs from one completed simulation.")],
                  "phase_reversed", "The source defines the pair through a pi phase shift; a second execution is not a second independent phase draw.", "Identifies the initial-condition coupling that determines the realization boundary."),
         question("E006-Q02", "In the source's paired-fixed statistical construction, which quantity contributes one value before statistics are taken across realizations?",
                  [("individual_execution", "The output of each individual execution, entered separately as an independent realization."), ("pair_average", "The average of the two corresponding outputs within a paired-fixed realization."),
                   ("pair_difference", "The difference between the two corresponding outputs within a paired-fixed realization."), ("all_runs_average", "One average across every N1000 execution, without distinct realization values.")],
                  "pair_average", "Equation 10 averages the two members within a pair before ensemble statistics are formed.", "Selects the aggregation object; code performs averaging and execution-versus-realization counting.")],
        "Execution counts measure computational work. Replication for the reported paired estimator is organized by the deliberately coupled realization, so those counts cannot be interchanged.",
        dict(resolution_status="established_for_supplied_table_and_formalism", judgment="Interpret the phase coupling and reported realization statistic.", code="Multiply the stated realization count by two for execution accounting; retain 100 pair-level values. Do not replace pair-level variation with the variance of 200 independent phase draws.",
             expected_outcome=dict(claim_assessment="inconsistent", paired_realizations=100, paired_execution_count=200, values_entering_pair_ensemble=100),
             inference_boundary="Neither this bookkeeping nor phase reversal establishes an effective sample size for every observable."),
        ["The reference does not require perfect anticorrelation of final nonlinear observables."],
        ["D02", "C02"], "D02 has multiple specimens within one build; C02 has repeated measurements of one event. This source has two genuine full executions, coupled by a deterministic transformation of their initial conditions and deliberately aggregated as one realization.",
        "Two full executions use transformed rather than independently drawn initial inputs; their outputs form one paired statistic.",
        records=dict(paired_realizations=100, executions_per_paired_realization=2))

problem("E007", "Ensemble membership after a forcing-protocol revision", ["LENS2-DOC"],
        "Original CMIP6 biomass-burning forcing versus the revised SMBB implementation in CESM2-LENS2.",
        "All 100 documented LENS2 members, with the forcing change during 1990-2020. Member groups and initialization dates follow the official page; no independent climate-state count is inferred from output fields.",
        [evidence("LENS2-DOC", "Initialization groups; Modifications incorporated in the second half", "LENS2 has two 50-member halves: original biomass-burning forcing and an 11-year-running-mean version, SMBB, affecting 1990-2020. At each of four macro-initialization dates (1231, 1251, 1281, 1301), the first ten micro-perturbation members use original forcing and the second ten use SMBB. Ten additional even-decade initializations use original forcing; ten odd-decade initializations use SMBB."),
         evidence("LENS2-DOC", "Remaining modification paragraphs", "The SMBB implementation also corrects emission-dataset issues and changes the timing of a crop-harvest carbon-flux term. The project reports no significant solution changes from the former corrections and no climate-changing impacts from the latter. Additional output fields also differ.")],
        "All 100 LENS2 members replicate the original biomass-burning forcing implementation; differences between the two documented halves isolate the effect of smoothing that forcing.",
        [question("E007-Q01", "How should the documented members be classified with respect to the original versus SMBB biomass-burning forcing protocol?",
                  [("all_original", "Every member uses the original biomass-burning forcing protocol."), ("all_smbb", "Every member uses the SMBB biomass-burning forcing protocol."),
                   ("two_protocol_groups", "The collection contains members using each of the two documented forcing protocols."), ("within_run_replicates", "Each member contains separate original and SMBB runs as internal replicate executions.")],
                  "two_protocol_groups", "The official page explicitly divides the collection into original and SMBB halves with a mapping across initialization groups.", "Selects treatment-protocol membership before code totals matching members."),
         question("E007-Q02", "Does the documented difference between these halves isolate biomass-burning smoothing as the only implementation change?",
                  [("smoothing_only", "Yes; the two halves differ only in the biomass-burning smoothing operation."), ("bundled_changes", "No; the SMBB half also incorporates other documented implementation changes."),
                   ("initialization_only", "No forcing or code difference is present; only the initial conditions differ.")],
                  "bundled_changes", "The same documentation lists emission and carbon-flux corrections in the SMBB half. Reported small impacts do not make a between-half contrast a single-change intervention.", "Blocks a smoothing-only interpretation of a group comparison even after code has correctly assigned members.")],
        "Nominal project membership does not establish identical treatment implementation. Correct subgroup counts still leave an identification problem when changes were introduced together.",
        dict(resolution_status="established_for_documented_group_mapping", judgment="Interpret protocol identity and the scope of the implementation change.", code="Use the documented group mapping to count original and SMBB members, then compose separate membership and single-change-identification outcomes. Do not infer treatment effects or statistical independence.",
             expected_outcome=dict(claim_assessment="inconsistent_in_both_clauses", original_members=50, smbb_members=50, total_members=100, smoothing_only_contrast=False),
             inference_boundary="The documentation reports evaluations of the corrections; this problem does not estimate their effects."),
        ["Both clauses share one underlying decision: whether these members replicate an identified forcing intervention. They do not count as two scientific problems.", "The source's reported impact checks are retained in model-facing evidence."],
        ["H01", "D03"], "H01 varies factors within a physical treatment scope and D03 separates a named level from missing runs. LENS2 documents a mid-project protocol version change bundled with other changes, plus a full group mapping; membership is known but a single-change causal contrast is not identified.",
        "A nominal collection contains implementation versions; version membership is mapped, but concurrent changes prevent isolating one intervention.",
        records=dict(macro_start_dates=[1231,1251,1281,1301], original_micro_members_per_date=10, smbb_micro_members_per_date=10,
                     original_extra_start_years=[1001,1021,1041,1061,1081,1101,1121,1141,1161,1181],
                     smbb_extra_start_years=[1011,1031,1051,1071,1091,1111,1131,1151,1171,1191]))

FACTOR_ROWS = [
    "+ - + - + - + - + - - - + + - + + - + -",
    "- + - + + - - + + - - - + + + - + - + -",
    "+ - - + - + + - + - + + - - + - - + + -",
    "+ - - + - + + - - + + + - - - + + - - +",
    "+ - - + + - + - + - - - + + + - - + - +",
    "- + - + + - + - - + - - + + - + - + + -",
    "- + - + + - - + + - + + - - - + - + + -",
    "- + + - + - + - - + + + - - + - + - - +",
]
Y = [.30,.65,.41,.53,.62,.42,.28,.65,.64,.33,.39,.35,.57,.60,.66,.25,.50,.41,.59,.35]
FOLD_RECORDS = [dict(column=i+1, factor_settings=[r.split()[i] for r in FACTOR_ROWS], y=Y[i]) for i in range(20)]
problem("E008", "Exact treatment repetition within a foldover design", ["FOLD-2025", "N-FOLD"],
        "The complete eight-factor coded treatment setting in the ethylene experiment.",
        "All 20 run columns of Table 7, factors 1-8 and response y. Column numbers in the transcription are left-to-right table indices assigned for this package, not claimed original run IDs or chronological order.",
        [evidence("FOLD-2025", "Section 6, PDF pp. 22-23; Table 7, PDF p. 23", "The ethylene experiment uses 20 runs and eight process factors. The authors prepare a fresh salt sample for each run and clean the vessel. Oxidation and regeneration steps include gas collection. Table 7 treats each column as a run; the preceding text explicitly describes the arrangement as replicates and foldover pairs. The source reports p=2 pure-error degrees of freedom and f=1 fake-factor degree of freedom."),
         evidence("FOLD-2025", "Introduction, PDF p. 2; N-FOLD, foldover definition", "Foldover reverses coded factor signs to create additional treatment settings and address aliasing. Complementary settings can belong to a foldover pair without being the same complete treatment condition. The full Table 7 transcription is supplied below; no repeated columns are removed.")],
        "The 20 Table 7 executions are ten complete treatment conditions, each repeated twice, because the runs are arranged in foldover pairs.",
        [question("E008-Q01", "Which relation defines exact repetition of the complete treatment condition for replication accounting in this coded eight-factor experiment? Do not compare columns or count repetitions; code will apply the selected relation to every supplied row.",
                  [("complete_setting_equality", "Separate run executions have identical settings for all eight coded process factors."),
                   ("sign_complement", "Separate run executions have opposite signs for every coded process factor."),
                   ("main_factor_match", "Separate run executions match on a selected main factor even if the other seven settings differ."),
                   ("same_run_gas_samples", "Multiple gas collections come from one run, regardless of that run's complete factor settings.")],
                  "complete_setting_equality", "Replication of the full condition requires equal full setting vectors in separate preparations. A sign complement is a different treatment; the fresh-sample procedure establishes separate executions.",
                  "Chooses the scientifically relevant equality key. Column comparison, deduplication, replicate counts, and pure-error degrees of freedom are code work.")],
        "Foldover can provide variance information without making every pair an exact replicate. Conflating alias-control structure with replicated conditions changes the pure-error accounting.",
        dict(resolution_status="established_zero_model_call_control", judgment="Interpret full-treatment equality versus foldover complementarity.", code="Group the transcribed columns by all eight factor signs; count repeated settings and sum n_g-1 for pure-error degrees of freedom. Compare with the authors' p=2. The explicit design and source explanation support deterministic resolution; do not route a model call solely because an existing phrase parser lacks this case.",
             expected_outcome=dict(claim_assessment="inconsistent", run_count=20, distinct_complete_settings=18, repeated_column_groups=[[11,12],[13,14]], singleton_settings=16, pure_error_df=2),
             inference_boundary="The counted degrees of freedom concern exact coded repetitions. Their use as an error estimator still follows the source's modeling assumptions."),
        ["Physical factor names and actual level magnitudes are not supplied by this preprint. Review the intended coded-design scope before extending the claim to chemical equivalence.", "A full rendered table crop was checked against all 160 factor entries and 20 responses."],
        ["D02", "C01"], "D02 asks whether specimens share an execution; here separate executions are explicit. The issue is whether a design transformation preserves the full treatment and supplies pure-error replication, which requires an equality criterion followed by deterministic matrix accounting.",
        "Separate executions use either identical or complementary treatment vectors; a design pair need not be a replicate pair.",
        records=dict(factor_order=list(range(1,9)), column_index_definition="Left-to-right position in Table 7; not execution chronology.", runs=FOLD_RECORDS))

problem("E009", "Shared traceability across laboratory calibrations", ["MET-2016"],
        "DC-voltage calibration of the same Fluke 5700A multifunction calibrator at a common setting s, with the shared INRIM 10 V reference-standard contribution.",
        "Sections III-V's INRIM-Lab / Cal-Lab interlaboratory comparison. Restrict the dependence judgment to the DC-voltage traceability term in Equation 5; do not generalize it to all uncertainty components or electrical quantities.",
        [evidence("MET-2016", "Sections III.A-IV, PDF pp. 2-3; Figure 3", "The comparison uses verification without adjustment. The Cal-Lab traceability chain shares standards calibrated at INRIM with the INRIM-Lab chain, creating partial correlation. For DC voltage, Equation 5 identifies the INRIM calibration uncertainty of the 10 V standard in both chains."),
         evidence("MET-2016", "Section V, PDF p. 3, Equations 1-5; Conclusions, PDF p. 6", "Cal-Lab measures before and after INRIM-Lab. Its two values at the same setting s are averaged to reduce possible calibrator drift in the comparison. The difference uncertainty includes a covariance term: u(d)^2 = u(E_L)^2 + u(E_I)^2 - 2 r u(E_L)u(E_I). Equation 5 gives r = u_B(std_DCV)^2/[u(E_I)u(E_L)]. The authors report high instrument stability.")],
        "Different laboratory names make the two laboratory results independent realizations of the shared DC-voltage reference calibration, so this covariance contribution can be dropped.",
        [question("E009-Q01", "What relationship does the source establish between the laboratories' DC-voltage results with respect to the reference-calibration contribution in Equation 5?",
                  [("independent_reference", "The laboratories use independent realizations of this reference-calibration contribution."), ("shared_reference", "The laboratories share a reference-calibration contribution that induces covariance between their results."),
                   ("identical_measurement", "The laboratory labels refer to the same measurement result copied into both records.")],
                  "shared_reference", "The source locates the INRIM 10 V calibration contribution in both traceability chains and retains it in Equation 5. Separate laboratory executions do not eliminate that common contribution.", "Determines whether code retains the shared-reference covariance term; it does not evaluate that term numerically."),
         question("E009-Q02", "What role do the Cal-Lab measurements before and after the INRIM visit play in this comparison?",
                  [("bracketing_average", "They are repeated Cal-Lab measurements that bracket the INRIM visit and are averaged for the comparison."),
                   ("two_laboratories", "They represent two additional laboratories providing separate interlaboratory results."),
                   ("adjustment_contrast", "They are a before-and-after contrast of an intentional calibrator adjustment performed for this comparison.")],
                  "bracketing_average", "Section V averages the two Cal-Lab calibrations to reduce possible drift, while Section III.A specifies verification without adjustment.", "Selects the laboratory-level aggregation and prevents bracketing observations from becoming additional laboratories or a treatment contrast.")],
        "Independent execution and independent traceability are different requirements. A calibration comparison must retain the common reference contribution even when the laboratories performed separate work.",
        dict(resolution_status="established_for_source_equations_and_protocol", judgment="Locate the shared traceability ancestor and interpret the bracketing measurements.", code="Average the two Cal-Lab values at equal s, compare with INRIM, and retain covariance. Offline algebra checks that substitution of Equation 5 yields a subtraction of 2*u_B(std_DCV)^2; no new calibration data or uncertainty values are invented.",
             expected_outcome=dict(claim_assessment="inconsistent", compared_laboratory_results=2, calibration_visits=3, shared_covariance_term="2*u_B(std_DCV)^2", exact_effective_replication_count=None),
             inference_boundary="Shared calibration ancestry does not imply identical total errors or a known scalar effective sample size."),
        ["Review whether calibration-setting replication is within the desired S2 boundary; this candidate concerns treatment/execution provenance, not a new uncertainty-estimation task.", "Do not interpret the bracketing precaution as evidence that drift was observed."],
        ["D01", "C02"], "D01 shares a manufacturing parent and C02 remeasures one event. These are separate laboratories and executions whose uncertainty shares a calibration ancestor; bracketing visits have a stated aggregation role. Counting distinct execution IDs alone would miss the dependence.",
        "Distinct execution chains inherit a common calibration input; repeated visits bracket a comparison and do not create new laboratories.")

problem("E010", "Complementary allocation to paired mountain ranges", ["CLOUD-2018", "CLOUD-2014"],
        "Assignment of ground-based silver-iodide cloud seeding to Sierra Madre or Medicine Bow during a four-hour experimental unit (EU).",
        "The 118 quality-controlled EUs used in the WWMPP primary analysis. One EU includes the paired ranges. Target sites are HY (Sierra Madre) and GL (Medicine Bow); auxiliary gauges and possible cross-range contamination do not redefine the assigned treatment.",
        [evidence("CLOUD-2018", "Section 2 and Figure 1 explanation, pp. 2640-2642", "Within an EU, seeding is randomly assigned to one range and not the other. The authors explicitly say the Medicine Bow assignment plot would have the opposite shading from the Sierra Madre plot. Of 154 EUs, 27 are excluded by precipitation QC and nine by generator performance, leaving 118 for the primary analysis."),
         evidence("CLOUD-2018", "Section 2a and Figure 2, pp. 2642-2643", "The design has eight generators per range and multiple precipitation gauges; gauge QC is conducted without knowledge of seeding assignments."),
         evidence("CLOUD-2014", "Slides 16-18, 24 and 29", "The presentation shows the paired design, four-hour measurements, and a 118-case Medicine Bow assignment plot. Slide 24 reports ground-based ice-nucleus measurements indicating that silver iodide reached Medicine Bow in 21 Sierra Madre seeding cases. Slide 29 reports 18 modeled cases of enhanced precipitation in Medicine Bow during Sierra Madre seeding in winters 2009/10, 2011/12, and 2013/14. These are different diagnostics within the same trial reported in 2018.")],
        "The two range records in every retained EU represent two independently randomized seeding decisions, and the assigned-unseeded range is thereby confirmed to have no seeding exposure.",
        [question("E010-Q01", "How are the two range-level seeding assignments related within one retained EU?",
                  [("independent_assignments", "Each range is independently randomized, so both or neither can be assigned seeding within that EU."),
                   ("complementary_assignment", "One joint allocation selects the seeded range, and the other range receives the complementary unseeded assignment."),
                   ("both_seeded", "Both ranges are assigned seeding together as one treated pair."),
                   ("permanent_range", "One range is permanently assigned seeding and the other remains unseeded throughout the study.")],
                  "complementary_assignment", "The article explicitly describes mutually exclusive seeding and opposite assignment-plot shading for the two ranges.", "Defines the joint assignment event; code counts paired EUs separately from range records."),
         question("E010-Q02", "Does an assigned-unseeded label, by itself, establish zero physical exposure to seeding material in this study?",
                  [("zero_exposure_established", "Yes; assignment to the unseeded range establishes that it received no seeding material."),
                   ("assignment_only", "No; it establishes the planned allocation, while physical exposure requires additional evidence because cross-range contamination is discussed."),
                   ("exposure_confirmed_everywhere", "No; the label establishes that every unseeded range-period was physically exposed to seeding material.")],
                  "assignment_only", "The 2014 presentation reports measured and modeled cross-range effects. Assignment therefore does not certify zero exposure, and those diagnostics do not establish exposure in every unseeded range-period.",
                  "Keeps the assignment-based replicate accounting distinct from any exposure-based reclassification.")],
        "Two simultaneously observed targets do not imply two independent assignment draws. Exposure records could change an exposure-based analysis without changing the original paired allocation.",
        dict(resolution_status="established_for_reported_assignment_and_totals; per_EU_exposure_unassessed", judgment="Identify complementary assignment and distinguish allocation from realized exposure.", code="Retain 118 joint allocation events and two range-level records per retained event; verify 154-27-9. Do not reconstruct target assignments from differently labeled plots or classify per-EU exposure without its evidence.",
             expected_outcome=dict(claim_assessment="inconsistent_independent_assignment; zero_exposure_not_established_by_label", original_EUs=154, retained_EUs=118, joint_assignment_events=118, range_level_records=236, independent_range_draws_claim=False),
             inference_boundary="This does not certify temporal independence among all EUs or re-estimate the cloud-seeding effect."),
        ["The two source plots label opposite mountain ranges; plot colors cannot be merged without target identity.", "Calendar and wind-criterion discrepancies are retained in sources.json but do not conflict with the selected allocation judgment.", "Per-EU physical exposure is not adjudicated here."],
        ["C01", "C02"], "C01 nests units under group treatments; C02 separates measurements from events. Here one randomized decision sets complementary treatments on concurrent targets, and assignment labels differ from realized exposure when spillover is possible.",
        "A joint random choice gives complementary treatments to two targets; separate target records do not create separate draws, and allocation does not guarantee exposure isolation.",
        records=dict(initial_EUs=154, precipitation_QC_exclusions=27, generator_exclusions=9, reported_retained_EUs=118, ranges_per_EU=2))


def dump(name, obj):
    (B/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n")


def input_problem(p):
    keys = ["problem_id", "title", "source_ids", "target_treatment", "scope", "evidence", "scientific_claim", "claim_origin", "records"]
    out = {k:p[k] for k in keys}
    out["source_assets"] = [f for s in SOURCES if s['source_id'] in p['source_ids'] for f in s['local_files'] if f.endswith(('.pdf', '.png', '.html'))]
    out["questions"] = [{k:q[k] for k in ["question_id", "instruction", "options"]} for q in p["questions"]]
    return out


def render_problem(p):
    lines = [f"## {p['problem_id']} — {p['title']}", "", f"Status: {STATUS}. No user approval recorded.", "",
             "### Evidence and scope", "", f"**Target treatment:** {p['target_treatment']}", "", f"**Scope:** {p['scope']}", ""]
    for sid in p['source_ids']:
        s=next(s for s in SOURCES if s['source_id']==sid)
        lines += [f"**{sid}:** [{s['title']}]({s['url']}). {s['version']}. Access: {s['access_date']}.", ""]
    for e in p['evidence']:
        lines += [f"**Adaptation — {e['source_id']}, {e['location']}:** {e['text']}", ""]
    if p['records']:
        lines += ["**Supplied records / design constants:**", "", "```json", json.dumps(p['records'],indent=2), "```", ""]
    lines += [f"**Claim:** {p['scientific_claim']}", "", f"**Claim origin:** {p['claim_origin']}", "", "### Atomic questions and proposed references", ""]
    for q in p['questions']:
        lines += [f"#### {q['question_id']}", "", q['instruction'], ""]
        lines += [f"- `{k}`: {v}" for k,v in q['options'].items()]
        lines += ["", f"**Proposed reference:** `{q['reference_option']}`.", "", f"**Evidence rationale:** {q['evidence_rationale']}", "",
                  f"**Downstream role:** {q['downstream_role']}", "", f"**Question status:** {q['review_status']}; user-prepared; user approval: none.", ""]
    c=p['deterministic_work']
    lines += ["### Scientific decision and division of work", "", p['scientific_significance'], "", f"**Judgment:** {c['judgment']}", "", f"**Code:** {c['code']}", "",
              f"**Deterministic resolution:** `{c['resolution_status']}`.", "", "**Proposed downstream outcome:**", "", "```json", json.dumps(c['expected_outcome'],indent=2), "```", "",
              f"**Inference boundary:** {c['inference_boundary']}", "", "### Review notes and source limitations", ""]
    lines += [f"- {x}" for x in p['review_issues']]
    lines += ["", "**Source limitations retained for review:**", ""]
    for sid in p['source_ids']:
        s=next(s for s in SOURCES if s['source_id']==sid)
        lines += [f"- {sid}: {x}" for x in s['limitations']]
    return "\n".join(lines)+"\n"


def main():
    protected = ("inputs.json", "evaluation.json", "review_decisions.json",
                 "history/initial-presented/manifest.json")
    if any((B / name).exists() for name in protected):
        raise SystemExit("Refusing to overwrite an existing review package with initial preparation defaults.")
    dump("inputs.json", dict(schema_version="s2-expansion-inputs-v1", batch_id="batch-001", problems=[input_problem(p) for p in PROBLEMS]))
    evals=[]
    for p in PROBLEMS:
        evals.append({k:p[k] for k in ["problem_id", "review_status", "closest_existing_problem_ids", "substantive_difference", "structure_without_domain_nouns", "scientific_significance", "deterministic_work", "review_issues"]})
        evals[-1]["questions"]=[{k:q[k] for k in ["question_id", "reference_option", "evidence_rationale", "downstream_role", "review_status", "prepared_by", "approved_by_user", "approval_evidence"]} for q in p['questions']]
        evals[-1]["reference_provenance"] = dict(author="user", basis="Inspected source locations in inputs.json and sources.json; proposed interpretation, not independent human annotation", source_ids=p['source_ids'], claim_origin=p['claim_origin'])
    dump("evaluation.json", dict(schema_version="s2-expansion-evaluation-v1", batch_id="batch-001", problem_count=len(PROBLEMS), question_count=sum(len(p['questions']) for p in PROBLEMS), reference_status="proposed_only", problems=evals))
    for s in SOURCES:
        s['linked_problem_ids']=[p['problem_id'] for p in PROBLEMS if s['source_id'] in p['source_ids']]
    dump("sources.json", dict(batch_id="batch-001", access_date=ACCESS, source_records=SOURCES,
                              grouping_note="Source families group related documents and prior use, not statistically independent observations. N-STRIP shares the existing C01 source N; N-FOLD is the same handbook. CLOUD-2014 and CLOUD-2018 are one trial.",
                              source_family_count=len(set(s['source_family'] for s in SOURCES)), newly_introduced_source_families=9))
    blocks=[render_problem(p) for p in PROBLEMS]
    header = ["# S2 non-biological expansion — batch-001", "",
              "Ten proposed scientific problems with eighteen atomic Choice questions, pending review.", "",
              "The original collection contains six scientific problems and fifteen user-approved Choice definitions. Independent multi-reviewer annotation was not performed.", "",
              "The incorrect claims below are constructed for this benchmark. They are not claims attributed to the source authors. Source evidence is paraphrased and labeled as adaptation; no passage is presented as a verbatim quotation.", "",
              "Review status is recorded for each problem and question; accepted answers and source qualifications are stored in the evaluation records.", "",
              "checks.json records structural and arithmetic checks. Source annotations and references require separate review.", "",
              "| Problem | Scientific decision |", "|---|---|"]
    for p in PROBLEMS:
        header.append(f"| [{p['problem_id']}](#{p['problem_id'].lower()}--{p['title'].lower().replace(' ', '-').replace('?', '')}) | {p['title']} |")
    # Explicit anchors avoid renderer-specific heading slug conventions.
    for p in PROBLEMS:
        old=f"#{p['problem_id'].lower()}--{p['title'].lower().replace(' ', '-').replace('?', '')}"
        header=[x.replace(old,f"#{p['problem_id'].lower()}") for x in header]
    doc="\n".join(header)+"\n\n"+"\n".join(f"<a id=\"{p['problem_id'].lower()}\"></a>\n\n{block}" for p,block in zip(PROBLEMS,blocks))
    (B/"BATCH_REVIEW.md").write_text(doc)
    review=["# Review log — batch-001", "", f"Prepared at access date: {ACCESS}.", "",
            "Initial preparation at the recorded source access date; reference answers await review.", "",
            "## Case construction", "",
            "- Ten underlying problems define the batch. Multiple questions, compound claims, and source documents do not increase that count.",
            "- Evidence includes source explanations of unit definitions, kinetic change, minute bootstrap, forcing/code revisions, and spillover.",
            "- The foldover example includes the complete coded records.",
            "- The supplied evidence establishes mixed powder histories but incompletely identifies exact lineage.",
            "- The other option is absent from E004-Q02, E007-Q02, E009-Q01, and E010-Q02 because their substantive alternatives and evidence states cover the requested judgment. Other unit, mechanism, and aggregation questions retain it for a different established answer.",
            "", "## Per-problem and per-question status", "", "| Problem | Problem status | Question | Question status | Explicit user decision |", "|---|---|---|---|---|"]
    for p in PROBLEMS:
        for q in p['questions']:
            review.append(f"| {p['problem_id']} | {STATUS} | {q['question_id']} | {STATUS} | None |")
    review += ["", "## Concrete issues awaiting review", ""]
    for p in PROBLEMS:
        review += [f"- {p['problem_id']}: {x}" for x in p['review_issues']]
    review += ["", "## Source and option qualifications", "",
               "- Source limitations include powder PDF overprint, WWMPP target/date distinctions, and the NIST anneal-wording slip.",
               "- LENS2 forcing membership and bundled-change identification are separate questions.",
               "- The paired cloud-seeding case distinguishes treatment assignment from realized exposure.",
               "- Strict nesting and the same-partition alternative in E001-Q01 are disjoint.",
               "- E005 plot/parameter spacing remains unresolved for numerical inference about the executed experiment.",
               "- The 2014 WWMPP report supplies exposure evidence with distinct measured and modeled diagnostics.",
               "", "## User decisions", "", "No decisions recorded in this initial package.", ""]
    (B/"REVIEW_LOG.md").write_text("\n".join(review))


if __name__ == "__main__":
    main()
