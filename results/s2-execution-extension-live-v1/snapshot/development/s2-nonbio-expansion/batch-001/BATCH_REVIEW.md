# S2 non-biological expansion — batch-001

Ten scientific problems; eighteen atomic Choice questions. These are author-reviewed development data. The author explicitly accepted all ten problems and eighteen questions, E001-E010, in UR001-UR010. No questions remain pending. Review is complete within the recorded scopes; source limitations and inference boundaries remain in place.

The original collection contains six scientific problems and fifteen author-reviewed Choice definitions. Independent multi-reviewer annotation was not performed.

The incorrect claims below are constructed for this benchmark. They are not claims attributed to the source authors. Source evidence is paraphrased and labeled as adaptation; no passage is presented as a verbatim quotation.

Review decisions identify the accepted questions, scope, and content hashes in `review_decisions.json`.

checks.json records structural and arithmetic checks. Source annotations and references require separate review.

| Problem | Scientific decision |
|---|---|
| [E001](#e001) | Wafer regrouping across two processing stages |
| [E002](#e002) | Controller applications across hourly switches |
| [E003](#e003) | Catalyst recovery across reaction cycles |
| [E004](#e004) | Powder top-up and incomplete lineage coverage |
| [E005](#e005) | Outcome-dependent stress assignment in a staircase |
| [E006](#e006) | Two executions within one paired-fixed realization |
| [E007](#e007) | Ensemble membership after a forcing-protocol revision |
| [E008](#e008) | Exact treatment repetition within a foldover design |
| [E009](#e009) | Shared traceability across laboratory calibrations |
| [E010](#e010) | Complementary allocation to paired mountain ranges |

<a id="e001"></a>

## E001 — Wafer regrouping across two processing stages

Status: author_reviewed. Explicit author review: UR001, covering both questions and the methodological-example scope.

### Evidence and scope

**Target treatment:** Joint implant-factor (A, B, C) and anneal-factor (D, E, F) settings in NIST Figure 5.16.

**Scope:** The single illustrated block: implant combinations 1-8 and anneal combinations 1-8. Each figure cell is one wafer. Combination numbers are treatment codes, not persistent wafer serial numbers.

**N-STRIP:** [NIST/SEMATECH e-Handbook: 5.5.5. How can I account for nested variation (restricted randomization)?](https://www.itl.nist.gov/div898/handbook/pri/section5/pri55.htm). Undated live handbook page, archived at access. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — N-STRIP, Strip-Plot Designs; Figure 5.16 and execution paragraphs:** Each implant setting processes eight wafers together. After all implant batches, every anneal batch receives one wafer from each implant batch and is annealed at its assigned D/E/F setting. Thus annealing regroups the wafers. The first implant setting executed is 3 and the first anneal setting executed is 5; treatment codes are not execution-order indices.

**Adaptation — N-STRIP, Three sizes of experimental units; Replication:** The handbook assigns implant effects to implant batches, anneal effects to anneal batches, and cross-stage interactions to individual wafers. The figure is one block or replicate. Without replicated blocks, it describes using A*B*C and D*E*F as error terms only under models excluding those three-factor interactions; each then supplies one degree of freedom.

**Supplied records / design constants:**

```json
{
  "implant_setting_codes": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "anneal_setting_codes": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "wafers_per_intersection": 1,
  "illustrated_blocks": 1
}
```

**Claim:** Within the illustrated block, each complete implant-by-anneal setting combination has eight separately processed wafer replicates.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E001-Q01

For this block, how are the wafer memberships of implant batches related to those of anneal batches? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `same_partition`: Each implant batch remains intact as one corresponding anneal batch.
- `anneal_nested`: Each anneal batch is wholly contained within one implant batch, and at least one implant batch supplies multiple anneal batches.
- `implant_nested`: Each implant batch is wholly contained within one anneal batch, and at least one anneal batch contains multiple implant batches.
- `crossed_regrouping`: Each anneal batch combines wafers from multiple implant batches, and each implant batch supplies multiple anneal batches.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `crossed_regrouping`.

**Evidence rationale:** The source explicitly sends one wafer from each implant batch to each anneal setting; neither stage's batch partition contains the other.

**Downstream role:** Selects a two-stage membership representation before code groups complete treatment combinations.

**Question status:** author_reviewed; reviewed by: author; decision: UR001.

#### E001-Q02

Which experimental unit does the source assign to interaction effects involving both an implant factor and an anneal factor in this block? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `implant_batch`: The group of wafers processed together in one implant operation.
- `anneal_batch`: The group of wafers processed together in one anneal operation.
- `wafer`: An individual wafer receiving one implant setting and one anneal setting.
- `whole_block`: The complete block containing all implant and anneal setting combinations.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `wafer`.

**Evidence rationale:** The handbook explicitly identifies the single wafer as the unit for cross-stage interaction effects.

**Downstream role:** Determines the relevant level for the joint-treatment replication claim; it does not count wafers or blocks.

**Question status:** author_reviewed; reviewed by: author; decision: UR001.

### Scientific decision and division of work

A one-parent batch identifier loses one treatment stage. The correct grouping prevents eight different joint settings from being treated as eight repeats of one joint setting.

**Judgment:** Interpret the crossed membership and the effect-specific experimental unit.

**Code:** Enumerate the source-described Cartesian grid, group wafers by both setting codes, and compare per-cell replication with the claim. Keep full-block replication separate. Source explanations make a zero-model-call route valid.

**Deterministic resolution:** `established_for_supplied_structured_evidence`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "implant_batches": 8,
  "anneal_batches": 8,
  "wafer_records": 64,
  "full_setting_combinations": 64,
  "wafers_per_full_setting": 1,
  "complete_blocks": 1,
  "description": "64 implant–anneal combinations, each corresponding to one wafer observation."
}
```

**Inference boundary:** One wafer per cell is not a claim of 64 mutually independent errors or replicated whole blocks.

### Review notes and source limitations

**Resolved in UR001:** The author accepted the methodological example, both question references, and the scoped observation count. D/E/F terminology is normalized to annealed. No unresolved E001 review issue remains.

**Source limitations retained for review:**

- N-STRIP: Authoritative methodological illustration, not a reported empirical wafer dataset.
- N-STRIP: The D/E/F stage is annealing. An operation-label typo in the source is normalized to 'annealed' in the benchmark adaptation, consistently with the factor definitions and diagram. Original source files retain their original wording for provenance.

<a id="e002"></a>

## E002 — Controller applications across hourly switches

Status: author_reviewed. Explicit author review: UR002, covering both questions and the benchmark scope.

### Evidence and scope

**Target treatment:** Baseline versus wake-steering controller mode on upstream turbine SMV6, with SMV5 downstream.

**Scope:** The reported SMV experiment's hourly mode toggles and one-minute analysis records; no new turbine deployment or complete campaign count is inferred.

**WIND-2021:** [Results from a wake-steering experiment at a commercial wind plant: investigating the wind speed dependence of wake-steering performance](https://wes.copernicus.org/articles/6/1427/2021/). Final article, 12 November 2021, Wind Energy Science 6, 1427-1453. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — WIND-2021, Sections 2.1-2.2 and Figure 5, PDF pp. 4-6:** Measurements are downsampled to one-minute records. Figure 5 switches SMV6 between baseline and wake-steering control hourly. The offset within controlled periods follows the wind-dependent controller schedule; hourly mode assignment is different from instantaneous yaw offset.

**Adaptation — WIND-2021, Sections 4.1-4.3, PDF pp. 9-10:** After operational and power-curve filtering, the first ten minutes after each mode switch are removed for yaw-controller transients. Further power and lidar-availability filters apply to yaw analyses. The authors bootstrap one-minute observations at least 2,000 times, by wind-direction bin where applicable, resampling baseline and controlled observations separately.

**Claim:** Each retained one-minute observation represents a separately assigned controller-mode application.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E002-Q01

What defines the reported allocation of baseline versus wake-steering mode on SMV6? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `fixed_turbine`: Each turbine receives a fixed controller mode for the whole experiment.
- `hourly_switch`: Controller mode alternates across hourly periods on the same turbine.
- `minute_randomization`: Each one-minute measurement receives a new independently randomized controller mode.
- `analysis_bin`: Post hoc wind-direction bins define separate controller-mode assignments.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `hourly_switch`.

**Evidence rationale:** Figure 5 explicitly gives an hourly toggle on SMV6; one-minute sampling and wind bins do not reassign the controller mode.

**Downstream role:** Defines the controller-mode application boundary before timestamps are grouped; this does not establish independent applications.

**Question status:** author_reviewed; reviewed by: author; decision: UR002.

#### E002-Q02

What is the role of the first ten minutes after a controller-mode switch in the reported analysis? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `transition_exclusion`: They are a transition segment of the switched application, excluded to allow for controller transients.
- `separate_treatment`: They are a separately assigned third controller treatment.
- `baseline_relabel`: They are relabeled as baseline observations regardless of the switched mode.
- `new_replication`: They are independent repeat applications retained to estimate controller replication.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `transition_exclusion`.

**Evidence rationale:** Section 4.1 removes this interval because of yaw-controller transients; it does not create or relabel an assignment.

**Downstream role:** Tells code how to retain application identity while excluding transition observations.

**Question status:** author_reviewed; reviewed by: author; decision: UR002.

### Scientific decision and division of work

Replicating time samples does not replicate controller assignments. The transition rule also prevents a new mode's early response from being mistaken for a separately applied treatment.

**Judgment:** Interpret the switch boundary and transition segment.

**Code:** With timestamped records, attach observations to hourly mode periods, apply the source filters, and count retained applications separately from rows. No actual log is supplied, so no campaign total is generated. The present claim is resolved by the explicit protocol.

**Deterministic resolution:** `established_for_scoped_claim; full_campaign_count_unassessed`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "actual_eligible_application_count": null,
  "minute_rows_are_new_assignments": false
}
```

**Inference boundary:** An application boundary marks a controller-mode period. Hourly switching alone establishes neither randomization nor independence between applications.

### Review notes and source limitations

**Resolved in UR002:** The author accepted both questions and the benchmark scope. Application boundaries do not establish independent applications. The source minute-bootstrap description remains available; no uncertainty reanalysis is performed.

**Source limitations retained for review:**

- WIND-2021: Hourly toggling identifies controller-mode application boundaries; it does not establish randomization or independence between applications.
- WIND-2021: The paper reports resampling one-minute observations. That analysis description is retained; the present question concerns assignment, not a verdict on all confidence intervals.
- WIND-2021: No timestamped campaign log is included in this package; no total number of eligible hourly applications is inferred.

<a id="e003"></a>

## E003 — Catalyst recovery across reaction cycles

Status: author_reviewed. Explicit author review: UR003, covering E003-Q01 and the single-reuse-history scope.

### Evidence and scope

**Target treatment:** Cu-AmP-CPG catalyst 1 used for benzyl azide 2a plus propargyl alcohol 3a to produce 4a.

**Scope:** The eight consecutive recycling cycles in Figure 2; Figure 3's C1-C3 kinetic curves provide context. The different-substrate series in Table 3 is excluded.

**CAT-2020:** [Copper nanoparticles on controlled pore glass (CPG) as highly efficient heterogeneous catalysts for 'click reactions'](https://www.nature.com/articles/s41598-020-77629-3). Scientific Reports 10, 20547, 25 November 2020. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — CAT-2020, Recycling procedure, PDF pp. 3 and 6; Figure 2, PDF p. 5:** The recycling reaction uses 2a (0.25 mmol), 3a (0.38 mmol), catalyst (10 mg, 5 mol%), and t-BuOH/water (1:1) at 70 degrees C for two hours. Solids are separated, washed, and the recovered catalyst is used in the next cycle. Figure 2 reports eight consecutive cycles with high endpoint conversion.

**Adaptation — CAT-2020, Results, PDF p. 3; Figure 3, PDF p. 5:** The source reports that reaction rates begin to decrease after two cycles, despite completion before the two-hour endpoint. Figure 3 distinguishes C1, C2, and C3. Catalyst synthesis is described separately from recovery and reuse.

**Claim:** The eight Figure 2 cycles are eight independent preparations of fresh catalyst 1 tested once each.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic question and accepted reference

#### E003-Q01

What material relationship connects the catalyst used in consecutive Figure 2 reaction cycles? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `fresh_preparation`: Each cycle uses catalyst from a newly performed synthesis, with no recovered catalyst carried forward.
- `recovered_carryover`: Catalyst recovered from the preceding reaction is carried into the next reaction cycle.
- `fresh_aliquots`: Each cycle uses a previously unused aliquot split from one preparation before any reaction.
- `one_reaction_samples`: The cycle labels identify repeated samples of one uninterrupted reaction mixture.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `recovered_carryover`.

**Evidence rationale:** The recycling method recovers, washes, and reuses the solid in the next experimental cycle. These are new reaction operations with inherited catalyst history.

**Downstream role:** Distinguishes reuse-performance evidence from fresh-preparation replication before code labels the claim.

**Question status:** author_reviewed; reviewed by: author; decision: UR003.

### Scientific decision and division of work

Cycle results address retained activity of a reused catalyst. They cannot estimate variation across eight independent catalyst syntheses, and equal endpoint conversions do not remove the observed kinetic history.

**Judgment:** Identify material carryover across separately initiated reactions.

**Code:** Represent the eight stated cycles as a chronological reuse chain, retain reaction-operation and catalyst-preparation levels separately, and reject the fresh-preparation interpretation. This explicit method is code-resolvable; no model call is required.

**Deterministic resolution:** `established_for_supplied_protocol`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "reported_reaction_cycles": 8,
  "documented_recycling_series": 1,
  "independent_synthesis_count_established_by_cycles": null
}
```

**Inference boundary:** Recovered carryover denotes procedural reuse; it establishes neither complete material conservation nor identical catalyst composition across cycles. One described reuse series is not proof that the entire study performed only one synthesis or one series.

### Review notes and source limitations

**Resolved in UR003:** The author accepted E003-Q01 and the single-reuse-history scope. The reference remains `recovered_carryover`, with its procedural meaning stated in the inference boundary. No unresolved E003 review issue remains.

**Source limitations retained for review:**

- CAT-2020: Figure 2 endpoint conversion does not establish unchanged kinetics: Figure 3 and the text report slowing after two cycles.
- CAT-2020: The recycling procedure uses two hours; the three-hour general procedure is a different scope.
- CAT-2020: These eight cycles document one catalyst reuse history. They do not establish independent synthesis-series replication, complete material conservation, or identical catalyst composition across cycles.

<a id="e004"></a>

## E004 — Powder top-up and incomplete lineage coverage

Status: author_reviewed. Explicit author review: UR004, covering both questions and the downstream representation as proposed.

### Evidence and scope

**Target treatment:** Recycling history of Ti-6Al-4V feedstock used in the LPBF top-up process.

**Scope:** Section 2.3's build-8-and-later top-up regime through build 10. The question concerns feedstock provenance, not the number of tensile specimens or scan tracks.

**POW-2023:** [Effective Ti-6Al-4V Powder Recycling in LPBF Additive Manufacturing Considering Powder History](https://researchonline.jcu.edu.au/86205/7/86205.pdf). Repository copy with final Sustainability 2023, 15, 15582 headers; published 2 November 2023. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — POW-2023, Section 2.3 and Figures 1-2, PDF pp. 4-6:** The process refreshes recovered powder with added powder. From build 8, the authors add previously reused powder with different extents of recycling. The R index aggregates powder consumption and input history; its assumptions relate degradation to material built and exclude interactions. The paper explains why a simple reuse-cycle number is inadequate.

**Adaptation — POW-2023, Section 2.3 final paragraphs, PDF p. 6:** Characterized R values 0.00, 0.04, 0.15, 0.24, and 0.40 refer to virgin powder and the starts of builds 1, 3, 6, and 10, respectively, with top-up as necessary. R can increase during a build as powder is converted into solid material. The build-8 paragraph describes the addition of previously reused powder of various recycling extents.

**Claim:** Build 8 feedstock can be represented as one parent lot whose particles all have the same prior recycling history; its exact parent-lot assignments can be recovered from the reported bulk history alone.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E004-Q01

Which membership pattern is established for the prior recycling histories of powder entering the build-8-and-later top-up regime? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `one_common_history`: All entering powder shares one identical prior recycling history.
- `mixed_histories`: Entering powder combines portions with different prior recycling histories.
- `virgin_replacement`: Each build replaces all recovered powder with unused virgin powder.
- `separate_unmixed`: Different-history portions are processed separately without mixing in a build's feedstock.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `mixed_histories`.

**Evidence rationale:** The build-8 paragraph explicitly adds previously reused powder with different extents of recycling. This is a known mixture, not ambiguous membership.

**Downstream role:** Selects a multiple-parent history representation; it supplies no exact parent count.

**Question status:** author_reviewed; reviewed by: author; decision: UR004.

#### E004-Q02

How completely does the supplied evidence identify every input portion's original lot, mixture fraction, and prior-build history for build 8? Select exactly one option. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope. Use partial_identification when some required provenance is established but the requested complete assignment is unavailable; this takes precedence over not_stated. A known mixture is not itself a conflict.

- `complete_assignment`: All requested lot identities, mixture fractions, and prior-build histories are established for every input portion.
- `partial_identification`: Some provenance is established, including the presence of different reuse histories, but the complete requested input-portion assignment is unavailable.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `partial_identification`.

**Evidence rationale:** The protocol establishes the mixed-history origin, but supplies no complete lot/fraction/exposure mapping. R does not uniquely invert to that mapping.

**Downstream role:** Prevents code from turning a broad mixture category into an exact count or allocation of source lots.

**Question status:** author_reviewed; reviewed by: author; decision: UR004.

### Scientific decision and division of work

A bulk recycling index can support a process-level comparison while failing to identify particle or lot-level replication. Lineage merges require both membership structure and coverage checks.

**Judgment:** Separate a known mixed-origin structure from the completeness of its assignments.

**Code:** Retain a multiple-parent relation with unresolved lot assignments. Do not create one parent per history label, invert R into reuse counts, or replace unknown counts with zero.

**Deterministic resolution:** `established_for_mixture_and_coverage; exact_lineage_not_estimable_from_supplied_evidence`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent_single_history; insufficient_exact_assignments",
  "exact_parent_lot_count": null,
  "complete_assignment_available": false
}
```

**Inference boundary:** Missing supplied assignments do not establish missing experimental replication or missing records in the actual study.

### Review notes and source limitations

**Resolved in UR004:** The author accepted both questions and the downstream representation as proposed. History streams remain distinct from original powder lots, and the bulk R index does not determine exact genealogy. The PDF overprint remains a documented source limitation.

**Source limitations retained for review:**

- POW-2023: The repository PDF visibly overprints earlier text on portions of pp. 5-6, including older peer-review headers. The build-8 statement and final sampling paragraph remain readable; the overprint is saved, not silently repaired.
- POW-2023: The bulk index assumes degradation related to material built and no interactions. It is not a particle-level lineage ledger.
- POW-2023: Exact input-lot IDs, fractions, and per-particle exposure histories are not established by the supplied methods. This is an evidence-coverage statement, not a claim that the investigators never kept such records.
- POW-2023: Publisher HTML returned HTTP 403 during acquisition; the repository copy was inspected.

<a id="e005"></a>

## E005 — Outcome-dependent stress assignment in a staircase

Status: author_reviewed. Explicit author review: UR005; both Choice answers reaffirmed in UR005-F01 independently of the unresolved numerical stress-step discrepancy.

### Evidence and scope

**Target treatment:** Applied fatigue stress in the regular staircase test of 304L stainless-steel foil specimens.

**Scope:** Table 2's staircase/up-down protocol as implemented in Section 4 and Figure 11(a). Figure 11(b-d) are other protocols, not additional observations of the selected allocation rule.

**FAT-2022:** [Bayesian Optimised Collection Strategies for Fatigue Strength Testing](https://arxiv.org/pdf/2107.02685v3). arXiv:2107.02685v3, 21 September 2022; 27-page preprint. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — FAT-2022, Table 2, PDF p. 3:** In the staircase protocol, the first specimen receives the starting stress. The next specimen receives a stress step down after failure or a step up after runout of the preceding specimen. Each specimen contributes one test. In the separately described step protocol, the same specimen is retested at increasing stress after runout.

**Adaptation — FAT-2022, Section 4 and Table 3, PDF p. 17; Figure 11(a), PDF p. 18:** The experimental material is 304L foil. Specimens were extracted randomly across the foil and assigned to protocols in randomized order to reduce time effects. Table 3 states a 325 MPa start and 30 MPa steps. Figure 11(a) plots the regular staircase sequence; the caption also states 30 MPa increments. The rendered table and figure accompany this evidence.

**Supplied records / design constants:**

```json
{
  "starting_stress_MPa": 325,
  "step_MPa": 30
}
```

**Claim:** Because specimen selection and protocol order were randomized, the stresses in the regular staircase were independently randomized across specimens.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E005-Q01

What determines the next specimen's applied stress in the selected regular staircase protocol? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `independent_randomization`: A fresh random draw selects stress independently of preceding outcomes.
- `response_adaptive`: The preceding specimen's failure or runout determines an upward or downward stress step.
- `fixed_level`: The initial stress is retained unchanged for every specimen.
- `preordered_schedule`: A preassigned stress sequence is followed regardless of preceding outcomes.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `response_adaptive`.

**Evidence rationale:** Table 2 specifies the outcome-dependent update. Randomization of specimen extraction and protocol order is a different operation.

**Downstream role:** Identifies dependence in treatment allocation before code reconstructs a stress sequence.

**Question status:** author_reviewed; reviewed by: author; decision: UR005.

#### E005-Q02

When this regular staircase advances after an outcome, which physical specimen receives the next stress setting? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `new_specimen`: A new specimen receives the next setting, and the preceding specimen's single test is complete.
- `same_specimen`: The same specimen receives the next setting as another step in its loading history.
- `whole_foil`: The complete foil receives the next setting collectively before specimens are extracted.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `new_specimen`.

**Evidence rationale:** The staircase row says next specimen and classifies the protocol as a single test per specimen. Retesting the same specimen belongs to the separate step protocol.

**Downstream role:** Separates adaptive dependence between assignments from repeated exposure of one specimen.

**Question status:** author_reviewed; reviewed by: author; decision: UR005.

### Scientific decision and division of work

New physical specimens do not make treatment allocation independent of prior outcomes. This distinction changes how repeated stress-level observations enter a fatigue-strength analysis.

**Judgment:** Identify the allocation dependency and the specimen boundary.

**Code:** Apply the documented up/down rule to outcome records if available; group equal stresses by code. The 30 MPa increment and grouping operations are computed in code. The offline check verifies the rule's arithmetic at the documented starting value only, not a reconstructed dataset.

**Deterministic resolution:** `established_for_explicit_protocol; observed_sequence_reconstruction_unassessed`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "next_stress_after_initial_failure_MPa": 295,
  "next_stress_after_initial_runout_MPa": 355,
  "observed_replicates_at_any_fixed_stress": null
}
```

**Inference boundary:** This is about conditional allocation, not proof that physical specimen failures have a particular correlation.

### Review notes and source limitations

**Resolved in UR005:** The author accepted both questions and the downstream outcome without content changes. The 295 MPa and 355 MPa values are protocol-derived; no observed sequence or fixed-stress replicate count is reconstructed from Figure 11(a). Randomized specimen extraction and protocol order do not imply independent stress allocation, and allocation dependence does not establish specimen failure correlation.

**Retained numerical limitation:**

- UR005-F01 confirms E005-Q01 as `response_adaptive` and E005-Q02 as `new_specimen`. Both answers concern the staircase allocation mechanism and do not depend on resolving the numerical stress-step discrepancy.
- The paper reports a 30 MPa stress step in Table 3 (PDF p. 17; printed p. 17) and the Figure 11 caption (PDF p. 18; printed p. 18). The [author-released Figure 11 plotting file](https://github.com/cmmagazz/BayesOptFatigue/tree/7dae4bc61c8929be20dcf818e19c509b5f019cd5/examplefigures/Figure%2011) contains a saved staircase stress sequence with 16.25 MPa adjacent spacing.
- No public correction or experimental log was found to determine whether these represent the same quantity. Numerical next-stress inference for the executed experiment remains unresolved. The retained 295/355 MPa values are conditional arithmetic using the paper's reported 30 MPa parameter; the Choice answers, rationales, and downstream evaluation remain unchanged.

**Source limitations retained for review:**

- FAT-2022: The regular staircase in Figure 11(a) is the selected protocol. The step tests in Figure 11(c,d) repeatedly load the same specimen and must not be merged into this scope.
- FAT-2022: Random specimen extraction and randomized protocol order do not imply randomized stress selection.
- FAT-2022: No digitized stress-by-specimen dataset is asserted; no exact count at a chosen stress is estimated from plot pixels.
- FAT-2022: The author-released Figure 11 plotting file saves 16.25 MPa adjacent stress spacing, whereas Table 3 and the figure caption report 30 MPa. The numerical discrepancy remains unresolved; the next-specimen and outcome-dependent allocation descriptions remain explicit and approved in UR005-F01.

<a id="e006"></a>

## E006 — Two executions within one paired-fixed realization

Status: author_reviewed. Explicit author review: UR006, covering both questions and the downstream outcome as proposed.

### Evidence and scope

**Target treatment:** Paired-fixed initialization for the N1000 cosmological N-body simulation set.

**Scope:** Only the 100 paired-fixed realizations in Table 1's N1000 row; exclude its 100 standard realizations and all other simulation sets. One paired-fixed realization contains two phase-related executions.

**COS-2018:** [Statistical properties of paired fixed fields](https://arxiv.org/pdf/1806.01871v1). arXiv:1806.01871v1, submitted 5 June 2018; PDF draft dated 7 June 2018. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — COS-2018, Section 2, PDF pp. 2-3; Table 1, PDF p. 4:** The two fixed fields of a pair use the same fixed Fourier amplitudes, with phases shifted by pi between them. Table 1 lists 100 N1000 paired-fixed realizations and states that each corresponds to two simulations. The simulations are separate executions, not two output snapshots of one execution.

**Adaptation — COS-2018, Section 3.2, PDF p. 5, Equation 10 and cross-correlation discussion:** The authors first average the two simulations' values for a paired-fixed realization, then calculate statistics across realizations. They explicitly analyze the cross-correlation within pairs. Phase flipping does not imply that every evolved observable has perfect negative correlation.

**Supplied records / design constants:**

```json
{
  "paired_realizations": 100,
  "executions_per_paired_realization": 2
}
```

**Claim:** The N1000 paired-fixed subset supplies 200 independently drawn initial phase fields because it contains 200 separately executed simulations.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E006-Q01

How are the initial phase fields of the two simulations within one paired-fixed realization related? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `independent_draws`: Both phase fields are independently drawn from the specified phase distribution.
- `phase_reversed`: One phase field is obtained from the other by a pi phase shift, with the same fixed amplitudes.
- `identical_field`: Both simulations use the identical phase field without phase reversal.
- `output_resampling`: The pair is produced by resampling outputs from one completed simulation.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `phase_reversed`.

**Evidence rationale:** The source defines the pair through a pi phase shift; a second execution is not a second independent phase draw.

**Downstream role:** Identifies the initial-condition coupling that determines the realization boundary.

**Question status:** author_reviewed; reviewed by: author; decision: UR006.

#### E006-Q02

In the source's paired-fixed statistical construction, which quantity contributes one value before statistics are taken across realizations? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `individual_execution`: The output of each individual execution, entered separately as an independent realization.
- `pair_average`: The average of the two corresponding outputs within a paired-fixed realization.
- `pair_difference`: The difference between the two corresponding outputs within a paired-fixed realization.
- `all_runs_average`: One average across every N1000 execution, without distinct realization values.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `pair_average`.

**Evidence rationale:** Equation 10 averages the two members within a pair before ensemble statistics are formed.

**Downstream role:** Selects the aggregation object; code performs averaging and execution-versus-realization counting.

**Question status:** author_reviewed; reviewed by: author; decision: UR006.

### Scientific decision and division of work

Execution counts measure computational work. Replication for the reported paired estimator is organized by the deliberately coupled realization, so those counts cannot be interchanged.

**Judgment:** Interpret the phase coupling and reported realization statistic.

**Code:** Multiply the stated realization count by two for execution accounting; retain 100 pair-level values. Do not replace pair-level variation with the variance of 200 independent phase draws.

**Deterministic resolution:** `established_for_supplied_table_and_formalism`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "paired_realizations": 100,
  "paired_execution_count": 200,
  "values_entering_pair_ensemble": 100
}
```

**Inference boundary:** Neither this bookkeeping nor phase reversal establishes an effective sample size for every observable.

### Review notes and source limitations

**Resolved in UR006:** The author accepted both questions and the downstream outcome without content changes. The 200 executions do not constitute 200 independent initial-condition samples. Initial Fourier-field sign reversal does not imply perfect anticorrelation of evolved observables, and the source aggregation unit does not establish an effective sample size for every observable.

**Source limitations retained for review:**

- COS-2018: Phase reversal is a deterministic initial-field relationship; it does not mean every final observable is perfectly anticorrelated.
- COS-2018: The N1000 paired-fixed subset is separate from the 100 standard realizations and the N20/H200/H20 sets.
- COS-2018: The published article DOI 10.3847/1538-4357/aae52b is a related version, not a second source or an audited replacement for v1.

<a id="e007"></a>

## E007 — Ensemble membership after a forcing-protocol revision

Status: author_reviewed. Author review is recorded in UR007. The Q02 rationale distinguishes additional implementation changes from their reported impacts.

### Evidence and scope

**Target treatment:** Original CMIP6 biomass-burning forcing versus the revised SMBB implementation in CESM2-LENS2.

**Scope:** All 100 documented LENS2 members, with the forcing change during 1990-2020. Member groups and initialization dates follow the official page; no independent climate-state count is inferred from output fields.

**LENS2-DOC:** [CESM2 Large Ensemble Community Project (LENS2)](https://www.cesm.ucar.edu/community-projects/lens2). Undated official project documentation, live snapshot at access. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — LENS2-DOC, Initialization groups; Modifications incorporated in the second half:** LENS2 has two 50-member halves: original biomass-burning forcing and an 11-year-running-mean version, SMBB, affecting 1990-2020. At each of four macro-initialization dates (1231, 1251, 1281, 1301), the first ten micro-perturbation members use original forcing and the second ten use SMBB. Ten additional even-decade initializations use original forcing; ten odd-decade initializations use SMBB.

**Adaptation — LENS2-DOC, Remaining modification paragraphs:** The SMBB implementation also corrects emission-dataset issues and changes the timing of a crop-harvest carbon-flux term. The project reports no significant solution changes from the former corrections and no climate-changing impacts from the latter. Additional output fields also differ.

**Supplied records / design constants:**

```json
{
  "macro_start_dates": [
    1231,
    1251,
    1281,
    1301
  ],
  "original_micro_members_per_date": 10,
  "smbb_micro_members_per_date": 10,
  "original_extra_start_years": [
    1001,
    1021,
    1041,
    1061,
    1081,
    1101,
    1121,
    1141,
    1161,
    1181
  ],
  "smbb_extra_start_years": [
    1011,
    1031,
    1051,
    1071,
    1091,
    1111,
    1131,
    1151,
    1171,
    1191
  ]
}
```

**Claim:** All 100 LENS2 members replicate the original biomass-burning forcing implementation; differences between the two documented halves isolate the effect of smoothing that forcing.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E007-Q01

How should the documented members be classified with respect to the original versus SMBB biomass-burning forcing protocol? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `all_original`: Every member uses the original biomass-burning forcing protocol.
- `all_smbb`: Every member uses the SMBB biomass-burning forcing protocol.
- `two_protocol_groups`: The collection contains members using each of the two documented forcing protocols.
- `within_run_replicates`: Each member contains separate original and SMBB runs as internal replicate executions.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `two_protocol_groups`.

**Evidence rationale:** The official page explicitly divides the collection into original and SMBB halves with a mapping across initialization groups.

**Downstream role:** Selects treatment-protocol membership before code totals matching members.

**Question status:** author_reviewed; reviewed by: author; decision: UR007.

#### E007-Q02

Does the documented difference between these halves isolate biomass-burning smoothing as the only implementation change? Select exactly one option. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `smoothing_only`: Yes; the two halves differ only in the biomass-burning smoothing operation.
- `bundled_changes`: No; the SMBB half also incorporates other documented implementation changes.
- `initialization_only`: No forcing or code difference is present; only the initial conditions differ.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `bundled_changes`.

**Evidence rationale:** The same documentation lists emission and carbon-flux corrections in the SMBB half. The project reports no significant model-solution changes from the emission corrections and no climate-changing impacts from the carbon-flux modification. These impact evaluations do not establish that smoothing was the only implementation change.

**Downstream role:** Blocks a smoothing-only interpretation of a group comparison even after code has correctly assigned members.

**Question status:** author_reviewed; reviewed by: author; decision: UR007.

### Scientific decision and division of work

Nominal project membership does not establish identical treatment implementation. Correct subgroup counts still leave an identification problem when changes were introduced together.

**Judgment:** Interpret protocol identity and the scope of the implementation change.

**Code:** Use the documented group mapping to count original and SMBB members, then compose separate membership and single-change-identification outcomes. Do not infer treatment effects or statistical independence.

**Deterministic resolution:** `established_for_documented_group_mapping`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent_in_both_clauses",
  "original_members": 50,
  "smbb_members": 50,
  "total_members": 100,
  "smoothing_only_contrast": false
}
```

**Inference boundary:** The documentation reports evaluations of the corrections; this problem does not estimate their effects.

### Review notes and source limitations

- UR007: Both questions were accepted as one scientific problem, with the references and downstream schema unchanged.
- UR007: The Q02 rationale now distinguishes other implementation changes from their reported impact evaluations. The model-facing evidence retains those evaluations.
- UR007: The official mapping gives 50 original and 50 SMBB members. Initialization dates are not forcing treatments; small or undetected impacts do not establish a smoothing-only causal contrast.

**Source limitations retained for review:**

- LENS2-DOC: The SMBB half also contains emission and carbon-flux code corrections; a between-half contrast does not isolate smoothing alone.
- LENS2-DOC: The project reports no significant model-solution or climate-changing impacts from the respective corrections. That report does not establish identical implementations.
- LENS2-DOC: The local snapshot is authoritative for this problem; a future website update could change the documentation.

<a id="e008"></a>

## E008 — Exact treatment repetition within a foldover design

Status: author_reviewed. Author review is recorded in UR008. The source annotation identifies the factor levels in Table 1 and the unresolved temperature discrepancy.

### Evidence and scope

**Target treatment:** The complete eight-factor coded treatment setting in the ethylene experiment.

**Scope:** All 20 run columns of Table 7, factors 1-8 and response y. Column numbers in the transcription are left-to-right table indices assigned for this package, not claimed original run IDs or chronological order.

**FOLD-2025:** [Powerful Foldover Designs](https://arxiv.org/pdf/2507.14648v1). arXiv:2507.14648v1, submitted 19 July 2025; PDF cover dated 22 July 2025. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**N-FOLD:** [NIST/SEMATECH e-Handbook: 5.3.3.8.1. Mirror-image foldover designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3381.htm). Undated live handbook page, archived at access. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — FOLD-2025, Section 6, PDF pp. 22-23; Table 7, PDF p. 23:** The ethylene experiment uses 20 runs and eight process factors. The authors prepare a fresh salt sample for each run and clean the vessel. Oxidation and regeneration steps include gas collection. Table 7 treats each column as a run; the preceding text explicitly describes the arrangement as replicates and foldover pairs. The source reports p=2 pure-error degrees of freedom and f=1 fake-factor degree of freedom.

**Adaptation — FOLD-2025, Introduction, PDF p. 2; N-FOLD, foldover definition:** Foldover reverses coded factor signs to create additional treatment settings and address aliasing. Complementary settings can belong to a foldover pair without being the same complete treatment condition. The full Table 7 transcription is supplied below; no repeated columns are removed.

**Supplied records / design constants:**

```json
{
  "factor_order": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8
  ],
  "column_index_definition": "Left-to-right position in Table 7; not execution chronology.",
  "runs": [
    {
      "column": 1,
      "factor_settings": [
        "+",
        "-",
        "+",
        "+",
        "+",
        "-",
        "-",
        "-"
      ],
      "y": 0.3
    },
    {
      "column": 2,
      "factor_settings": [
        "-",
        "+",
        "-",
        "-",
        "-",
        "+",
        "+",
        "+"
      ],
      "y": 0.65
    },
    {
      "column": 3,
      "factor_settings": [
        "+",
        "-",
        "-",
        "-",
        "-",
        "-",
        "-",
        "+"
      ],
      "y": 0.41
    },
    {
      "column": 4,
      "factor_settings": [
        "-",
        "+",
        "+",
        "+",
        "+",
        "+",
        "+",
        "-"
      ],
      "y": 0.53
    },
    {
      "column": 5,
      "factor_settings": [
        "+",
        "+",
        "-",
        "-",
        "+",
        "+",
        "+",
        "+"
      ],
      "y": 0.62
    },
    {
      "column": 6,
      "factor_settings": [
        "-",
        "-",
        "+",
        "+",
        "-",
        "-",
        "-",
        "-"
      ],
      "y": 0.42
    },
    {
      "column": 7,
      "factor_settings": [
        "+",
        "-",
        "+",
        "+",
        "+",
        "+",
        "-",
        "+"
      ],
      "y": 0.28
    },
    {
      "column": 8,
      "factor_settings": [
        "-",
        "+",
        "-",
        "-",
        "-",
        "-",
        "+",
        "-"
      ],
      "y": 0.65
    },
    {
      "column": 9,
      "factor_settings": [
        "+",
        "+",
        "+",
        "-",
        "+",
        "-",
        "+",
        "-"
      ],
      "y": 0.64
    },
    {
      "column": 10,
      "factor_settings": [
        "-",
        "-",
        "-",
        "+",
        "-",
        "+",
        "-",
        "+"
      ],
      "y": 0.33
    },
    {
      "column": 11,
      "factor_settings": [
        "-",
        "-",
        "+",
        "+",
        "-",
        "-",
        "+",
        "+"
      ],
      "y": 0.39
    },
    {
      "column": 12,
      "factor_settings": [
        "-",
        "-",
        "+",
        "+",
        "-",
        "-",
        "+",
        "+"
      ],
      "y": 0.35
    },
    {
      "column": 13,
      "factor_settings": [
        "+",
        "+",
        "-",
        "-",
        "+",
        "+",
        "-",
        "-"
      ],
      "y": 0.57
    },
    {
      "column": 14,
      "factor_settings": [
        "+",
        "+",
        "-",
        "-",
        "+",
        "+",
        "-",
        "-"
      ],
      "y": 0.6
    },
    {
      "column": 15,
      "factor_settings": [
        "-",
        "+",
        "+",
        "-",
        "+",
        "-",
        "-",
        "+"
      ],
      "y": 0.66
    },
    {
      "column": 16,
      "factor_settings": [
        "+",
        "-",
        "-",
        "+",
        "-",
        "+",
        "+",
        "-"
      ],
      "y": 0.25
    },
    {
      "column": 17,
      "factor_settings": [
        "+",
        "+",
        "-",
        "+",
        "-",
        "-",
        "-",
        "+"
      ],
      "y": 0.5
    },
    {
      "column": 18,
      "factor_settings": [
        "-",
        "-",
        "+",
        "-",
        "+",
        "+",
        "+",
        "-"
      ],
      "y": 0.41
    },
    {
      "column": 19,
      "factor_settings": [
        "+",
        "+",
        "+",
        "-",
        "-",
        "+",
        "+",
        "-"
      ],
      "y": 0.59
    },
    {
      "column": 20,
      "factor_settings": [
        "-",
        "-",
        "-",
        "+",
        "+",
        "-",
        "-",
        "+"
      ],
      "y": 0.35
    }
  ]
}
```

**Claim:** The 20 Table 7 executions are ten complete treatment conditions, each repeated twice, because the runs are arranged in foldover pairs.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E008-Q01

Which relation defines exact repetition of the complete treatment condition for replication accounting in this coded eight-factor experiment? Do not compare columns or count repetitions; code will apply the selected relation to every supplied row. Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `complete_setting_equality`: Separate run executions have identical settings for all eight coded process factors.
- `sign_complement`: Separate run executions have opposite signs for every coded process factor.
- `main_factor_match`: Separate run executions match on a selected main factor even if the other seven settings differ.
- `same_run_gas_samples`: Multiple gas collections come from one run, regardless of that run's complete factor settings.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `complete_setting_equality`.

**Evidence rationale:** Replication of the full condition requires equal full setting vectors in separate preparations. A sign complement is a different treatment; the fresh-sample procedure establishes separate executions.

**Downstream role:** Chooses the scientifically relevant equality key. Column comparison, deduplication, replicate counts, and pure-error degrees of freedom are code work.

**Question status:** author_reviewed; reviewed by: author; decision: UR008.

### Scientific decision and division of work

Foldover can provide variance information without making every pair an exact replicate. Conflating alias-control structure with replicated conditions changes the pure-error accounting.

**Judgment:** Interpret full-treatment equality versus foldover complementarity.

**Code:** Group the transcribed columns by all eight factor signs; count repeated settings and sum n_g-1 for pure-error degrees of freedom. Compare with the authors' p=2. The explicit design and source explanation support deterministic resolution; do not route a model call solely because an existing phrase parser lacks this case.

**Deterministic resolution:** `established_zero_model_call_control`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "run_count": 20,
  "distinct_complete_settings": 18,
  "repeated_column_groups": [
    [
      11,
      12
    ],
    [
      13,
      14
    ]
  ],
  "singleton_settings": 16,
  "pure_error_df": 2
}
```

**Inference boundary:** The counted degrees of freedom concern exact coded repetitions. Their use as an error estimator still follows the source's modeling assumptions.

### Review notes and source limitations

- Table 1 (PDF p. 3) provides the eight factor names and low/high levels. It lists temperature levels of 750 and 800 °C, whereas Section 6 describes each cycle as operating at 800 °C. This discrepancy remains unresolved for reconstructing physical operating conditions. The present judgment concerns equality of the eight-factor coded settings in Table 7, not chemical equivalence outside that design.
- UR008: The author accepted the reference and downstream outcome after checking the sources. The full table transcription contains all 160 factor entries and 20 responses.
- UR008: Table positions do not establish execution order; response differences do not negate treatment equality. The source variance estimate's three degrees of freedom include only two pure-error degrees of freedom.

**Source limitations retained for review:**

- FOLD-2025: The caption describes foldover pairs, while the preceding paragraph explicitly mentions both replicates and foldover pairs. The full matrix resolves which are equal conditions; no incompatible assignment remains.
- FOLD-2025: Table 1 (PDF p. 3) provides the eight factor names and low/high levels. It lists temperature levels of 750 and 800 °C, whereas Section 6 describes each cycle as operating at 800 °C. This discrepancy remains unresolved for reconstructing physical operating conditions. The present judgment concerns equality of the eight-factor coded settings in Table 7, not chemical equivalence outside that design.
- FOLD-2025: Later publication is not substituted for the inspected preprint.
- N-FOLD: Methodological corroboration only; the ethylene treatment records come from FOLD-2025.

<a id="e009"></a>

## E009 — Shared traceability across laboratory calibrations

Status: author_reviewed. Explicit author review recorded in UR009, including the S2 scope and downstream outcome; no content changes requested.

### Evidence and scope

**Target treatment:** DC-voltage calibration of the same Fluke 5700A multifunction calibrator at a common setting s, with the shared INRIM 10 V reference-standard contribution.

**Scope:** Sections III-V's INRIM-Lab / Cal-Lab interlaboratory comparison. Restrict the dependence judgment to the DC-voltage traceability term in Equation 5; do not generalize it to all uncertainty components or electrical quantities.

**MET-2016:** [Extensive Comparison between INRIM and a Secondary Calibration Laboratory using a Multifunction Electrical Calibrator](https://arxiv.org/pdf/1510.07866v3). arXiv:1510.07866v3, 21 April 2016; downloaded PDF has 7 pages. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — MET-2016, Sections III.A-IV, PDF pp. 2-3; Figure 3:** The comparison uses verification without adjustment. The Cal-Lab traceability chain shares standards calibrated at INRIM with the INRIM-Lab chain, creating partial correlation. For DC voltage, Equation 5 identifies the INRIM calibration uncertainty of the 10 V standard in both chains.

**Adaptation — MET-2016, Section V, PDF p. 3, Equations 1-5; Conclusions, PDF p. 6:** Cal-Lab measures before and after INRIM-Lab. Its two values at the same setting s are averaged to reduce possible calibrator drift in the comparison. The difference uncertainty includes a covariance term: u(d)^2 = u(E_L)^2 + u(E_I)^2 - 2 r u(E_L)u(E_I). Equation 5 gives r = u_B(std_DCV)^2/[u(E_I)u(E_L)]. The authors report high instrument stability.

**Claim:** Different laboratory names make the two laboratory results independent realizations of the shared DC-voltage reference calibration, so this covariance contribution can be dropped.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E009-Q01

What relationship does the source establish between the laboratories' DC-voltage results with respect to the reference-calibration contribution in Equation 5? Select exactly one option. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `independent_reference`: The laboratories use independent realizations of this reference-calibration contribution.
- `shared_reference`: The laboratories share a reference-calibration contribution that induces covariance between their results.
- `identical_measurement`: The laboratory labels refer to the same measurement result copied into both records.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `shared_reference`.

**Evidence rationale:** The source locates the INRIM 10 V calibration contribution in both traceability chains and retains it in Equation 5. Separate laboratory executions do not eliminate that common contribution.

**Downstream role:** Determines whether code retains the shared-reference covariance term; it does not evaluate that term numerically.

**Question status:** author_reviewed; reviewed by: author; decision: UR009.

#### E009-Q02

What role do the Cal-Lab measurements before and after the INRIM visit play in this comparison? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `bracketing_average`: They are repeated Cal-Lab measurements that bracket the INRIM visit and are averaged for the comparison.
- `two_laboratories`: They represent two additional laboratories providing separate interlaboratory results.
- `adjustment_contrast`: They are a before-and-after contrast of an intentional calibrator adjustment performed for this comparison.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `bracketing_average`.

**Evidence rationale:** Section V averages the two Cal-Lab calibrations to reduce possible drift, while Section III.A specifies verification without adjustment.

**Downstream role:** Selects the laboratory-level aggregation and prevents bracketing observations from becoming additional laboratories or a treatment contrast.

**Question status:** author_reviewed; reviewed by: author; decision: UR009.

### Scientific decision and division of work

Independent execution and independent traceability are different requirements. A calibration comparison must retain the common reference contribution even when the laboratories performed separate work.

**Judgment:** Locate the shared traceability ancestor and interpret the bracketing measurements.

**Code:** Average the two Cal-Lab values at equal s, compare with INRIM, and retain covariance. Offline algebra checks that substitution of Equation 5 yields a subtraction of 2*u_B(std_DCV)^2; no new calibration data or uncertainty values are invented.

**Deterministic resolution:** `established_for_source_equations_and_protocol`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent",
  "compared_laboratory_results": 2,
  "calibration_visits": 3,
  "shared_covariance_term": "2*u_B(std_DCV)^2",
  "exact_effective_replication_count": null
}
```

**Inference boundary:** Shared calibration ancestry does not imply identical total errors or a known scalar effective sample size.

### Review notes and source limitations

- UR009: Author accepted both questions, the downstream outcome, and inclusion within S2 as a counting/dependence judgment about a shared reference-calibration contribution.
- UR009: The approved scope is limited to the specified DC-voltage contribution. It does not extend to the full uncertainty budget, other electrical quantities, effective sample size, or perfect correlation.
- UR009: The bracketing average addresses possible drift and is not an adjustment contrast. The source limitation distinguishing a precaution from observed drift remains in place.

**Source limitations retained for review:**

- MET-2016: The preprint retains a template identification header; this is not a second experiment.
- MET-2016: The source takes precautions against possible drift and reports instrument stability; a bracketing design does not establish observed drift.
- MET-2016: Shared traceability creates particular correlated uncertainty contributions. Separate laboratory executions remain real; the question does not declare all uncertainty components identical or all errors perfectly correlated.

<a id="e010"></a>

## E010 — Complementary allocation to paired mountain ranges

Status: author_reviewed. Explicit author review recorded in UR010, including the downstream outcome and S2 scope; no content changes requested. Source wording was qualified on 2026-09-21; Choices and reference answers retain their original review attribution. See [source_revisions.json](source_revisions.json).

### Evidence and scope

**Target treatment:** Assignment of ground-based silver-iodide cloud seeding to Sierra Madre or Medicine Bow during a four-hour experimental unit (EU).

**Scope:** The 118 quality-controlled EUs used in the WWMPP primary analysis. One EU includes the paired ranges. Target sites are HY (Sierra Madre) and GL (Medicine Bow); auxiliary gauges and possible cross-range contamination do not redefine the assigned treatment.

**CLOUD-2018:** [Evaluation of the Wyoming Weather Modification Pilot Project (WWMPP) Using Two Approaches: Traditional Statistics and Ensemble Modeling](https://www.researchgate.net/publication/328180082_Evaluation_of_the_Wyoming_Weather_Modification_Pilot_Project_WWMPP_Using_Two_Approaches_Traditional_Statistics_and_Ensemble_Modeling). Rasmussen et al., Journal of Applied Meteorology and Climatology 57 (2018), 2639-2660; author-uploaded full text, 26 December 2018. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**CLOUD-2014:** [Wyoming Weather Modification Pilot Project: Final Results Presentation](https://crwua.org/wp-content/uploads/2024/01/WWMPP-CRWUA-Dec-2014.pdf). Investigators' December 2014 results presentation; 50-slide public copy hosted in a 2024 directory. Access: 2026-09-21 (UTC); 2026-09-20 (America/New_York).

**Adaptation — CLOUD-2018, Section 2, Figure 1 explanation, and Table 1 with its caption, pp. 2640-2643:** Within an EU, seeding is randomly assigned to one range and not the other. The authors explicitly say the Medicine Bow assignment plot would have the opposite shading from the Sierra Madre plot. The authors report 154 EUs, 27 precipitation-QC exclusions, and nine additional generator-performance exclusions, leaving 118 for the primary analysis. The monthly generator-exclusion cells in Table 1 sum to eight, while its margins and the prose report nine; the retained count here follows the authors' reported totals.

**Adaptation — CLOUD-2018, Section 2a and Figure 2, pp. 2642-2643:** The design has eight generators per range and multiple precipitation gauges; gauge QC is conducted without knowledge of seeding assignments.

**Adaptation — CLOUD-2014, Slides 16-18, 24 and 29:** The presentation shows the paired design, four-hour measurements, and a 118-case Medicine Bow assignment plot. Slide 24 reports ground-based ice-nucleus measurements indicating that silver iodide reached Medicine Bow in 21 Sierra Madre seeding cases. Slide 29 reports 18 modeled cases of enhanced precipitation in Medicine Bow during Sierra Madre seeding in winters 2009/10, 2011/12, and 2013/14. These are different diagnostics within the same trial reported in 2018.

**Supplied records / design constants:**

```json
{
  "initial_EUs": 154,
  "precipitation_QC_exclusions": 27,
  "generator_exclusions": 9,
  "reported_retained_EUs": 118,
  "ranges_per_EU": 2
}
```

**Claim:** The two range records in every retained EU represent two independently randomized seeding decisions, and the assigned-unseeded range is thereby confirmed to have no seeding exposure.

**Claim origin:** benchmark_constructed; not attributed to the source authors

### Atomic questions and accepted references

#### E010-Q01

How are the two range-level seeding assignments related within one retained EU? Select exactly one option. Use other only when the evidence establishes an answer outside the substantive alternatives. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `independent_assignments`: Each range is independently randomized, so both or neither can be assigned seeding within that EU.
- `complementary_assignment`: One joint allocation selects the seeded range, and the other range receives the complementary unseeded assignment.
- `both_seeded`: Both ranges are assigned seeding together as one treated pair.
- `permanent_range`: One range is permanently assigned seeding and the other remains unseeded throughout the study.
- `other`: The evidence establishes a different substantive answer from those listed.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `complementary_assignment`.

**Evidence rationale:** The article explicitly describes mutually exclusive seeding and opposite assignment-plot shading for the two ranges.

**Downstream role:** Defines the joint assignment event; code counts paired EUs separately from range records.

**Question status:** author_reviewed; reviewed by: author; decision: UR010.

#### E010-Q02

Does an assigned-unseeded label, by itself, establish zero physical exposure to seeding material in this study? Select exactly one option. Use not_stated when missing, incomplete, or ambiguous supplied evidence prevents this judgment without unresolved incompatible statements. Use conflicting only for unresolved incompatible evidence about this same judgment and scope.

- `zero_exposure_established`: Yes; assignment to the unseeded range establishes that it received no seeding material.
- `assignment_only`: No; it establishes the planned allocation, while physical exposure requires additional evidence because cross-range contamination is discussed.
- `exposure_confirmed_everywhere`: No; the label establishes that every unseeded range-period was physically exposed to seeding material.
- `not_stated`: The supplied evidence does not establish the requested judgment.
- `conflicting`: The supplied evidence contains unresolved incompatible accounts of this judgment and scope.

**Accepted reference:** `assignment_only`.

**Evidence rationale:** The 2014 presentation reports measured and modeled cross-range effects. Assignment therefore does not certify zero exposure, and those diagnostics do not establish exposure in every unseeded range-period.

**Downstream role:** Keeps the assignment-based replicate accounting distinct from any exposure-based reclassification.

**Question status:** author_reviewed; reviewed by: author; decision: UR010.

### Scientific decision and division of work

Two simultaneously observed targets do not imply two independent assignment draws. Exposure records could change an exposure-based analysis without changing the original paired allocation.

**Judgment:** Identify complementary assignment and distinguish allocation from realized exposure.

**Code:** Retain 118 joint allocation events and two range-level records per retained event; verify 154-27-9. Do not reconstruct target assignments from differently labeled plots or classify per-EU exposure without its evidence.

**Deterministic resolution:** `established_for_reported_assignment_and_totals; per_EU_exposure_unassessed`.

**Accepted downstream outcome:**

```json
{
  "claim_assessment": "inconsistent_independent_assignment; zero_exposure_not_established_by_label",
  "original_EUs": 154,
  "retained_EUs": 118,
  "joint_assignment_events": 118,
  "range_level_records": 236,
  "independent_range_draws_claim": false
}
```

**Inference boundary:** This does not certify temporal independence among all EUs or re-estimate the cloud-seeding effect.

### Review notes and source limitations

- UR010: The author accepted both questions, the downstream outcome, and the S2 scope. The two source plots retain their different mountain-range identities; plot colors cannot be merged without target identity.
- Calendar and wind-criterion discrepancies are retained in sources.json but do not conflict with the selected allocation judgment.
- UR010: Per-EU physical exposure remains unassessed. The 21 measured transport cases and 18 modeled enhancement cases do not supply per-EU labels or redefine assigned treatment/control.
- UR010: The 118 EUs yield 118 joint assignment events and 236 range-level records, not 236 independent assignments. Effect sizes, p-values, causal conclusions, and temporal independence are outside the approved judgment.

**Source limitations retained for review:**

- CLOUD-2018: Full article text was inspected through the author-uploaded ResearchGate page; full PDF retrieval and publisher article access returned HTTP 403. Publisher Table 1 was retrieved separately and visually checked on 2026-09-21.
- CLOUD-2018: Table 1 generator exclusions sum to eight across monthly cells, but the margins and prose report nine. The March cells sum to zero versus a row total of one; the 2008/09 cells sum to two versus a column total of three. The 118 retained EUs are the author-reported total, not a reconciled reconstruction from every cell. No missing event is imputed. [Publisher Table 1](https://journals.ametsoc.org/view/journals/apme/57/11/full-jamc-d-17-0335.1-t1.jpg).
- CLOUD-2018: The Table 1 caption assigns four EUs failing both precipitation and generator checks to precipitation QC. The nine generator exclusions are additional to the 27 precipitation exclusions; overlapping failures are not subtracted again.
- CLOUD-2018: The prose calls the winters 2008-13, while Table 1 uses 2008/09-2013/14. The present scope is the explicitly reported 118 retained EUs, not reconstructed dates.
- CLOUD-2018: Wind-direction criteria differ between the introductory account and Section 2b; this does not change the documented complementary assignment.
- CLOUD-2018: Cross-range exposure evidence used in E010 comes from CLOUD-2014 slides 24 and 29, not an independently replicated experiment.
- CLOUD-2018: The paper's p-value gloss is not adopted as a probability that the null hypothesis is true; significance testing is outside this problem.
- CLOUD-2014: The slide plot labels Medicine Bow, whereas the 2018 Figure 1 plot labels Sierra Madre. Their colors must not be joined as though they identify the same target.
- CLOUD-2014: The PDF has malformed object offsets tolerated by the PDF readers; rendered slides were checked.
- CLOUD-2014: The slide p-value wording is not used as a statistical reference.
