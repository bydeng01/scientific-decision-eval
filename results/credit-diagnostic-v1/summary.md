# Targeted credit diagnostic

These eight cases were selected after inspecting document-v1. They are exposed development cases.

| Model | Case | Exact transcription | Code credits | Gold new_ok | Original error | Revised error |
|---|---|---|---:|---:|---:|---:|
| openai/gpt-4.1-mini | plain-0 | True | 23 | 0 | 1 | 0 |
| anthropic/claude-haiku-4.5 | plain-0 | True | 23 | 0 | 1 | 0 |
| openai/gpt-4.1-mini | plain-1 | True | 24 | 1 | 0 | 0 |
| anthropic/claude-haiku-4.5 | plain-1 | True | 24 | 1 | 0 | 0 |
| openai/gpt-4.1-mini | plain-7 | True | 24 | 1 | 0 | 0 |
| anthropic/claude-haiku-4.5 | plain-7 | True | 24 | 1 | 0 | 0 |
| openai/gpt-4.1-mini | superseded-0 | True | 23 | 0 | 1 | 1 |
| anthropic/claude-haiku-4.5 | superseded-0 | True | 23 | 0 | 1 | 0 |
| openai/gpt-4.1-mini | superseded-5 | True | 24 | 1 | 1 | 1 |
| anthropic/claude-haiku-4.5 | superseded-5 | True | 24 | 1 | 0 | 0 |
| openai/gpt-4.1-mini | other_applicant-0 | True | 23 | 0 | 1 | 0 |
| anthropic/claude-haiku-4.5 | other_applicant-0 | True | 23 | 0 | 1 | 0 |
| openai/gpt-4.1-mini | credit_exclusions-0 | True | 23 | 0 | 1 | 0 |
| anthropic/claude-haiku-4.5 | credit_exclusions-0 | True | 23 | 0 | 1 | 0 |
| openai/gpt-4.1-mini | credit_exclusions-1 | True | 24 | 1 | 0 | 0 |
| anthropic/claude-haiku-4.5 | credit_exclusions-1 | True | 24 | 1 | 0 | 0 |

Diagnostic accounted cost: $0.010543; total including original batch: $0.074741.
Any reduction here concerns an exposed, selected subset. The unchanged original route/renewal predictions can still cause terminal errors. No risk certificate is claimed.
