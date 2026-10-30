"""Paper metrics distinguish scientific fields from historical full outputs."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_paper_metrics import downstream_exact, score, strict_equal


@pytest.fixture(scope='module')
def alternatives():
    # Isolate the execution package's generic module names from other tests.
    source = '''
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / 'development/s2-execution-v1'))
from dataset import load_inputs
from derive import derive
from scoring import load_references, score_lane
groups = load_inputs()
refs = load_references(groups)
examples = {}
for gid, option in [('E004', 'one_common_history'), ('E009', 'independent_reference')]:
    group = next(g for g in groups if g['group_id'] == gid)
    answers = {q['question_id']: refs['answers'][q['question_id']] for q in group['questions']}
    answers[gid + '-Q01'] = option
    row = {'answers': answers, 'derived': derive(group, answers)}
    historical = score_lane([group], refs, {(0, gid): row}, 1)['per_claim'][0]
    examples[gid] = {'group': group, 'refs': refs, 'row': row, 'historical': historical}
print(json.dumps(examples))
'''
    return json.loads(subprocess.check_output([sys.executable, '-B', '-c', source], cwd=ROOT, text=True))


def test_label_change_does_not_change_scientific_outputs(alternatives):
    case = alternatives['E004']
    result = score(case['group'], case['refs'], case['row'])
    assert result['downstream_exact']
    assert not result['joint_correct']
    assert not result['label_correct']
    assert not case['historical']['exact']


def test_covariance_change_counts_as_downstream_error(alternatives):
    case = alternatives['E009']
    result = score(case['group'], case['refs'], case['row'])
    assert not result['downstream_exact']
    assert not result['joint_correct']
    assert case['historical']['counts_exact']


@pytest.mark.parametrize('actual, expected', [
    (False, 0), (1.0, 1), ({'nested': [True]}, {'nested': [1]}), ({}, {'unknown': None}),
])
def test_strict_comparison_rejects_type_and_missing_value_changes(actual, expected):
    assert not strict_equal(actual, expected)


def test_unknown_field_must_be_present():
    expected = {'exact_parent_lot_count': None, 'complete_assignment_available': False}
    assert downstream_exact('E004', expected.copy(), expected)
    assert not downstream_exact('E004', {'complete_assignment_available': False}, expected)
    assert not downstream_exact('E004', None, expected)


def test_missing_response_gets_no_credit(alternatives):
    case = alternatives['E004']
    result = score(case['group'], case['refs'], {'answers': {}, 'derived': None})
    assert result['planned_semantic_answers'] == 2
    assert result['received_semantic_answers'] == result['semantic_correct'] == 0
    assert not any(result[k] for k in ('downstream_exact', 'joint_correct', 'label_correct'))


def test_biological_counts_and_canonical_label():
    path = ROOT / 'results/s2-execution-live-v1'
    group = next(g for g in json.loads((path / 'inputs.json').read_text()) if g['group_id'] == 'B002')
    refs = json.loads((path / 'evaluation_only/references.json').read_text())
    row = json.loads((path / 'attempts/r01-B002-jev/prediction.json').read_text())
    result = score(group, refs, row)
    assert result['semantic_correct'] == 2
    assert all(result[k] for k in ('downstream_exact', 'joint_correct', 'label_correct'))
    changed = copy.deepcopy(row)
    changed['derived']['counts']['growth_histories']['11a'] = True
    assert not score(group, refs, changed)['downstream_exact']
