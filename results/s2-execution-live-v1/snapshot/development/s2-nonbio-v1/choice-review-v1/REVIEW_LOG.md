# S2 Choice review log

The author reviewed the fifteen Choice definitions and reference mappings on 2026-09-24. Approval covers the prepared review as a whole; independent multi-reviewer annotation was not performed. Source-review scope is recorded in [ALL_CASES_REVIEW.md](../ALL_CASES_REVIEW.md), section 4.

## Per-question status

| Question ID | Author review | Reference option | Decision record |
|---|---|---|---|
| D01.unit | Accepted with revisions | `mixing_batch` | [Accepted review](#accepted-review) |
| D01.membership | Accepted with revisions | `shared` | [Accepted review](#accepted-review) |
| D01-O.omitted_unit | Accepted with revisions | `other` | [Accepted review](#accepted-review) |
| D02.unit | Accepted with revisions | `build` | [Accepted review](#accepted-review) |
| D02.membership | Accepted with revisions | `shared` | [Accepted review](#accepted-review) |
| D03.treatment_level | Accepted with revisions | `water_bath_temperature_control` | [Accepted review](#accepted-review) |
| D03.run_boundary | Accepted with revisions | `not_stated` | [Accepted review](#accepted-review) |
| D03.specimen_assignment | Accepted with revisions | `not_stated` | [Accepted review](#accepted-review) |
| C01-T.unit | Accepted with revisions | `whole_plot_group` | [Accepted review](#accepted-review) |
| C01-A.unit | Accepted with revisions | `strip` | [Accepted review](#accepted-review) |
| H01-L.unit | Accepted with revisions | `column_region` | [Accepted review](#accepted-review) |
| H01-T.unit | Accepted with revisions | `whole_specimen` | [Accepted review](#accepted-review) |
| H01-T.membership | Accepted with revisions | `shared` | [Accepted review](#accepted-review) |
| C02.unit | Accepted with revisions | `wear_event` | [Accepted review](#accepted-review) |
| C02.identifier | Accepted with revisions | `part_id` | [Accepted review](#accepted-review) |

## Accepted review

Revision: `s2-choice-review-v1-r2`.

The review used the supplied evidence and the inherited source review in `ALL_CASES_REVIEW.md`, section 4. No new wording required a change to the scientific scope or revealed a source contradiction. The C02 identifier revision resolves an ambiguity in the Choice question using the identifier definition already supplied; it does not require a new source confirmation.

### Per-group decisions

**D01**

- `D01.unit`: Accepted for distinguishing mixing-operation units from downstream test specimens. Speed and duration have one stated application level. Added an explicit conflict outcome and narrowed missing-information handling. Reference: `mixing_batch` (unchanged).
- `D01.membership`: Accepted for establishing whether the selected prisms represent shared or separate mixing operations. Named prisms explicitly and distinguished a known mixed pattern from unresolved membership and conflicting records. Reference: `shared` (unchanged).
- `D01-O.omitted_unit`: Accepted as an engineering candidate-omission check. The mixing-batch alternative remains absent; other remains the reference. Added conflicting without changing the active omission fixture. Reference: `other` (unchanged).

**D02**

- `D02.unit`: Accepted for distinguishing a complete EB-PBF build from a tensile specimen within that build. The target remains the complete process in the supplied passage. Added explicit conflict handling. Reference: `build` (unchanged).
- `D02.membership`: Accepted for determining whether specimens 7, 8, and 9 share a build. The table heading Replicate does not establish repeated builds. Named the selected specimens and separated mixed membership, missing information, and conflict. Reference: `shared` (unchanged).

**D03**

- `D03.treatment_level`: Accepted for locating physical temperature control at the water bath. This answer identifies neither a run count nor run boundaries. Added explicit conflict handling. Reference: `water_bath_temperature_control` (unchanged).
- `D03.run_boundary`: Accepted after distinguishing complete, partial, absent, and conflicting run identification. The instruction asks one coverage judgment. A bath photograph, equipment identity, or curing period alone does not distinguish run executions. Reference: `not_stated` (unchanged).
- `D03.specimen_assignment`: Accepted after requiring assignments to identified run executions and making the no-assignment outcome exclude conflict. Complete and partial assignment remain separate. No specimen-to-run assignment is supplied. Reference: `not_stated` (unchanged).

**C01**

- `C01-T.unit`: Accepted for the source-defined unit of jointly applied temperature and concentration in the second NIST batch-process scenario. Both factors share one group-level unit here. Added explicit conflict handling. Reference: `whole_plot_group` (unchanged).
- `C01-A.unit`: Accepted for the source-defined current unit. Code counts the two low-current strips within the fixed temperature-concentration combination. Added explicit conflict handling. Reference: `strip` (unchanged).

**H01**

- `H01-L.unit`: Accepted for distinguishing column-level laser-parameter application from whole-specimen treatment and indentation measurements. No independent manufacturing, sampling, or measurement-error claim is introduced. Added explicit conflict handling. Reference: `column_region` (unchanged).
- `H01-T.unit`: Accepted for identifying the whole continuous specimen as the stress-relief application unit. The question does not identify or count furnace runs. Added explicit conflict handling. Reference: `whole_specimen` (unchanged).
- `H01-T.membership`: Accepted for relating the five selected default-setting columns to the selected 870-degree whole specimen. Named column regions explicitly and separated mixed membership, missing information, and conflict. Reference: `shared` (unchanged).

**C02**

- `C02.unit`: Accepted for distinguishing scar-generating machining events from scans and cutter-level pooling. Code retains the corrected six-row scope and counts two events. Added explicit conflict handling. Reference: `wear_event` (unchanged).
- `C02.identifier`: Accepted after asking which identifier encodes both cutter and scar identity and adding the second-character alternative. Within the fixed cutter-1 scope, scar character alone also separates A and B; the original wording did not make the full-ID requirement unique. The revised question resolves that ambiguity without changing selected rows or counts. Reference: `part_id` (unchanged).

### Option changes and reference handling

Every question now gives conflict handling precedence explicitly in its model-facing instructions. Where absent, `conflicting` was added; the existing `conflicting_assignment` remains specific to D03 specimen assignments. Missing or ambiguous evidence no longer absorbs an explicit unresolved contradiction. `other` remains a known answer outside the substantive alternatives.

D03 retains three separate questions. `partial_identification` was added to the run-boundary question. Both run identification and specimen assignment distinguish complete, partial, absent, and conflicting information. The reference remains an identified water-bath control level with no established run identity or specimen-to-run assignment. No single water-bath run has been inferred.

C02 retains rows 1-6, with 1A/O1 and 1B/O3 pooled and 1C/1D excluded. `scar_character` was added to `C02.identifier`. Within cutter 1, A/B alone would yield the same two groups, so the revised question explicitly asks for the identifier encoding both cutter and scar identity. The complete PART ID answers that question. This is a data-identity check that supports event counting, not evidence of a difficult scientific inference.

All original option IDs were retained. The exact option sets grew where noted; D01-O still omits `mixing_batch` and retains reference `other`. All 15 reference option IDs and all 12 existing case outcomes are unchanged. Reference rationales and review notes are stored only in evaluation files and review documentation.

### Scientific value and remaining boundaries

The fourteen questions attached to scientific claims check treatment level, hierarchical membership, run identifiability, assignment completeness, or event identity. These judgments help prevent repeated measurements or subsamples from being counted as repeated treatment operations. D01-O remains an engineering routing check. The prepared passages make most answers explicit, and the current rules already resolve them. These questions establish basic workflow checks, not model necessity or scientific-reasoning difficulty.

Counts, arithmetic, filtering, deduplication, numerical comparisons, and final labels stay in code. A membership-pattern answer alone does not generally give a full assignment map or an exact count. `partly_shared` may be established from a shared pair and a known different parent even if other assignments are missing; a later counting stage still needs enough records for its own requested quantity. A conflict response requires evidence resolution rather than acceptance of one incompatible record. No routing for these new options has been activated.

The H-source 295/285 W discrepancy remains outside the selected column-ID questions. The final published H version remains unverified in the inherited source review. Additional U run-mapping files and laboratory records remain unaudited. These recorded limits do not change the supplied-evidence reference answers.

No unresolved wording or mapping issues were identified within the supplied scope after revision. The dataset contains twelve items with fifteen question definitions. The review does not change the offline runner.
