# Release contents

The release includes scientific inputs, reference answers, source evidence,
execution configurations, request and response records, predictions, and analyses.
Case records retain review scope, attribution, accepted answers, and content hashes.

`release-sha256.json` lists the published files and their SHA-256 digests.
Verification checks this file set and reproduces the saved S2 scores:

```sh
python3 -B scripts/verify_release.py
```

Case records identify the author review, review date, accepted answers and
content hashes. Source-revision records retain changes to evidence wording
and the corresponding before/after hashes. This is author review;
independent multi-reviewer annotation was not performed.

Historical inventories retain the original hashes for the recorded experimental
artifacts. Their validation counts describe the original runs. Current file
identity is checked against `release-sha256.json`; historical validation reports
are distributed as structured summaries.

Use the current scripts to prepare new runs. Drag preparation verifies distributed
source runs against the release hashes before copying their experimental records.
New runs retain their own frozen-file checks.

Release verification checks published-file hashes, runs the case validators,
and compares regenerated inputs, requests, references, outputs, and
scores with the saved S2 artifacts. The case validators check current
document/data agreement, accepted-reference hashes, source content, and
deterministic calculations. Preflight tests compare the current inputs with
the publicly saved execution snapshot. Use these commands for the distributed
results; the analysis scripts under `results/` record the original analysis
procedures and may write analysis artifacts.

The following source PDFs are not distributed. Their original paths and hashes
remain in the case records and historical manifests; source URLs remain in each
batch's `sources.json`:

- `paired-fixed-1806.01871v1.pdf`
- `metrology-1510.07866v3.pdf`
- `cloud-2014-report.pdf`
- `luria-delbruck-1943.pdf`

`omitted_source_assets` in `release-sha256.json` records their exact paths.
Release verification requires these files to be absent and reports them as
omitted, without checking their contents. Prepared evidence text and saved
experimental artifacts are retained. Reproducing the saved scores does not
require these PDFs.
