# S2 semantic and operational exceptions

All seven observed semantic errors concern B002-Q01. The expected option is `shared_then_separate`, and expected culture growth histories are `11a: 1; 11: 10`. The correct final label is `inconsistent`. Links point to the saved response receipt; the same attempt directory contains the request intent and persisted prediction.

| Attempt | Selected option | Growth histories 11a / 11 | First clause | Final label |
| --- | --- | --- | --- | --- |
| [r02-B002-luna](../../results/s2-execution-live-v1/attempts/r02-B002-luna/receipt.json) | separate_then_shared | 10 / 1 | consistent | inconsistent |
| [r01-B002-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r01-B002-qwen_flash/receipt.json) | separate_then_shared | 10 / 1 | consistent | inconsistent |
| [r01-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r01-B002-qwen_max/receipt.json) | both_shared | 1 / 1 | inconsistent | inconsistent |
| [r02-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r02-B002-qwen_max/receipt.json) | both_shared | 1 / 1 | inconsistent | inconsistent |
| [r03-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r03-B002-qwen_max/receipt.json) | separate_then_shared | 10 / 1 | consistent | inconsistent |
| [r04-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r04-B002-qwen_max/receipt.json) | both_separate | 10 / 10 | consistent | inconsistent |
| [r05-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r05-B002-qwen_max/receipt.json) | separate_then_shared | 10 / 1 | consistent | inconsistent |

All seven retain `clonal_descendants` for B002-Q02, `exact_mutation_origins: null`, and colony totals `{11a: 514, 11: 624}`. The second clause, `one_colony_one_origin`, is inconsistent in every case. It keeps the final label correct despite the wrong Choice and derived counts. These are seven responses to one independent question, not seven independent scientific cases.

The operational exceptions contain no valid Choice answers. Each removes two planned answers and one complete derived outcome while remaining in the fixed denominators.

| Attempt | HTTP status | Saved error category | Absent answers | Usage / cost |
| --- | --- | --- | --- | --- |
| [r01-B002-terra](../../results/s2-execution-live-v1/attempts/r01-B002-terra/receipt.json) | no response | InterruptedWithoutReceipt | 2 | unknown |
| [r02-B004-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-B004-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r02-E005-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-E005-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r02-E010-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-E010-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r03-B001-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-B001-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r03-E007-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-E007-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r03-E009-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-E009-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r04-B003-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r04-B003-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r04-E009-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r04-E009-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r05-B001-deepseek_flash](../../results/s2-execution-extension-live-v1/attempts/r05-B001-deepseek_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r05-E009-deepseek_flash](../../results/s2-execution-extension-live-v1/attempts/r05-E009-deepseek_flash/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |
| [r05-E007-deepseek_pro](../../results/s2-execution-extension-live-v1/attempts/r05-E007-deepseek_pro/receipt.json) | 429 | upstream_provider_shared_pool | 2 | unknown |

Terra's interruption is a terminal local recovery record with unknown server completion, tokens and charge. It is not a confirmed semantic error or a confirmed provider rejection. Every extension failure is a received HTTP 429. The router identifies the fixed upstream provider's shared pool as the rate-limit source: eight Alibaba/Qwen Flash, two Fireworks/DeepSeek Flash and one Fireworks/DeepSeek Pro. This is the saved service explanation; no further upstream diagnosis was performed. No absent record is converted into `not_stated`, and no failed request is retried or replaced.

Format/contract errors and missing answer fields within HTTP 200 responses both count zero. All remaining received semantic answers match their existing references. See [choices.json](choices.json) for every Choice and [outcomes.json](outcomes.json) for complete actual/reference projections, including nulls.
