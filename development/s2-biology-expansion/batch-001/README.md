# Biological S2 expansion, batch 001

The collection contains 16 non-biological groups and 4 biological groups: **20 total**. User-approved biological references cover 4 groups and 8 Choices. Review attribution for the original and non-biological expansion groups is recorded in their case packages.

| Group | Scientific distinction | Questions | Status |
| --- | --- | --- | --- |
| [B001](BATCH_REVIEW.md#b001) | Developmental exposure of future-generation germ cells | 2 | user_reviewed |
| [B002](BATCH_REVIEW.md#b002) | Clonal amplification separates mutation origins from colony counts | 2 | user_reviewed |
| [B003](BATCH_REVIEW.md#b003) | Pre-assay pooling merges outcomes and reuses the same contributors | 2 | user_reviewed |
| [B004](BATCH_REVIEW.md#b004) | Somatic mosaicism and a non-specific germline phenotype marker | 2 | user_reviewed |

[BATCH_REVIEW.md](BATCH_REVIEW.md) contains all four groups and their reference answers.

`inputs.json` contains evidence, structured records, claims, and Choices. `evaluation.json` contains reference answers, rationales, inference boundaries, and expected code outputs. `derive.py` performs offline bookkeeping from supplied semantic answers; its outputs are conditional on those answers. [SOURCE_REVIEW.md](SOURCE_REVIEW.md) records source locations and inspection limits. [REVIEW_LOG.md](REVIEW_LOG.md) records each question's status. `collection_inventory.json` preserves the prior inventory and file hashes.

Run from the repository root:

```sh
python3 -B development/s2-biology-expansion/batch-001/verify_batch.py --release
```

After editing case documentation, regenerate Markdown with `render_review.py` and check it with `verify_batch.py --release`. For published-file checksums and saved model scores, run `python3 -B scripts/verify_release.py` from the repository root. Historical `--write-checks` requires the original private archive. These checks establish artifact consistency, not scientific correctness.
