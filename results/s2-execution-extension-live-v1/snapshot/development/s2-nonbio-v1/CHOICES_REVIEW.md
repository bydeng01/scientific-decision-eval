# S2: questions, choices, and reference review

2026-09-20 · Choice review v1, revision 2 · English · 12 existing items, 6 groups, 5 sources.

This document combines the complete prepared evidence, scoped claims, atomic questions, option descriptions, and evaluation-only expected answers for eleven scientific claims and the D01-O engineering check.

All fifteen question definitions and reference mappings below are user-approved. [REVIEW_LOG.md](choice-review-v1/REVIEW_LOG.md) gives their review attribution and decisions; source review is recorded separately in [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md). The Choice definitions do not activate calls in the original rule runner.

The evidence and claims below are copied from the existing English inputs. They are translated source adaptations, not verbatim paper quotations. Source records and prior human review remain in [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md).

Machine-readable [question inputs](choice-review-v1/inputs.json) contain no expected options or final reference labels. [Evaluation references](choice-review-v1/evaluation.json) are separate. This Markdown document intentionally includes answers for human review and must never be sent to a model as its state.

A Choice has an instruction and a map from option IDs to descriptions. Descriptions define the alternatives; reference answers stay in evaluation files. `other` means the evidence establishes an answer outside the substantive alternatives. `not_stated` covers missing, incomplete, or ambiguous information that prevents the requested judgment, without unresolved contradictory evidence. The conflict option takes precedence when relevant statements are incompatible within the stated scope; this rule is included in every question's model-facing instructions. [Official Choice interface](https://docs.typesafe.ai/primitives/choice).

`partly_shared` denotes an established mixture of shared and different parents, not incomplete information. Partial records can still establish that pattern if they identify a shared pair and another entity with a different parent. D03 separately distinguishes partial run identification and partial specimen assignment. Those options preserve known information without filling in missing records. No question asks the model to calculate a count.

## Item index

| Item | Atomic Choice drafts | Active route | Choice review |
|---|---|---|---|
| [D01](#d01) | D01.unit, D01.membership | Rule; no model call | User approved |
| [D01-S](#d01) | D01.unit, D01.membership | Rule; no model call | User approved |
| [D01-O](#d01) | D01-O.omitted_unit | Rule + candidate-omission simulation | User approved |
| [D02](#d02) | D02.unit, D02.membership | Rule; no model call | User approved |
| [D02-S](#d02) | D02.unit, D02.membership | Rule; no model call | User approved |
| [D03](#d03) | D03.treatment_level, D03.run_boundary, D03.specimen_assignment | Rule; no model call | User approved |
| [C01-T](#c01) | C01-T.unit | Rule; no model call | User approved |
| [C01-A](#c01) | C01-A.unit | Rule; no model call | User approved |
| [H01-L](#h01) | H01-L.unit | Rule; no model call | User approved |
| [H01-T](#h01) | H01-T.unit, H01-T.membership | Rule; no model call | User approved |
| [C02](#c02) | C02.unit, C02.identifier | Rule; no model call | User approved |
| [C02-S](#c02) | C02.unit, C02.identifier | Rule; no model call | User approved |

There are 15 distinct question definitions: 14 questions for scientific claims and one engineering simulation. Paired claims share relevant questions. These are interface definitions, not 15 independent cases or planned calls.

## Final outcomes computed by code

`supported`: all quantities in the scoped claim agree with the established relation. `inconsistent`: at least one quantity disagrees. `insufficient`: the evidence does not establish a required count. Parser failure is a separate failure state, not scientific insufficiency. These are downstream labels, not an extra model question.

## D01

**Source U:** Rezazadeh et al. (2026), *Dataset on the reproducibility of UHPC mechanical properties under a fixed recipe with controlled production variability*, Scientific Data 13, 1058. DOI: `10.1038/s41597-026-07805-z`.

[Source link 1](https://www.nature.com/articles/s41597-026-07805-z) · [Source link 2](https://www.nature.com/articles/s41597-026-07805-z.pdf)

**Location:** PDF p9 Methods: Mixing conditions; Mechanical properties; p11; p12 Fig. 6; p8, p14 shared mixing batch across curing records.

**Inherited review:** User-confirmed scientific scope, mixing relation, and labels. D01-O is an engineering fixture.

**Complete evidence**

> Mixer speed and duration are set for each mixing operation. Mechanical testing includes 24-hour and 28-day groups, with three prisms in each group. This check covers only the 28-day group from the same mixing operation and the same curing regimen: the three prisms each undergo flexural testing, followed by compression testing of the two half-prisms produced from each prism.

**Scoped claims and reviewed code outcomes**

- **D01** — Target: mixing conditions. Scope: The 28-day group from the same mixing operation and the same curing regimen.
  Claim: The six half-prisms in this group provide six independent mixing replicates to which these mixing conditions were applied.
  Declared quantities: `{"target": 6}`. Reference count: `1`; label: `inconsistent`; action: `revise_scoped_claim`.
- **D01-S** — Target: mixing conditions. Scope: The 28-day group from the same mixing operation and the same curing regimen.
  Claim: This group comes from one mixing operation; its three prisms and six half-prisms do not increase the number of mixing operations.
  Declared quantities: `{"target": 1, "prism": 3, "half_prism": 6}`. Reference count: `1`; label: `supported`; action: `accept_scoped_claim`.
- **D01-O** — Target: mixing conditions. Scope: The 28-day group from the same mixing operation and the same curing regimen.
  Claim: The six half-prisms in this group provide six independent mixing replicates to which these mixing conditions were applied.
  Declared quantities: `{"target": 6}`. Reference count: `1`; label: `inconsistent`; action: `revise_scoped_claim`.
  The count and label above are its normal code path. The separate omission simulation expects `other`, stops dependent counting in that branch, and requests candidate completion or transfer.

**Deterministic work:** Read the stated three prisms and two halves per prism; enforce the same mixing operation, curing regimen, and 28-day scope; count each entity level and compare each claim. D01-O separately simulates candidate omission.

### D01.unit

**Applies to:** D01, D01-S.

**Choice review:** User approved; accepted with revisions.

**Question:** At which unit are mixer speed and mixing duration set in the supplied production workflow? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `mixing_batch` | The batch produced by one mixing operation. |
| `prism` | One intact prism made from a mixture. |
| `half_prism` | One half-prism produced by breaking an intact prism. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `mixing_batch`. The passage assigns mixer speed and duration to each mixing operation. Prism and half-prism production occur downstream.

### D01.membership

**Applies to:** D01, D01-S.

**Choice review:** User approved; accepted with revisions.

**Question:** How do the three prisms in the specified 28-day group relate to mixing operations? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `shared` | All selected prisms belong to the same mixing operation. |
| `distinct` | Each of the selected prisms belongs to a different mixing operation; none share one. |
| `partly_shared` | At least two of the selected prisms share a mixing operation, and at least one other belongs to a different mixing operation. |
| `not_stated` | Missing, incomplete, or ambiguous evidence does not establish any of the three listed membership patterns, without conflicting mixing-operation membership statements. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about the mixing-operation membership of the selected prisms. |

**Reference — evaluation only:** `shared`. The stated scope explicitly places these prisms in the same mixing operation and curing regimen.

### D01-O.omitted_unit

**Applies to:** D01-O.

**Choice review:** User approved; accepted with revisions.

**Question:** At which unit are mixer speed and mixing duration set in the supplied production workflow? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `prism` | One intact prism made from a mixture. |
| `half_prism` | One half-prism produced by breaking an intact prism. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `other`. The identified mixing-batch unit is intentionally absent. Other requests candidate completion or transfer; not_stated would incorrectly describe the evidence.

## D02

**Source A:** Shanbhag et al. (2021), *Data related to the effect of specimen geometry and orientation on tensile properties of Ti-6Al-4V manufactured by electron beam powder bed fusion*, Data in Brief 39, 107613. DOI: `10.1016/j.dib.2021.107613`.

[Source link 1](https://doi.org/10.1016/j.dib.2021.107613) · [Source link 2](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/c76e04af-b2c6-42ff-89d0-a7492f9fef9e/content)

**Location:** PDF p2 Data Description item 1; p4 Table 2: E8-3, Z, specimens 7/8/9; p5 Data Description item 2.

**Inherited review:** User-confirmed specimen table. Unit relations and labels have separate review attribution in [the source review record](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check).

**Complete evidence**

> The study manufactured specimens with different geometries and orientations in a single complete EB-PBF build. In Table 2, the E8-3 row with Z orientation lists specimens 7, 8, and 9 under Replicate 1, 2, and 3, respectively.

**Scoped claims and reviewed code outcomes**

- **D02** — Target: complete manufacturing process. Scope: Table 2: E8-3 geometry, Z orientation, specimens 7, 8, and 9.
  Claim: These three specimens represent three independent repetitions of the complete manufacturing process.
  Declared quantities: `{"target": 3}`. Reference count: `1`; label: `inconsistent`; action: `revise_scoped_claim`.
- **D02-S** — Target: complete manufacturing process. Scope: Table 2: E8-3 geometry, Z orientation, specimens 7, 8, and 9.
  Claim: These are three specimens within one build.
  Declared quantities: `{"target": 1, "specimen": 3}`. Reference count: `1`; label: `supported`; action: `accept_scoped_claim`.

**Deterministic work:** Filter Table 2 to E8-3/Z specimens 7, 8, and 9; deduplicate their parent build; compare build and specimen quantities.

### D02.unit

**Applies to:** D02, D02-S.

**Choice review:** User approved; accepted with revisions.

**Question:** Which unit corresponds to one repetition of the complete manufacturing process described in the passage? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `build` | One complete EB-PBF build. |
| `specimen` | One tensile specimen produced within a build. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `build`. The complete process is the EB-PBF build; the table lists specimens manufactured within it.

### D02.membership

**Applies to:** D02, D02-S.

**Choice review:** User approved; accepted with revisions.

**Question:** How do the selected E8-3/Z specimens relate to complete EB-PBF builds? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `shared` | All selected E8-3/Z specimens belong to the same complete EB-PBF build. |
| `distinct` | Each of the selected E8-3/Z specimens belongs to a different complete EB-PBF build; none share one. |
| `partly_shared` | At least two of the selected E8-3/Z specimens share a complete EB-PBF build, and at least one other belongs to a different complete EB-PBF build. |
| `not_stated` | Missing, incomplete, or ambiguous evidence does not establish any of the three listed membership patterns, without conflicting build membership statements. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about the build membership of the selected E8-3/Z specimens. |

**Reference — evaluation only:** `shared`. The complete passage states that the study manufactured its specimens in a single complete build.

## D03

**Source U:** Rezazadeh et al. (2026), *Dataset on the reproducibility of UHPC mechanical properties under a fixed recipe with controlled production variability*, Scientific Data 13, 1058. DOI: `10.1038/s41597-026-07805-z`.

[Source link 1](https://www.nature.com/articles/s41597-026-07805-z) · [Source link 2](https://www.nature.com/articles/s41597-026-07805-z.pdf)

**Location:** PDF p9 Curing conditions; Mechanical properties; p4 Table 2; p5 Fig. 2 and caption.

**Inherited review:** User-confirmed control level, missing run boundaries and specimen assignments, and insufficiency decision.

**Complete evidence**

> The methods record curing environment category and temperature by batch. In the water-curing branch, a water bath at a set temperature is used from demolding until day 28; an in-bath probe measures the water temperature. Mechanical testing at 28 days uses a group of three prisms from that batch. Figure 2 shows the curing equipment, including a photograph of a water bath.

**Scoped claims and reviewed code outcomes**

- **D03** — Target: water-bath curing temperature. Scope: The three prisms tested at 28 days from the batch in the water-curing branch.
  Claim: In the water-curing branch, these three prisms represent three independent water-bath runs in which the temperature condition was separately set and applied.
  Declared quantities: `{"target": 3}`. Reference count: unknown; label: `insufficient`; action: `request_run_boundary_and_specimen_run_records`.

**Deterministic work:** Keep run count unknown when run identification or specimen assignment is missing; request the missing records. Never infer a single run from one equipment photograph.

### D03.treatment_level

**Applies to:** D03.

**Choice review:** User approved; accepted with revisions.

**Question:** At what physical control level is temperature set for the water-curing branch in the supplied evidence? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `water_bath_temperature_control` | Temperature control of the water bath used for curing. |
| `individual_prism_temperature_control` | Temperature set and controlled separately for each individual prism. |
| `mixing_process_temperature_control` | Temperature control during mixing, before the curing stage. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `water_bath_temperature_control`. A bath setpoint and an in-bath probe establish the control level. This option makes no claim about the number or boundaries of bath runs.

### D03.run_boundary

**Applies to:** D03.

**Choice review:** User approved; accepted with revisions.

**Question:** How completely does the supplied evidence distinguish the relevant water-bath temperature-control run executions? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `identified` | Identifiers or explicit execution boundaries distinguish all relevant runs, with no conflicting run records. An equipment identifier alone does not identify a run. |
| `partial_identification` | At least one relevant run is distinguishable, but the evidence does not establish a complete set of relevant run identities or boundaries; no conflicting run records are supplied. |
| `not_stated` | The supplied evidence does not distinguish any relevant run as an execution, and contains no conflicting run records. |
| `conflicting` | The supplied evidence contains unresolved, incompatible records about the identities or execution boundaries of relevant runs. |

**Reference — evaluation only:** `not_stated`. The curing period and bath photograph do not delineate individual run executions.

### D03.specimen_assignment

**Applies to:** D03.

**Choice review:** User approved; accepted with revisions.

**Question:** Does the supplied evidence establish a water-bath-run assignment for each prism in the specified 28-day group? Use conflicting_assignment for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `complete_assignment` | The evidence establishes a consistent assignment to identified run executions for every selected prism; multiple prisms may share a run. |
| `partial_assignment` | The evidence establishes a consistent assignment to identified run executions for some but not all selected prisms, with no conflicting assignment records. |
| `not_stated` | No assignment to an identified run execution is established for any selected prism, and no conflicting assignment records are supplied. |
| `conflicting_assignment` | The supplied records give unresolved, incompatible run assignments for at least one selected prism. |

**Reference — evaluation only:** `not_stated`. The supplied material lists the prism group but contains no prism-to-run records.

## C01

**Source N:** NIST/SEMATECH, How can I account for nested variation (restricted randomization)?, e-Handbook section 5.5.5.

[Source link 1](https://itl.nist.gov/div898/handbook/pri/section5/pri55.htm)

**Location:** NIST 5.5.5, second scenario: batch process, unit definitions.

**Inherited review:** User-confirmed source scenario, factor-specific units, and labels.

**Complete evidence**

> Four copper strips enter a single treatment together. Temperature and concentration apply jointly to this group; within the group, two strips are randomly assigned to low current and two to high current. Each of the four temperature-concentration combinations is run once. The source explicitly defines a single copper strip as the experimental unit for current (subplot experimental unit), and the group of four strips treated together as the unit for temperature and concentration (whole-plot experimental unit).

**Scoped claims and reviewed code outcomes**

- **C01-T** — Target: temperature and concentration. Scope: One fixed temperature-concentration combination.
  Claim: This combination has four independent group-level treatment units.
  Declared quantities: `{"target": 4}`. Reference count: `1`; label: `inconsistent`; action: `revise_scoped_claim`.
- **C01-A** — Target: current. Scope: One fixed temperature-concentration combination.
  Claim: Within this combination, low current is assigned to two strip-level treatment units.
  Declared quantities: `{"target": 2}`. Reference count: `2`; label: `supported`; action: `accept_scoped_claim`.

**Deterministic work:** Use the stated group and low-current assignment; count the source-defined units for each target and compare the claims.

### C01-T.unit

**Applies to:** C01-T.

**Choice review:** User approved; accepted with revisions.

**Question:** Which experimental unit does the source assign to temperature and concentration in this batch-process scenario? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `whole_plot_group` | The copper-strip group treated together in one batch operation. |
| `strip` | One individual copper strip within the group. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `whole_plot_group`. The source explicitly defines the treated group as the whole-plot unit for temperature and concentration.

### C01-A.unit

**Applies to:** C01-A.

**Choice review:** User approved; accepted with revisions.

**Question:** Which experimental unit does the source assign to current in this batch-process scenario? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `whole_plot_group` | The copper-strip group treated together in one batch operation. |
| `strip` | One individual copper strip within the group. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `strip`. The source explicitly defines an individual strip as the subplot unit for current.

## H01

**Source H:** Weaver et al. (2021), *Demonstration of a laser powder bed fusion combinatorial sample for high-throughput microstructure and indentation characterization*, Materials & Design 209, 109969. DOI: `10.1016/j.matdes.2021.109969`.

[Source link 1](https://doi.org/10.1016/j.matdes.2021.109969) · [Source link 2](https://www.nist.gov/publications/demonstration-laser-powder-bed-fusion-combinatorial-sample-high-throughput) · [Source link 3](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=929236)

**Location:** 60-page author manuscript pp6-7 section 2.1; p8 Fig. 1; p9 Table 2 and split-plot explanation; p13 section 2.2; p27 spatial proximity discussion.

**Inherited review:** User-confirmed column table. Unit relations and labels have separate review attribution in [the source review record](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check).

**Complete evidence**

> A continuous nickel-alloy combinatorial specimen contains multiple column regions, each processed at a specified laser power and scan speed. Columns 1, 10, 16, 19, and 24 in Table 2 use the same default settings. The study produced multiple specimens of the same geometry; one whole specimen received stress-relief treatment at 800°C and another at 870°C. The authors explicitly describe a split-plot design because each combinatorial specimen was fabricated and stress-relieved as a continuous whole. Multiple indentation measurements were then taken within each column region.
> This check covers only the combinatorial specimen treated at 870°C and the default-setting columns listed above; other specimens and columns are excluded.

**Scoped claims and reviewed code outcomes**

- **H01-L** — Target: default laser settings. Scope: The whole specimen treated at 870°C and default-setting columns 1, 10, 16, 19, and 24.
  Claim: The default laser settings have five column-level application units within this specimen.
  Declared quantities: `{"target": 5}`. Reference count: `5`; label: `supported`; action: `accept_scoped_claim`.
- **H01-T** — Target: whole-specimen heat treatment. Scope: The whole specimen treated at 870°C and default-setting columns 1, 10, 16, 19, and 24.
  Claim: The same five columns provide five separate repetitions of the 870°C whole-specimen heat treatment.
  Declared quantities: `{"target": 5}`. Reference count: `1`; label: `inconsistent`; action: `revise_scoped_claim`.

**Deterministic work:** Select the 870-degree whole specimen and columns 1, 10, 16, 19, and 24; count columns or the selected whole specimen for the relevant treatment. Do not count furnace runs or infer statistical independence.

### H01-L.unit

**Applies to:** H01-L.

**Choice review:** User approved; accepted with revisions.

**Question:** At which specimen level are laser power and scan speed assigned in the supplied fabrication description? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `whole_specimen` | One continuous combinatorial specimen as a whole. |
| `column_region` | One column region within a combinatorial specimen. |
| `indentation` | One individual indentation measurement within a column region. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `column_region`. Laser parameters are assigned to column regions. This is an application-unit judgment, not a claim of independent manufacturing replicates.

### H01-T.unit

**Applies to:** H01-T.

**Choice review:** User approved; accepted with revisions.

**Question:** At which specimen level is the selected stress-relief heat treatment applied in the supplied description? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `whole_specimen` | One continuous combinatorial specimen as a whole. |
| `column_region` | One column region within a combinatorial specimen. |
| `indentation` | One individual indentation measurement within a column region. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `whole_specimen`. Stress relief is applied to the continuous specimen as a whole. This does not identify or count furnace runs.

### H01-T.membership

**Applies to:** H01-T.

**Choice review:** User approved; accepted with revisions.

**Question:** How do the selected default-setting columns relate to whole specimens receiving the selected heat treatment? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `shared` | All selected column regions belong to the same whole treated specimen. |
| `distinct` | Each of the selected column regions belongs to a different whole treated specimen; none share one. |
| `partly_shared` | At least two of the selected column regions share a whole treated specimen, and at least one other belongs to a different whole treated specimen. |
| `not_stated` | Missing, incomplete, or ambiguous evidence does not establish any of the three listed membership patterns, without conflicting whole-specimen membership statements. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about the whole-specimen membership of the selected column regions. |

**Reference — evaluation only:** `shared`. The scope selects columns within the one whole specimen treated at 870 degrees Celsius.

## C02

**Source J:** Jason Wiggins (US Synthetic), *Advanced Measurement System Analysis for a Destructive Gauge Using a Split-Plot Design*.

[Source link 1](https://community.jmp.com/kvoqx44227/attachments/kvoqx44227/discovery-2017-content/17/5/Advanced%20Measurement%20System%20Analysis%20for%20a%20Destructive%20Gauge%20Using%20a%20Split%20Design.pdf)

**Location:** PDF p8 operator/cutter assignment; p9 Repeat Measures Discussion, Fig. 2.6 rows 1-6 only.

**Inherited review:** User-confirmed corrected six-row/operator table. Unit relations and labels have separate review attribution in [the source review record](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check).

**Complete evidence**

> Wear scars are generated at different circumferential positions on a cutter. Each scar results from a machining operation performed by one operator, who then scans that scar three times. The first character of PART ID identifies the cutter, and the second identifies the wear scar. From Figure 2.6, this check selects six scan records for cutter 1, PART IDs 1A and 1B: 1A, 1A, and 1A are assigned to operator O1; 1B, 1B, and 1B are assigned to operator O3; 1C and 1D are excluded.

**Scoped claims and reviewed code outcomes**

- **C02** — Target: wear-scar generation. Scope: Figure 2.6, rows 1-6: 1A/O1 and 1B/O3, pooling operators; exclude 1C and 1D.
  Claim: The six selected records correspond to six wear-scar generation operations in total.
  Declared quantities: `{"target": 6}`. Reference count: `2`; label: `inconsistent`; action: `revise_scoped_claim`.
- **C02-S** — Target: wear-scar generation. Scope: Figure 2.6, rows 1-6: 1A/O1 and 1B/O3, pooling operators; exclude 1C and 1D.
  Claim: The six selected records correspond to two wear-scar generation operations in total.
  Declared quantities: `{"target": 2}`. Reference count: `2`; label: `supported`; action: `accept_scoped_claim`.

**Deterministic work:** Select rows 1-6, pooling 1A/O1 and 1B/O3; deduplicate full PART IDs; compare event counts. The O1-only regression count remains one.

### C02.unit

**Applies to:** C02, C02-S.

**Choice review:** User approved; accepted with revisions.

**Question:** Which unit should be counted when assessing repetitions of wear-scar generation in the supplied workflow? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `wear_event` | A machining operation that generates a wear scar. |
| `scan` | A scan that measures an existing wear scar. |
| `cutter` | Use of an entire cutter, pooling all scars on it. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `wear_event`. A scar is generated by machining and then scanned repeatedly. Repeated scans do not generate new scars.

### C02.identifier

**Applies to:** C02, C02-S.

**Choice review:** User approved; accepted with revisions.

**Question:** According to the supplied identifier definition, which identifier encodes both cutter identity and wear-scar identity? Use conflicting for unresolved contradictions about this judgment within the stated scope.

| Option ID | Description supplied to the model |
|---|---|
| `part_id` | The complete PART ID. |
| `cutter_character` | Only the first character of PART ID. |
| `scar_character` | Only the second character of PART ID. |
| `operator` | The operator code. |
| `scan_row` | The individual scan-row position. |
| `other` | The supplied evidence establishes an answer outside the listed substantive options. |
| `not_stated` | Missing, incomplete, or ambiguous evidence prevents a unique answer, without conflicting statements about this judgment. |
| `conflicting` | The supplied evidence contains unresolved, incompatible statements about this judgment within the stated scope. |

**Reference — evaluation only:** `part_id`. The first PART ID character identifies the cutter and the second identifies its scar. The complete PART ID retains both identities. Code groups only the six selected 1A/O1 and 1B/O3 rows by this field.

## Review and execution boundary

The accepted review checked atomicity, physical meaning, candidate coverage, missing and conflicting evidence, reference support, and the division between judgment and code. All 15 definitions were accepted with the revisions recorded in the log. Existing source and scope confirmations retain their earlier attribution; no new source contradiction was found in the supplied evidence.

The current parser still resolves these exact prepared passages. The drafts document reviewed semantic interfaces; they are not residual model tasks in the current runner. Unit choices alone do not supply all entity memberships. In particular, partly_shared does not specify an exact parent count for an arbitrary group; code needs the underlying assignments before it can count. The existing rules still extract the remaining quantities and relations, and any later model workflow needs an explicit routing and scoring design.

The source issues remain as previously recorded: H has a 295/285 W discrepancy outside the selected column-ID question, and U lacks audited bath-run mapping records. New choices do not resolve these source issues.

Choice-review preparation time and tooling costs have not been measured.
