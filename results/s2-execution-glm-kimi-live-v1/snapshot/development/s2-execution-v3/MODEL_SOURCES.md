# GLM and Kimi interface sources

Documentation and endpoint catalogs retrieved on 2026-09-21 for the third S2 cohort.

| Source | Configuration decision |
|---|---|
| [GLM-5.3-Flash overview](https://docs.z.ai/guides/vlm/glm-5.3-flash) | Model identity, output envelope, mandatory thinking and structured JSON capability. |
| [GLM Chat Completion API](https://docs.z.ai/api-reference/llm/chat-completion) | GLM-5.3-Flash supports `low`, `high` and `max` effort; this cohort uses `high`. |
| [GLM official pricing](https://docs.z.ai/guides/overview/pricing) | Published input, cache-read and output prices. Execution estimates use the selected router endpoint snapshot. |
| [GLM router endpoints](https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flash/endpoints) | Fireworks explicitly lists `structured_outputs` and a sufficient output cap. Z.AI lists `response_format` without `structured_outputs`, so this batch uses Fireworks for the strict JSON Schema contract. |
| [Kimi model list](https://platform.kimi.ai/docs/models) | Current `kimi-k3` model identity; this batch does not select deprecated K2.5. |
| [Kimi reasoning effort](https://platform.kimi.ai/docs/guide/use-reasoning-effort) | K3 supports `low`, `high` and `max`; use `high` through OpenRouter's unified reasoning field. |
| [Kimi router endpoints](https://openrouter.ai/api/v1/models/moonshotai/kimi-k3/endpoints) | Select Moonshot AI's `moonshotai/mxfp4` endpoint with structured outputs and the documented token prices. |
| [OpenRouter provider selection](https://openrouter.ai/docs/guides/routing/provider-selection) | `only`, `allow_fallbacks: false` and `require_parameters: true`; suffix slugs restrict endpoint variants. |
| [OpenRouter reasoning](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens) | Request `reasoning.effort: high`; reasoning consumes output budget. Acceptance alone does not establish upstream internal compute. |

`provider_catalog.json` preserves complete responses for both model catalogs and the retrieval time. The selected endpoint names are `Fireworks | z-ai/glm-5.3-flash-20260826` and `Moonshot AI | moonshotai/kimi-k3-20260715`. Returned model and provider fields must match the configured allowlists. The saved execution records distinguish successful responses, rate-limit failures, and observed model/provider identities.
