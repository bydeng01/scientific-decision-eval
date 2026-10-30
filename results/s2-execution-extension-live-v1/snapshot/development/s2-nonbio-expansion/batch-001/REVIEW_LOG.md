# S2 non-biological review decisions

The ten problems and eighteen questions were reviewed and accepted by the author within the scopes below. Structured decisions, reference options, and accepted question hashes are in [review_decisions.json](review_decisions.json).

## Per-question status

| Problem | Problem status | Question | Question status | Explicit author decision |
|---|---|---|---|---|
| E001 | author_reviewed | E001-Q01 | author_reviewed | UR001 |
| E001 | author_reviewed | E001-Q02 | author_reviewed | UR001 |
| E002 | author_reviewed | E002-Q01 | author_reviewed | UR002 |
| E002 | author_reviewed | E002-Q02 | author_reviewed | UR002 |
| E003 | author_reviewed | E003-Q01 | author_reviewed | UR003 |
| E004 | author_reviewed | E004-Q01 | author_reviewed | UR004 |
| E004 | author_reviewed | E004-Q02 | author_reviewed | UR004 |
| E005 | author_reviewed | E005-Q01 | author_reviewed | UR005 |
| E005 | author_reviewed | E005-Q02 | author_reviewed | UR005 |
| E006 | author_reviewed | E006-Q01 | author_reviewed | UR006 |
| E006 | author_reviewed | E006-Q02 | author_reviewed | UR006 |
| E007 | author_reviewed | E007-Q01 | author_reviewed | UR007 |
| E007 | author_reviewed | E007-Q02 | author_reviewed | UR007 |
| E008 | author_reviewed | E008-Q01 | author_reviewed | UR008 |
| E009 | author_reviewed | E009-Q01 | author_reviewed | UR009 |
| E009 | author_reviewed | E009-Q02 | author_reviewed | UR009 |
| E010 | author_reviewed | E010-Q01 | author_reviewed | UR010 |
| E010 | author_reviewed | E010-Q02 | author_reviewed | UR010 |

## Retained source limitations and scope boundaries

- E005: Table 3 and the Figure 11 caption report a 30 MPa step, while the author-released Figure 11 plotting file saves a staircase sequence with 16.25 MPa adjacent spacing. No public correction or experimental log was found to determine whether these represent the same quantity. Numerical next-stress inference for the executed experiment remains unresolved; the offline 325 +/- 30 calculation checks only the reported parameter. The Choice answers remain approved in UR005-F01.
- E008: Table 1 (PDF p. 3) provides the eight factor names and low/high levels. It lists temperature levels of 750 and 800 °C, whereas Section 6 describes each cycle as operating at 800 °C. This discrepancy remains unresolved for reconstructing physical operating conditions. The present judgment concerns equality of the eight-factor coded settings in Table 7, not chemical equivalence outside that design.
- E010: The two source plots label opposite mountain ranges; plot colors cannot be merged without target identity.
- E010: Calendar and wind-criterion discrepancies are retained in sources.json but do not conflict with the selected allocation judgment.
- E010: Per-EU physical exposure is not adjudicated here.

## Accepted scopes

### UR001 — E001

- Normalized the D/E/F stage to annealed in current adaptations and source annotations.
- Clarified the evaluation-only outcome as 64 implant–anneal combinations, each corresponding to one wafer observation.

### UR002 — E002

- Clarified the evaluation-only downstream role and inference boundary: controller-mode application boundaries do not establish independent applications.

### UR003 — E003

The eight Figure 2 cycles represent a single catalyst reuse history, not eight independent catalyst preparations or replications.

- Clarified the evaluation-only inference boundary: recovered carryover denotes procedural reuse and implies neither complete material conservation nor identical catalyst composition across cycles.

### UR004 — E004

Mixed reuse-history feedstock in the build-8-and-later top-up regime, with incomplete lot identity, mixture fraction, and prior-build assignment for build 8. History streams are distinct from original powder lots; the bulk R index does not establish exact genealogy. The downstream exact_parent_lot_count remains null and complete_assignment_available remains false.

### UR005 — E005

Regular staircase outcome-dependent stress assignment to a new specimen. The accepted 295 MPa and 355 MPa values are protocol-derived, not reconstructed observations. Random specimen extraction and protocol order do not establish independent stress randomization; allocation dependence does not establish specimen failure correlation. The fixed-stress observed replicate count remains null.

### UR006 — E006

The N1000 paired-fixed subset has 100 paired realizations, 200 executions, and 100 pair-level values. Phase reversal relates the initial fields of two separate executions and does not constitute an independent second initial-condition draw or imply perfectly anticorrelated evolved observables. The accepted pair-average aggregation does not establish an effective sample size for every observable.

### UR007 — E007

The 100 LENS2 members comprise 50 original and 50 SMBB protocol members under the official initialization mapping. The SMBB half includes other documented implementation changes, so the between-half contrast does not isolate smoothing alone. Initialization dates are not forcing treatments. Reported small or undetected impacts do not establish identical implementations or a single-variable causal contrast. The proposed references and downstream schema are unchanged.

- The revised E007-Q02 rationale distinguishes additional implementation changes from the source-reported evaluations of their impacts.

### UR008 — E008

Exact equality of all eight coded factor settings across separate executions defines complete treatment replication. The author accepted 20 runs, 18 distinct settings, repeated table-column groups [11,12] and [13,14], 16 singleton settings, and two pure-error degrees of freedom. Table positions do not establish execution order, sign complementarity is not treatment equality, response differences do not negate treatment equality, and the source variance-related degrees of freedom are not all pure error. The source note now acknowledges Table 1 and retains the unresolved temperature-description discrepancy for physical-condition reconstruction.

- The corrected source note identifies Table 1 as the factor dictionary and retains the unresolved temperature discrepancy.

### UR009 — E009

The author accepted the shared DC-voltage reference-calibration contribution and the Cal-Lab bracketing average, with two compared laboratory results across three calibration visits. The shared covariance subtraction remains 2*u_B(std_DCV)^2 and the exact effective replication count remains null. S2 inclusion is approved as a counting/dependence judgment about shared reference provenance, without expansion to the full uncertainty budget, other electrical quantities, effective sample size, or perfect correlation.

### UR010 — E010

The author accepted complementary assignment within each four-hour EU and the distinction between assigned-unseeded and physical exposure. The downstream outcome retains 154 original EUs, 118 quality-controlled EUs and joint assignment events, 236 EU-by-range records, and a false independent-range-draws claim. Cross-range contamination does not redefine assigned treatment/control; the 21 transport cases and 18 modeled enhancement cases do not supply per-EU exposure labels. S2 inclusion is approved without effect-size, p-value, or causal conclusions.

## Follow-up review

UR005-F01 retains E005-Q01 = `response_adaptive` and E005-Q02 = `new_specimen`; the unresolved source discrepancy in stress-step size does not change these accepted Choices.

## Source qualification, 2026-09-21

E010 retains 118 as the author-reported number of quality-controlled EUs and records the one-case difference between Table 1 generator-exclusion cells and margins. Reference answers are unchanged. [source_revisions.json](source_revisions.json) records the exact input edits and before/after hashes.
