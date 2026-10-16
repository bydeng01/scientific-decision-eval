# S2 non-biological development preflight: English results

6 groups, 12 items, 5 sources; 11 scientific claims and 1 engineering routing check. Reviewed development data.

Input revision: s2-nonbio-en-v1. These results come from a fresh run on the English passages. Earlier Chinese runs remain historical.

| Item | Route | Count | Label | New model calls |
|---|---|---:|---|---:|
| D01 | rule | 1 | inconsistent | 0 |
| D01-S | rule | 1 | supported | 0 |
| D01-O | rule_plus_engineering_simulation | 1 | inconsistent | 0 |
| D02 | rule | 1 | inconsistent | 0 |
| D02-S | rule | 1 | supported | 0 |
| D03 | rule | unknown | insufficient | 0 |
| C01-T | rule | 1 | inconsistent | 0 |
| C01-A | rule | 2 | supported | 0 |
| H01-L | rule | 5 | supported | 0 |
| H01-T | rule | 1 | inconsistent | 0 |
| C02 | rule | 2 | inconsistent | 0 |
| C02-S | rule | 2 | supported | 0 |

D01-O's table entry is the normal rule result. Its separate candidate-omission simulation returns other, stops downstream counting in that branch, and requests candidate completion or transfer.

Text rules: relation 11/11, count 11/11, label 11/11, action 11/11.
Human relation oracle: count 11/11, label 11/11. See scores.json for item-level results.
D03 scores treatment level, run boundary and specimen assignment separately. The latter two are not stated; the run count remains unknown.

Offline scoring checks passed: True. Call-matrix status: no_model_branch.
Model-call, retry and fallback limits are all zero. Worst-case new API cost is $0; historical reported/estimated cost is $0.668041116 and the initial-stage balance is $0.331958884.

The baseline uses a finite phrase grammar developed on manually prepared English passages with supplied targets, scopes and claim numbers. Generalization to unseen sources, arbitrary-paper/PDF extraction and model quality are unmeasured.
Human source localization, transcription, translation/review and rule-development time, and local compute costs are unmeasured. Missing token, API-latency and full-workflow measurements are not recorded as zero.
Local execution timing is in resource_summary.json; it excludes earlier preparation and later record requests.
