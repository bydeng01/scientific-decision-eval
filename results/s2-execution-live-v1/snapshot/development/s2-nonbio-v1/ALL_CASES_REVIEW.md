# S2 non-biological cases: evidence and review record

2026-09-20 · English development revision `s2-nonbio-en-v1`.

The collection contains six case groups and twelve items from five sources: eleven scientific claims and one engineering routing check. D01 and D03 share source U. Paired claims and repeated runs remain grouped by their underlying source.

These English passages translate reviewed source adaptations while preserving scientific scope, identifiers, and claims. They are not verbatim quotations from the papers. Translation checks are recorded in [LANGUAGE_MIGRATION.json](LANGUAGE_MIGRATION.json). The user has approved the English wording and the scientific content within the scope recorded in section 4.

The machine-readable evidence and questions are in [inputs/](inputs/evidence.json). References and scoring are stored separately in [evaluation/](evaluation/references.json). For execution and results, see [PREFLIGHT.md](PREFLIGHT.md).

The [question-and-choice review](CHOICES_REVIEW.md) contains atomic instructions, complete option descriptions, and expected option mappings for all twelve items. [REVIEW_LOG.md](choice-review-v1/REVIEW_LOG.md) records the fifteen question-level decisions and their attribution. Question-level review and the source review below have different scopes.

## 1. Sources and case groups

| Group | Items | Source | Material |
|---|---|---|---|
| D01 | D01, D01-S, D01-O | U | Adapted production/testing workflow; no individual batch-data audit |
| D02 | D02, D02-S | A | Published study, specimens 7, 8, 9 |
| D03 | D03 | U | Curing workflow; run-to-specimen records unavailable in the supplied material |
| C01 | C01-T, C01-A | N | Handbook teaching design |
| H01 | H01-L, H01-T | H | Published materials experiment and original column IDs |
| C02 | C02, C02-S | J | Industrial case report and selected figure rows |


### U: UHPC production and mechanical testing

Rezazadeh et al. (2026), *Dataset on the reproducibility of UHPC mechanical properties under a fixed recipe with controlled production variability*, Scientific Data 13, 1058. DOI: `10.1038/s41597-026-07805-z`.

- [Source 1](https://www.nature.com/articles/s41597-026-07805-z)
- [Source 2](https://www.nature.com/articles/s41597-026-07805-z.pdf)
- D01: PDF p9 Methods: Mixing conditions; Mechanical properties; p11; p12 Fig. 6; p8, p14 shared mixing batch across curing records.
- D03: PDF p9 Curing conditions; Mechanical properties; p4 Table 2; p5 Fig. 2 and caption.
- Recorded PDF SHA-256: `c8bc5a28b954a10f6f426c1c80edba12a287f18ee0d1224dd3b5e57cae74cc86`.

### A: Additively manufactured tensile specimens

Shanbhag et al. (2021), *Data related to the effect of specimen geometry and orientation on tensile properties of Ti-6Al-4V manufactured by electron beam powder bed fusion*, Data in Brief 39, 107613. DOI: `10.1016/j.dib.2021.107613`.

- [Source 1](https://doi.org/10.1016/j.dib.2021.107613)
- [Source 2](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/c76e04af-b2c6-42ff-89d0-a7492f9fef9e/content)
- D02: PDF p2 Data Description item 1; p4 Table 2: E8-3, Z, specimens 7/8/9; p5 Data Description item 2.
- Recorded PDF SHA-256: `29e9118aba9bb30856132da99f85a84d8c8b3a9b851249e5b0e0d8a5ef29bb5f`.

### N: NIST electroplating design

NIST/SEMATECH, How can I account for nested variation (restricted randomization)?, e-Handbook section 5.5.5.

- [Source 1](https://itl.nist.gov/div898/handbook/pri/section5/pri55.htm)
- C01: NIST 5.5.5, second scenario: batch process, unit definitions.

### H: Combinatorial metal specimen

Weaver et al. (2021), *Demonstration of a laser powder bed fusion combinatorial sample for high-throughput microstructure and indentation characterization*, Materials & Design 209, 109969. DOI: `10.1016/j.matdes.2021.109969`.

- [Source 1](https://doi.org/10.1016/j.matdes.2021.109969)
- [Source 2](https://www.nist.gov/publications/demonstration-laser-powder-bed-fusion-combinatorial-sample-high-throughput)
- [Source 3](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=929236)
- H01: 60-page author manuscript pp6-7 section 2.1; p8 Fig. 1; p9 Table 2 and split-plot explanation; p13 section 2.2; p27 spatial proximity discussion.
- Recorded PDF SHA-256: `938d055b7139ba045b6f57d8c2e0de4c70b5bfee38bf838e8f3e6ece788a0b0d`.

### J: Industrial cutter wear and scanning

Jason Wiggins (US Synthetic), *Advanced Measurement System Analysis for a Destructive Gauge Using a Split-Plot Design*.

- [Source 1](https://community.jmp.com/kvoqx44227/attachments/kvoqx44227/discovery-2017-content/17/5/Advanced%20Measurement%20System%20Analysis%20for%20a%20Destructive%20Gauge%20Using%20a%20Split%20Design.pdf)
- C02: PDF p8 operator/cutter assignment; p9 Repeat Measures Discussion, Fig. 2.6 rows 1-6 only.
- Recorded PDF SHA-256: `2bcd966891e949502d879fe495440267cbe45f823234ff7bc888871a5bf95e7d`.

Page numbers refer to PDF file order; H uses the 60-page author manuscript. Links, locations and hashes are inherited from the 2026-09-20 source review; this translation did not download or re-audit the sources. Source J is an industrial case report, with no publication year or DOI established in the existing review. N refers specifically to the second, batch-process scenario.

## 2. Case inputs

Each claim is evaluated for its stated treatment and local counting scope. Treatment-unit counts do not establish independent response errors. Source locations, targets, scope filters and claim numbers were prepared manually. The labels are `supported`, `inconsistent` and `insufficient`, conditional on the supplied evidence. Candidate omission is a separate engineering outcome.

### D01: UHPC mixing and destructive testing

Source U. Scope: The 28-day group from the same mixing operation and the same curing regimen.

> Mixer speed and duration are set for each mixing operation. Mechanical testing includes 24-hour and 28-day groups, with three prisms in each group. This check covers only the 28-day group from the same mixing operation and the same curing regimen: the three prisms each undergo flexural testing, followed by compression testing of the two half-prisms produced from each prism.

- **D01** — Target: mixing conditions. Claim: The six half-prisms in this group provide six independent mixing replicates to which these mixing conditions were applied.
- **D01-S** — Target: mixing conditions. Claim: This group comes from one mixing operation; its three prisms and six half-prisms do not increase the number of mixing operations.
- **D01-O** — Target: mixing conditions. Claim: The six half-prisms in this group provide six independent mixing replicates to which these mixing conditions were applied.

The code path needs no unit choices. The historical candidate set was: one batch from one mixing operation, one intact prism, one half-prism, other, not stated. D01-O removes the mixing-batch option from a simulated branch. It checks candidate completion or transfer without making a model call.

### D02: A complete build and specimen replicates

Source A. Scope: Table 2: E8-3 geometry, Z orientation, specimens 7, 8, and 9.

> The study manufactured specimens with different geometries and orientations in a single complete EB-PBF build. In Table 2, the E8-3 row with Z orientation lists specimens 7, 8, and 9 under Replicate 1, 2, and 3, respectively.

- **D02** — Target: complete manufacturing process. Claim: These three specimens represent three independent repetitions of the complete manufacturing process.
- **D02-S** — Target: complete manufacturing process. Claim: These are three specimens within one build.

D02-S is the previously unnumbered supported variant. The target is repetition of the complete manufacturing process; geometry and orientation treatments are outside this claim. Historical unit choices were one complete build, one tensile specimen, other, not stated.

### D03: Water-bath temperature and treatment runs

Source U. Scope: The three prisms tested at 28 days from the batch in the water-curing branch.

> The methods record curing environment category and temperature by batch. In the water-curing branch, a water bath at a set temperature is used from demolding until day 28; an in-bath probe measures the water temperature. Mechanical testing at 28 days uses a group of three prisms from that batch. Figure 2 shows the curing equipment, including a photograph of a water bath.

- **D03** — Target: water-bath curing temperature. Claim: In the water-curing branch, these three prisms represent three independent water-bath runs in which the temperature condition was separately set and applied.

The retired candidate list included mixing batch, individual prism, one temperature-controlled water-bath run, other and not stated. A single run is no longer treated as the uniquely correct atomic answer. The reference separately records treatment level, run boundary and specimen assignment. No source-verified supported/inconsistent paired variant has been added.

### C01: Factor-specific units in electroplating

Source N. Scope: One fixed temperature-concentration combination.

> Four copper strips enter a single treatment together. Temperature and concentration apply jointly to this group; within the group, two strips are randomly assigned to low current and two to high current. Each of the four temperature-concentration combinations is run once. The source explicitly defines a single copper strip as the experimental unit for current (subplot experimental unit), and the group of four strips treated together as the unit for temperature and concentration (whole-plot experimental unit).

- **C01-T** — Target: temperature and concentration. Claim: This combination has four independent group-level treatment units.
- **C01-A** — Target: current. Claim: Within this combination, low current is assigned to two strip-level treatment units.

This is the second NIST execution scenario: a batch process with four strips treated together. The source provides the whole-plot and subplot unit definitions directly. No unit choices are needed.

### H01: Laser settings and heat treatment in a combinatorial specimen

Source H. Scope: The whole specimen treated at 870°C and default-setting columns 1, 10, 16, 19, and 24.

> A continuous nickel-alloy combinatorial specimen contains multiple column regions, each processed at a specified laser power and scan speed. Columns 1, 10, 16, 19, and 24 in Table 2 use the same default settings. The study produced multiple specimens of the same geometry; one whole specimen received stress-relief treatment at 800°C and another at 870°C. The authors explicitly describe a split-plot design because each combinatorial specimen was fabricated and stress-relieved as a continuous whole. Multiple indentation measurements were then taken within each column region.
> This check covers only the combinatorial specimen treated at 870°C and the default-setting columns listed above; other specimens and columns are excluded.

- **H01-L** — Target: default laser settings. Claim: The default laser settings have five column-level application units within this specimen.
- **H01-T** — Target: whole-specimen heat treatment. Claim: The same five columns provide five separate repetitions of the 870°C whole-specimen heat treatment.

H01-L concerns column-level application units only. These are not asserted to be independent manufacturing batches, independent random samples or independent measurement errors. H01-T counts the selected whole treated specimen, without inferring the number of furnace runs across the study. Historical unit choices were whole combinatorial specimen, column region, individual indentation measurement, other and not stated.

### C02: Wear-scar generation and scan records

Source J. Scope: Figure 2.6, rows 1-6: 1A/O1 and 1B/O3, pooling operators; exclude 1C and 1D.

> Wear scars are generated at different circumferential positions on a cutter. Each scar results from a machining operation performed by one operator, who then scans that scar three times. The first character of PART ID identifies the cutter, and the second identifies the wear scar. From Figure 2.6, this check selects six scan records for cutter 1, PART IDs 1A and 1B: 1A, 1A, and 1A are assigned to operator O1; 1B, 1B, and 1B are assigned to operator O3; 1C and 1D are excluded.

- **C02** — Target: wear-scar generation. Claim: The six selected records correspond to six wear-scar generation operations in total.
- **C02-S** — Target: wear-scar generation. Claim: The six selected records correspond to two wear-scar generation operations in total.

C02-S is the previously unnumbered supported variant. Both claims pool O1 and O3 within rows 1-6; cutter 1 also has 1C and 1D. If the scope is restricted to O1, the count is one and both the six-operation and two-operation claims are inconsistent. The earlier O1/two-operation supported label remains withdrawn. This correction concerns transcription and scope, not model judgment.

## 3. References and execution

| Item | Reviewed relation | Count and result |
|---|---|---|
| D01 | Six half-prisms → three prisms → one mixing operation, same curing regimen and 28-day group | 1; inconsistent with 6 |
| D01-S | Same relation and scope | 1 mixing operation, 3 prisms, 6 half-prisms; supported |
| D01-O | Mixing unit is identifiable but absent from the simulated candidate list | Simulated `other`; stop that branch's counting and complete candidates or transfer; normal code path still finishes |
| D02 | Specimens 7, 8, 9 share one complete build | 1; inconsistent with 3 |
| D02-S | Same relation | 1 build and 3 specimens; supported |
| D03 | Water-bath temperature-control level is identified; run boundaries and specimen assignment are not stated | Unknown; insufficient; request run boundaries and specimen-to-run records |
| C01-T | The four-strip group at fixed temperature/concentration is one whole-plot experimental unit | 1; inconsistent with 4 |
| C01-A | Two low-current strips are two subplot experimental units | 2; supported |
| H01-L | The default laser settings apply to the five selected column regions | 5; supported |
| H01-T | The five columns belong to one whole treated specimen | 1; inconsistent with 5 separate whole-specimen treatments |
| C02 | Selected 1A/O1 and 1B/O3 scan rows map to two wear-scar generation events | 2; inconsistent with 6 |
| C02-S | Same selected rows and pooled operators | 2; supported |

All counts, filtering, deduplication, comparisons and final labels are computed in code. The English text baseline reads the same prepared passages a model branch would receive. The manual relation oracle bypasses text processing and is reported separately. The current passages leave no residual model question; H01-L/T are therefore program controls.

## 4. Inherited human review and translation check

The user confirmed the D02, H01 and corrected C02 tables on 2026-09-20. This confirmation covers specimens 7/8/9, columns 1/10/16/19/24, and the six selected 1A/O1 and 1B/O3 rows. The user has approved the associated unit and label judgments.

The user separately confirmed:

- **D01/D01-S:** the same mixing operation, same curing regimen and 28-day group; the three prisms and six resulting half-prisms belong to that one mixing operation. Labels: inconsistent and supported.
- **D03:** the visible material identifies water-bath temperature control but does not establish run boundaries or specimen assignment. Count unknown; insufficient; request the missing records.
- **C01-T/C01-A:** in NIST's second batch-process scenario, the fixed temperature/concentration group is one whole-plot experimental unit; its two low-current strips are two subplot experimental units. Labels: inconsistent and supported.

The user has approved the source review for all six groups, including enlarged tables and figures. The English translation preserves the complete evidence explanations, operator assignments, local scope and compound claims. [LANGUAGE_MIGRATION.json](LANGUAGE_MIGRATION.json) records this revision; the numeric scope fields and reference file remain unchanged. D01-O remains an engineering fixture and requires no scientific source signoff.

Two source issues remain bounded by the current questions. H's author manuscript gives 295 W in the Table 1 description and 285 W in Table 2; the selected column IDs avoid reliance on either value. The final published version was not verified in the earlier review because access was limited. For U, the reviewed methods, figures and public README did not provide specimen-to-water-bath-run mappings; specific CSV/XLSX records and laboratory logs remain unaudited. The insufficient answer concerns the supplied evidence, not the existence of replication in the actual study.

## 5. Checks and resources

The original [check_counts.py](check_counts.py) contains eleven oracle-based counting checks. The English [test_preflight.py](test_preflight.py) additionally checks text processing, translation invariants, scope handling, budget continuity and the offline entry point. Engineering perturbations do not add scientific cases.

Current English outputs: [results](../../../../s2-nonbio-preflight-en-v1/SUMMARY.md), [scores](../../../../s2-nonbio-preflight-en-v1/scores.json), [call matrix](../../../../s2-nonbio-preflight-en-v1/call_matrix.json). The Chinese v1/v2 results remain historical; they are not counted as English evaluations.

Human preparation, translation/review, local compute costs and full-workflow time remain unmeasured. The reviewed cases remain development data.
