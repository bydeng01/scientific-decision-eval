# Drag mechanism development results

Development cases only. No OpenAI or Anthropic comparison has been run by this runner.

| Method | Round | n | Accuracy | Brier | Mean TV | Excluded true law | Confident wrong |
|---|---|---:|---:|---:|---:|---:|---:|
| reference | 1 | 12 | 0.500 | 0.5042 | 0.0000 | 0 | 0 |
| reference | 2 | 12 | 1.000 | 0.0000 | 0.0000 | 0 | 0 |
| uniform | 1 | 12 | 0.333 | 0.6667 | 0.3159 | 0 | 0 |
| uniform | 2 | 12 | 0.333 | 0.6667 | 0.6663 | 0 | 0 |
| jev | 1 | 2 | 0.000 | 0.8381 | 0.2481 | 0 | 0 |
| jev | 2 | 1 | 0.000 | 1.2566 | 0.8900 | 0 | 0 |

Jev task responses completed: 3/24. This partial run does not provide the complete development comparison.
Empty-data control TV: 0.5067.

API attempts: 7.
Conservative budget charge: USD 0.2357.
Reported cost (known entries only): USD 0.00023512.
Attempts with unknown billed cost: 2.
