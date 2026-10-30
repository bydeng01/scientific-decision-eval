# Matched drag diagnostic

Exposed development data: two systems (H1 and H2), four accumulated-data states.
No H3-generated system was attempted. These cases are not a population benchmark.

Astra uses a 2048-token output cap; Sonnet uses the separate 8192-token condition.
Sonnet's first 2048-token trajectory attempt ended at max_tokens without probabilities.
That failure is retained in carry_in.jsonl. The table uses the new condition only.

## Individual responses

All vectors below are H1 / H2 / H3, displayed to four decimals; JSON retains full precision.
An asterisk marks a native-invalid vector.

| State | True law | Reference | Jev raw | Astra | Sonnet |
|---|---|---|---|---|---|
| dev-00-r1 | H1 | 0.5523 / 0.0082 / 0.4395 | 0.2300 / 0.2400 / 0.5300 | 0.5523 / 0.0082 / 0.4395 | 0.5500 / 0.0200 / 0.4300 |
| dev-00-r2 | H1 | 1.0000 / 0.0000 / 0.0000 | 0.1100 / 0.2600 / 0.6300 | 1.0000 / 0.0000 / 0.0000 | 0.9700 / 0.0050 / 0.0250 |
| dev-01-r1 | H2 | 0.3900 / 0.3639 / 0.2461 | 0.2800 / 0.3000 / 0.4200 | 0.3900 / 0.3639 / 0.2461 | 0.3900 / 0.3600 / 0.2500 |
| dev-01-r2 | H2 | 0.0000 / 0.9993 / 0.0007 | 0.1100 / 0.3300 / 0.5500 * | 0.0000 / 0.9993 / 0.0007 | max_tokens (8192) |

## Probability precision

Native validity is unchanged: Jev dev-01-r2 sums to 0.99 and is invalid.
The following bounds assume independent ±0.005 rounding intervals intersected
with the simplex. This assumption is not a verified vendor precision policy.

| State | Derived sensitivity vector | Minimum possible TV to reference |
|---|---|---:|
| empty-prior | 0.1100 / 0.0500 / 0.8400 | 0.501667 |
| dev-00-r1 | 0.2300 / 0.2400 / 0.5300 | 0.317327 |
| dev-00-r2 | 0.1100 / 0.2600 / 0.6300 | 0.885000 |
| dev-01-r1 | 0.2800 / 0.3000 / 0.4200 | 0.168928 |
| dev-01-r2 | 0.1133 / 0.3333 / 0.5533 | 0.664329 |

## Native scores on common valid states

Common states: dev-00-r1, dev-00-r2, dev-01-r1.

| Method | n | Accuracy | Brier | Mean TV | Mean retained size |
|---|---:|---:|---:|---:|---:|
| reference | 3 | 0.667 | 0.336945 | 0 | 2.00 |
| uniform | 3 | 0.667 | 0.666667 | 0.359689 | 3.00 |
| openrouter-jev native | 3 | 0.000 | 0.9776 | 0.462085 | 3.00 |
| openai native | 3 | 0.667 | 0.336984 | 2.22034e-05 | 2.00 |
| anthropic native (8192-token condition) | 3 | 0.667 | 0.33785 | 0.015248 | 2.00 |

## Available states by round

Sample counts differ for native Jev. Its derived sensitivity lane is separate.

| Method | Round | n | Accuracy | Brier | Mean TV | True law excluded | Confident wrong |
|---|---|---:|---:|---:|---:|---:|---:|
| reference | 1 | 2 | 0.500 | 0.505417 | 0 | 0 | 0 |
| reference | 2 | 2 | 1.000 | 4.50399e-07 | 0 | 0 | 0 |
| uniform | 1 | 2 | 0.500 | 0.666667 | 0.2062 | 0 | 0 |
| uniform | 2 | 2 | 0.500 | 0.666667 | 0.666331 | 0 | 0 |
| openrouter-jev native | 1 | 2 | 0.000 | 0.8381 | 0.248128 | 0 | 0 |
| openrouter-jev native | 2 | 1 | 0.000 | 1.2566 | 0.89 | 0 | 0 |
| openai native | 1 | 2 | 0.500 | 0.505476 | 3.33051e-05 | 0 | 0 |
| openai native | 2 | 2 | 1.000 | 4.49704e-07 | 2.59034e-07 | 0 | 0 |
| anthropic native (8192-token condition) | 1 | 2 | 0.500 | 0.506 | 0.00787205 | 0 | 0 |
| anthropic native (8192-token condition) | 2 | 1 | 1.000 | 0.00155 | 0.03 | 0 | 0 |
| Jev rounding sensitivity | 1 | 2 | 0.000 | 0.8381 | 0.248128 | 0 | 0 |
| Jev rounding sensitivity | 2 | 2 | 0.000 | 1.01003 | 0.777998 | 0 | 0 |

## Completeness and cost

New attempts in this condition: 4/4. Cumulative distinct API attempts: 16.
Cumulative reported-plus-usage-estimated charge: USD 0.668041116.
Provider usage estimates are not reconciled invoices. Every input/output reservation
and the release of unused earlier reservations is recorded separately.

| Provider | Calls including control | Valid / attempted trajectory states | Charge USD | Mean latency s |
|---|---:|---|---:|---:|
| openrouter-jev | 5 | 3 / 4 | 0.000235116 | 0.47 |
| openai | 5 | 4 / 4 | 0.351800000 | 37.58 |
| anthropic / 2048-token condition | 2 | 0 / 1 | 0.025610000 | 9.77 |
| anthropic / sonnet-low-8192 | 4 | 3 / 4 | 0.290396000 | 55.79 |

The planned full 24-state-per-model screen remains incomplete. Its all-valid
native Jev advancement condition cannot pass with the preserved failure.
No calibration or test episodes were generated.
Sonnet dev-00-r1 was repeated once under the changed output cap; its original failure remains.
No sampling interval, rare-error guarantee, or repeat variability is estimated.
Episode-level exclusion, first-crossing counts, log loss, and exact-zero counts
are in report.json; states within a system are not independent samples.
