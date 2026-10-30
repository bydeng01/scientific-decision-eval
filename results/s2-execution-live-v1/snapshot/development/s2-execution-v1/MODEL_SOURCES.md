# Model and interface sources

Checked 2026-09-21 through the public official pages below. This was documentation retrieval, not authenticated inference. `config.json` records the executable choices and price snapshot.

| Decision | Official source and use |
|---|---|
| Jev interface | [OpenRouter Decisions API](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-questions-and-answers-request): `POST /api/alpha/decisions`, `model/state/questions`, typed Choice answers, usage and reported cost. Its response example names `typesafe/jev-1.13-20260917`; this is the accepted returned ID for the prepared run. |
| Jev price | [Jev 1.13 model page](https://openrouter.ai/typesafe/jev-1.13): $0.042/M input and $0/M output, 32K context. The requested named route is `typesafe/jev-1.13`. |
| Jev workload division | [Jev 1.13 usage guidance](https://docs.typesafe.ai/model-jaggedness/jev-1.13): counting and mathematical comparisons belong in code; semantic questions use explicit scoped options. |
| Grouped Choices | [TypeSafe Choice documentation](https://docs.typesafe.ai/primitives/choice): submit questions sharing a state together; native confidence summarizes the option distribution. This supports one request for each two-Choice residual group. |
| Cost-sensitive comparator | [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna): named model, medium effort, structured outputs; $0.20/M input, $0.02/M cached input and $1.20/M output. |
| Intermediate comparator | [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra): named model and supported medium effort; $2/M input, $0.20/M cached input and $12/M output. |
| GPT-5.6 frontier comparator | [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol): use the explicit `gpt-5.6-sol` ID; $4/M input, $0.40/M cached input and $20/M output. The source describes the current promotional period. |
| Current flagship comparator | [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra): medium effort, structured outputs, $10/M input, $1/M cached input, $12.50/M cache writes and $50/M output. |
| OpenAI output contract | [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs): Responses JSON schema output; parser separately handles refusal and incomplete responses. |
| Reasoning allocation | [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning): output caps include reasoning; initial experiments should leave at least 25,000 tokens. This package allocates 32,768 rather than imposing the older 2,048-token cap. |
| OpenAI price accounting | [API pricing](https://developers.openai.com/api/docs/pricing): standard service, short context, separate cached input and cache-write rates. The runner sends no tools or priority tier. Missing cache-write quantities prevent an exact usage estimate; an explicit upper estimate remains available. |
| Existing cross-provider comparator | [Sonnet 5 changes](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5): `claude-sonnet-5`, adaptive thinking and no non-default sampling parameters. Medium effort is set explicitly. |
| Claude response contract | [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs): `output_config.format` with a JSON schema. Text blocks are selected by type after any thinking blocks. |
| Claude price accounting | [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing): Sonnet 5 is $2/M input and $10/M output, with cache reads and writes accounted separately. |

The fetched OpenAI snapshot sections list the named IDs used here without a distinct dated snapshot. This package therefore records exact request IDs, accepted response IDs and every served ID; it does not describe these routes as immutable weight hashes. An unlisted response ID is a recorded version mismatch and halts that model. Observed response IDs are retained in the saved request records and thirteen-model analysis.

Credentials for OpenRouter, OpenAI Responses and Anthropic Messages use `configure_science_keys.py`. Request counts, repeats and output envelopes are fixed in `config.json`; the runner has no monetary cap.
