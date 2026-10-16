# Release contents

The release includes scientific inputs, reference answers, source evidence,
execution configurations, request and response records, predictions, and analyses.
Case records retain review scope, attribution, accepted answers, and content hashes.

`release-sha256.json` identifies the published files. Verify them and reproduce
the saved S2 scores with:

```sh
python3 -B scripts/verify_release.py
```

Historical manifests, `checks.json`, and source-revision before/after hashes
describe the original experiment archives. Some entries refer to earlier drafts or records unavailable in this
release. Use `release-sha256.json` to check the files distributed here.

Planning documents, candidate-screening notes, and standalone case-comparison
audits are not distributed, including their copies in result source directories.
Published case records retain source evidence, reference answers, review
attribution, and inference boundaries. Distributed source copies include
documentation and review-attribution updates. Historical manifests retain the
original hashes and file inventory. User approval of the prepared review does
not add independent scientific annotations.

`omitted_development_records` lists the excluded development files in
`release-sha256.json`. Release verification rejects their restoration at those paths.

Use the current scripts to prepare new runs. Drag preparation verifies distributed
source runs against the release hashes before copying their experimental records.
New runs retain their own frozen-file checks.

Release verification checks published-file hashes, runs the case validators with
`--release`, and compares regenerated inputs, requests, references, outputs, and
scores with the saved S2 artifacts. The case validators check current
document/data agreement, reference content, and deterministic calculations.
Historical `results/s2-*/analyze.py` and `verify_analysis.py` checks require the
corresponding original files and may write analysis artifacts; the
pre-translation comparison is skipped when that archive is absent. Current
English inputs and their executed request packets are still checked.

File hashes establish artifact identity, not independent scientific validation.

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
