# Offline pilot

Exploratory finite synthetic population; no LLM or Jev calls.

20 independent development/calibration repeats per condition; 4000 calibration episodes; alpha=0.05, delta=0.05.
Population coverage and risk are enumerated exactly. Below, coverage is averaged across repeats; risk is the maximum among certified repeats. No-policy outcomes have coverage zero and undefined risk.

| Program | Errors | Dev labels | Method | Mean coverage | Max risk | Certified | Risk violations | Shift violations |
|---|---|---:|---|---:|---:|---:|---:|---:|
| all_required | independent | 512 | uniform | 0.0000 | undefined | 0/20 | 0 | 0 |
| all_required | independent | 512 | all_nodes_product | 0.0000 | undefined | 0/20 | 0 | 0 |
| all_required | independent | 512 | graph_certificate | 0.5935 | 0.0364 | 20/20 | 0 | 0 |
| all_required | independent | 512 | graph_independent | 0.6956 | 0.0423 | 20/20 | 0 | 0 |
| all_required | independent | 512 | e2e_hgb | 0.6007 | 0.0459 | 20/20 | 0 | 0 |
| all_required | independent | 512 | oracle_terminal | 0.6956 | 0.0423 | 20/20 | 0 | 0 |
| all_required | independent | 4096 | uniform | 0.0000 | undefined | 0/20 | 0 | 0 |
| all_required | independent | 4096 | all_nodes_product | 0.0000 | undefined | 0/20 | 0 | 0 |
| all_required | independent | 4096 | graph_certificate | 0.5935 | 0.0364 | 20/20 | 0 | 0 |
| all_required | independent | 4096 | graph_independent | 0.6956 | 0.0423 | 20/20 | 0 | 0 |
| all_required | independent | 4096 | e2e_hgb | 0.6840 | 0.0440 | 20/20 | 0 | 0 |
| all_required | independent | 4096 | oracle_terminal | 0.6956 | 0.0423 | 20/20 | 0 | 0 |
| all_required | shared | 512 | uniform | 0.0185 | 0.0444 | 3/20 | 0 | 1 |
| all_required | shared | 512 | all_nodes_product | 0.0241 | 0.0436 | 4/20 | 0 | 1 |
| all_required | shared | 512 | graph_certificate | 0.7083 | 0.0259 | 20/20 | 0 | 0 |
| all_required | shared | 512 | graph_independent | 0.7755 | 0.0424 | 20/20 | 0 | 8 |
| all_required | shared | 512 | e2e_hgb | 0.7907 | 0.0398 | 20/20 | 0 | 20 |
| all_required | shared | 512 | oracle_terminal | 0.8269 | 0.0440 | 20/20 | 0 | 20 |
| all_required | shared | 4096 | uniform | 0.0185 | 0.0444 | 3/20 | 0 | 1 |
| all_required | shared | 4096 | all_nodes_product | 0.0241 | 0.0436 | 4/20 | 0 | 1 |
| all_required | shared | 4096 | graph_certificate | 0.7083 | 0.0259 | 20/20 | 0 | 0 |
| all_required | shared | 4096 | graph_independent | 0.7755 | 0.0424 | 20/20 | 0 | 8 |
| all_required | shared | 4096 | e2e_hgb | 0.8194 | 0.0407 | 20/20 | 0 | 20 |
| all_required | shared | 4096 | oracle_terminal | 0.8269 | 0.0440 | 20/20 | 0 | 20 |
| routed | independent | 512 | uniform | 0.0000 | undefined | 0/20 | 0 | 0 |
| routed | independent | 512 | all_nodes_product | 0.0000 | undefined | 0/20 | 0 | 0 |
| routed | independent | 512 | graph_certificate | 0.0222 | 0.0272 | 3/20 | 0 | 0 |
| routed | independent | 512 | graph_independent | 0.0347 | 0.0289 | 5/20 | 0 | 0 |
| routed | independent | 512 | e2e_hgb | 0.0025 | 0.0256 | 1/20 | 0 | 0 |
| routed | independent | 512 | oracle_terminal | 0.0347 | 0.0289 | 5/20 | 0 | 0 |
| routed | independent | 4096 | uniform | 0.0000 | undefined | 0/20 | 0 | 0 |
| routed | independent | 4096 | all_nodes_product | 0.0000 | undefined | 0/20 | 0 | 0 |
| routed | independent | 4096 | graph_certificate | 0.0222 | 0.0272 | 3/20 | 0 | 0 |
| routed | independent | 4096 | graph_independent | 0.0347 | 0.0289 | 5/20 | 0 | 0 |
| routed | independent | 4096 | e2e_hgb | 0.0051 | 0.0349 | 1/20 | 0 | 0 |
| routed | independent | 4096 | oracle_terminal | 0.0347 | 0.0289 | 5/20 | 0 | 0 |
| routed | shared | 512 | uniform | 0.0037 | 0.0100 | 2/20 | 0 | 0 |
| routed | shared | 512 | all_nodes_product | 0.0037 | 0.0100 | 2/20 | 0 | 0 |
| routed | shared | 512 | graph_certificate | 0.1481 | 0.0125 | 20/20 | 0 | 0 |
| routed | shared | 512 | graph_independent | 0.0963 | 0.0235 | 14/20 | 0 | 0 |
| routed | shared | 512 | e2e_hgb | 0.0076 | 0.0245 | 2/20 | 0 | 2 |
| routed | shared | 512 | oracle_terminal | 0.3333 | 0.0089 | 20/20 | 0 | 20 |
| routed | shared | 4096 | uniform | 0.0037 | 0.0100 | 2/20 | 0 | 0 |
| routed | shared | 4096 | all_nodes_product | 0.0037 | 0.0100 | 2/20 | 0 | 0 |
| routed | shared | 4096 | graph_certificate | 0.1481 | 0.0125 | 20/20 | 0 | 0 |
| routed | shared | 4096 | graph_independent | 0.0963 | 0.0235 | 14/20 | 0 | 0 |
| routed | shared | 4096 | e2e_hgb | 0.3289 | 0.0367 | 20/20 | 0 | 20 |
| routed | shared | 4096 | oracle_terminal | 0.3333 | 0.0089 | 20/20 | 0 | 20 |

The oracle has access to the true terminal error distribution. The independent graph score is itself the oracle score under independent errors. Neither establishes a new algorithm.

Graph scores receive exact conditional node probabilities in this experiment. Real API scores do not satisfy that assumption by construction. Shift columns change the error dependence after calibration and are outside the guarantee. No errors in 20 repeats do not validate a 95% guarantee.

Per-action coverage/risk, candidate selections, and every repeat are retained in `runs.jsonl`.
