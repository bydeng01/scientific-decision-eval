# Document development pilot

32 controlled fictional packets, four templates, eight predicate combinations per template.
Every case is development data. Template-related examples are not independent draws from a deployment population.
No thresholds were calibrated or certified on this batch. Probabilities are model-generated scores.

| Model | Mode | Valid / attempted | Terminal errors | Score | Brier error score | Error AUROC |
|---|---|---:|---:|---|---:|---:|
| openai/gpt-4.1-mini | nodes | 32/32 | 9 | uniform | 0.25844 | 0.5169 |
| openai/gpt-4.1-mini | nodes | 32/32 | 9 | graph_certificate | 0.25812 | 0.5362 |
| openai/gpt-4.1-mini | nodes | 32/32 | 9 | graph_independent | 0.25977 | 0.5362 |
| openai/gpt-4.1-mini | direct | 32/32 | 6 | direct | 0.18750 | 0.5000 |
| anthropic/claude-haiku-4.5 | nodes | 32/32 | 8 | uniform | 0.25039 | 0.4583 |
| anthropic/claude-haiku-4.5 | nodes | 32/32 | 8 | graph_certificate | 0.25000 | 0.5000 |
| anthropic/claude-haiku-4.5 | nodes | 32/32 | 8 | graph_independent | 0.25000 | 0.5000 |
| anthropic/claude-haiku-4.5 | direct | 32/32 | 9 | direct | 0.26875 | 0.6812 |

Reported API cost: $0.064198. Budget accounting including unknown-cost attempts: $0.064198 of $1.

Undefined error AUROC means this batch contains only correct or only incorrect predictions; it cannot establish error discrimination.
Brier values for union/product scores are diagnostics, not a claim that these scores are calibrated probabilities.
A zero-error development batch is not evidence that the deployment error is zero. Even 32 independent zero-error observations for a fixed policy would have a one-sided 95% upper bound of 0.0894; the template design here does not justify that binomial interval.
