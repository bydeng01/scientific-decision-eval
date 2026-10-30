# References and scoring

`references.json` is evaluation-only data. Each item stores its reviewed relation, target count, final label and downstream action. The relation oracle is supplied manually and bypasses text extraction. Its result is reported separately from predictions made from `inputs/evidence.json`.

The English migration preserves the reference file byte for byte, including scientific scope and numeric filters. Translation checks are recorded in [text_revision.json](../text_revision.json). Earlier human confirmations concern source content and scope, not approval of the translated wording.

For the eleven scientific items, scoring reports exact relation structure, count correctness, label correctness and action correctness. Labels mean:

- `supported`: all quantities in the scoped claim agree with the extracted relation.
- `inconsistent`: at least one required quantity disagrees with the complete relation.
- `insufficient`: the parsed evidence does not establish a required count.

Unsupported input or a parser failure receives a null scientific label and a separate review action. It is counted as a failed scientific prediction, not as a correct insufficiency decision. Confusion matrices retain this null-output category.

D03 has three atomic fields: `treatment_level`, `run_boundary` and `specimen_assignment`. The reference identifies water-bath temperature control while leaving boundaries and assignment `not_stated`. The target count is null. Scoring checks all three fields and the request for run-boundary/specimen-to-run records.

D01-O is excluded from the scientific denominator. Its normal rule result and simulated candidate-omission action are checked separately. Selecting `other` in this simulation tests engineering routing, not a model's ability to recognize missing candidates.

The current label distribution is five supported, five inconsistent and one insufficient claim. Error reports include missed incorrect-count claims and false alarms. The six groups come from five sources; D01 and D03 share U. These are reviewed development cases. No model quality or post-record-request quality is measured.
