# S2 execution coverage

The current collection has 20 groups, 41 Choice definitions, 25 scientific claim outcomes and one engineering case. The scientific Choice denominator is 40. Its 21 source records form 18 documented source families; these family labels are not a certification of statistical independence.

| Group | Choice IDs | Route | Source IDs | Recorded source-review subset |
|---|---|---|---|---|
| D01 | D01.unit, D01.membership, D01-O.omitted_unit | Zero calls | U | Outside this subset |
| D02 | D02.unit, D02.membership | Zero calls | A | Outside this subset |
| D03 | D03.treatment_level, D03.run_boundary, D03.specimen_assignment | Zero calls | U | Outside this subset |
| C01 | C01-T.unit, C01-A.unit | Zero calls | N | Outside this subset |
| H01 | H01-L.unit, H01-T.unit, H01-T.membership | Zero calls | H | Outside this subset |
| C02 | C02.unit, C02.identifier | Zero calls | J | Outside this subset |
| E001 | E001-Q01, E001-Q02 | Zero calls | N-STRIP | Outside this subset |
| E002 | E002-Q01, E002-Q02 | Zero calls | WIND-2021 | Yes |
| E003 | E003-Q01 | Zero calls | CAT-2020 | Yes |
| E004 | E004-Q01, E004-Q02 | Model semantics + code | POW-2023 | Outside this subset |
| E005 | E005-Q01, E005-Q02 | Model semantics + code | FAT-2022 | Outside this subset |
| E006 | E006-Q01, E006-Q02 | Model semantics + code | COS-2018 | Yes |
| E007 | E007-Q01, E007-Q02 | Model semantics + code | LENS2-DOC | Yes |
| E008 | E008-Q01 | Zero calls | FOLD-2025, N-FOLD | Yes |
| E009 | E009-Q01, E009-Q02 | Model semantics + code | MET-2016 | Outside this subset |
| E010 | E010-Q01, E010-Q02 | Model semantics + code | CLOUD-2018, CLOUD-2014 | Yes |
| B001 | B001-Q01, B001-Q02 | Model semantics + code | BIO-EXP-2012 | Yes |
| B002 | B002-Q01, B002-Q02 | Model semantics + code | BIO-LD-1943 | Yes |
| B003 | B003-Q01, B003-Q02 | Model semantics + code | BIO-RNA-2015 | Yes |
| B004 | B004-Q01, B004-Q02 | Model semantics + code | BIO-TYR-2014 | Yes |

The case review logs record preparation, user acceptance, and source-review scope. The recorded source-review subset covers 10 groups and 18 Choices within the full collection. Of those 18 Choices, four use code and fourteen use models in this execution configuration. The saved field `recent_independent_review` identifies this historical subset; it does not count reviewers or establish independent multi-reviewer annotation. Approval of prepared review content is recorded separately as user approval.

D01-O is the candidate-omission engineering fixture. It shares D01 evidence and adds neither a scientific group nor a scientific Choice. Paired original claims reuse their linked questions rather than duplicating calls.

`prepare` writes `inventory.json` for routing and source coverage and `evaluation_only/mapping.json` for the complete join between each input JSON pointer, reference pointer, accepted option, claim IDs and reference downstream output. Every reference remains in the evaluation-only path.
