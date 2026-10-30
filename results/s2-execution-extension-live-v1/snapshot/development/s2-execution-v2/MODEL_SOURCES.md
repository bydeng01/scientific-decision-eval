# Extension interface sources

Checked on 2026-09-21 before the added inference requests. The complete OpenRouter endpoint catalog is saved in `provider_catalog.json`, including supported parameters, endpoint names, output limits, upstream identities and prices. Retrieval comprised four public catalog requests.

| Source | Decision supported |
|---|---|
| [Qwen3.8 Flash](https://openrouter.ai/qwen/qwen3.8-flash) | Named route; Alibaba endpoint; JSON schema and reasoning support. Catalog endpoint names the 20260826 version. |
| [Qwen3.8 Max 0902](https://openrouter.ai/qwen/qwen3.8-max-0902) | Explicit 0902 route; Alibaba endpoint names the 20260902 version. |
| [DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash) | Named route; catalog names the 20260910 version. Fireworks supports the requested schema and token envelope. |
| [DeepSeek V4 Pro 0813](https://openrouter.ai/deepseek/deepseek-v4-pro-0813) | Explicit 0813 route; catalog names the 20260813 version. Same fixed Fireworks service as Flash. |
| [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) | `provider.only` restricts providers, `allow_fallbacks: false` prevents switching, and `require_parameters: true` rejects unsupported parameter routing. |
| [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs) | `response_format.type=json_schema`, named schema and strict flag. Enforcement can vary upstream; local parsing still validates every key and option. |
| [OpenRouter reasoning](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens) | Explicit `reasoning.effort` and reasoning usage. Router-normalized effort is not a universal compute scale. |
| [DeepSeek Chat API](https://api-docs.deepseek.com/api/create-chat-completion/) | Ordinary `high` thinking; first-party compatibility mapping of `medium` to `high`. This motivates the requested setting without claiming to inspect Fireworks internals. |
| [Claude Opus 5](https://platform.claude.com/docs/en/models/opus-5/overview) | Direct model ID `claude-opus-5`; adaptive thinking; $5/M input, $25/M output, $0.50/M cache read, $6.25/M 5-minute cache write. No fast mode or one-hour cache is requested. |

The selected OpenRouter prices per million tokens are Flash Qwen $0.15/$0.47, Max Qwen $2/$6, Flash DeepSeek $0.22/$0.66, and Pro DeepSeek $1.32/$3.96 for input/output. Cache rates are copied from the selected endpoint, not the model page's cheapest provider. OpenRouter response-reported charges take precedence as observations; snapshot-based estimates remain separate.

Provider support and model availability were checked through public metadata. Account access and observed returned identities are established only by the saved live responses. A contract failure is retained and halts the affected model; it does not authorize a silent substitute.
