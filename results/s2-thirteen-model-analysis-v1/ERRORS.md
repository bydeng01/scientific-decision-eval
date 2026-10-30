# S2 semantic and operational exceptions

All seven known semantic errors concern B002-Q01. The reference `shared_then_separate` maps culture growth histories to 11a:1 and 11:10. The wrong answers change these counts; B002-Q02 remains `clonal_descendants`, mutation origins remain null, colony totals remain 514 and 624, and the final label remains inconsistent. These are seven responses to one unique scientific Choice.

| Attempt | Choice | Reference | Prediction | Full output exact | Label exact |
| --- | --- | --- | --- | --- | --- |
| [r02-B002-luna](../../results/s2-execution-live-v1/attempts/r02-B002-luna/receipt.json) | B002-Q01 | shared_then_separate | separate_then_shared | False | True |
| [r01-B002-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r01-B002-qwen_flash/receipt.json) | B002-Q01 | shared_then_separate | separate_then_shared | False | True |
| [r01-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r01-B002-qwen_max/receipt.json) | B002-Q01 | shared_then_separate | both_shared | False | True |
| [r02-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r02-B002-qwen_max/receipt.json) | B002-Q01 | shared_then_separate | both_shared | False | True |
| [r03-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r03-B002-qwen_max/receipt.json) | B002-Q01 | shared_then_separate | separate_then_shared | False | True |
| [r04-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r04-B002-qwen_max/receipt.json) | B002-Q01 | shared_then_separate | both_separate | False | True |
| [r05-B002-qwen_max](../../results/s2-execution-extension-live-v1/attempts/r05-B002-qwen_max/receipt.json) | B002-Q01 | shared_then_separate | separate_then_shared | False | True |

The following 53 operational exceptions account for 106 absent semantic answers. Terra's interruption has unknown server completion. The other 52 records are received HTTP 429s, including 41 GLM/Fireworks failures. No absent answer is classified as a semantic mistake or converted into `not_stated`. Saved rate-limit metadata describes the service response; it is not an independent upstream diagnosis. Costs remain unknown.

| Attempt | HTTP | Saved error or limit source | Cost |
| --- | --- | --- | --- |
| [r01-B002-terra](../../results/s2-execution-live-v1/attempts/r01-B002-terra/receipt.json) | unknown | InterruptedWithoutReceipt | unknown |
| [r02-B004-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-B004-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E005-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-E005-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E010-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r02-E010-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-B001-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-B001-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E007-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-E007-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E009-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r03-E009-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-B003-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r04-B003-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E009-qwen_flash](../../results/s2-execution-extension-live-v1/attempts/r04-E009-qwen_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-B001-deepseek_flash](../../results/s2-execution-extension-live-v1/attempts/r05-B001-deepseek_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E009-deepseek_flash](../../results/s2-execution-extension-live-v1/attempts/r05-E009-deepseek_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E007-deepseek_pro](../../results/s2-execution-extension-live-v1/attempts/r05-E007-deepseek_pro/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r01-E005-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r01-E005-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r01-E009-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r01-E009-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-B001-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-B001-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-B002-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-B002-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-B003-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-B003-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-B004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-B004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-E004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E005-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-E005-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E007-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-E007-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E009-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-E009-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r02-E010-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r02-E010-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-B001-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-B001-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-B002-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-B002-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-B003-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-B003-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-B004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-B004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E005-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E005-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E006-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E006-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E007-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E007-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E009-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E009-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r03-E010-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r03-E010-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-B001-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-B001-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-B002-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-B002-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-B003-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-B003-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-B004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-B004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E005-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E005-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E006-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E006-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E007-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E007-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E009-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E009-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r04-E010-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r04-E010-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-B001-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-B001-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-B002-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-B002-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-B003-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-B003-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-B004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-B004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E004-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E004-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E005-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E005-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E006-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E006-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E007-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E007-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E009-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E009-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |
| [r05-E010-glm_flash](../../results/s2-execution-glm-kimi-live-v1/attempts/r05-E010-glm_flash/receipt.json) | 429 | upstream_provider_shared_pool | unknown |

There are no format/contract errors or missing answer fields in the 597 HTTP 200 responses. Complete actual/reference projections are in [outcomes.json](outcomes.json).
