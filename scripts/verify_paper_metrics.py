"""Reproduce the paper's correctness metrics from saved responses, offline."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys

from verify_release import COHORTS, ROOT, blocked, read, verify_files

PAPER_MODELS = (
    'jev', 'luna', 'terra', 'sol', 'astra', 'sonnet', 'opus5',
    'qwen_flash', 'qwen_max', 'deepseek_flash', 'deepseek_pro', 'kimi_k3',
)
# JSON fields corresponding to the paper's declared scientific outputs.
# Biological cases store these fields inside `counts`.
FIELDS = {
    'E004': ('exact_parent_lot_count', 'complete_assignment_available'),
    'E005': ('next_stress_after_initial_failure_MPa', 'next_stress_after_initial_runout_MPa',
             'observed_replicates_at_any_fixed_stress'),
    'E006': ('paired_realizations', 'paired_execution_count', 'values_entering_pair_ensemble'),
    'E007': ('original_members', 'smbb_members', 'total_members', 'smoothing_only_contrast'),
    'E009': ('compared_laboratory_results', 'calibration_visits', 'shared_covariance_term',
             'exact_effective_replication_count'),
    'E010': ('original_EUs', 'retained_EUs', 'joint_assignment_events', 'range_level_records',
             'independent_range_draws_claim'),
    'B001': ('F3_pups', 'F3_weaned_litters', 'newly_injected_F3_animals',
             'first_generation_beyond_original_window', 'distinct_F0_ancestors'),
    'B002': ('platings', 'growth_histories', 'colony_totals', 'exact_mutation_origins'),
    'B003': ('selected_libraries', 'distinct_contributors', 'distinct_contributors_by_genotype',
             'contributor_appearances', 'separately_observed_contributor_profiles'),
    'B004': ('deep_sequenced_hybrid_founders', 'reported_mutant_alleles',
             'validated_new_germline_lines'),
}
LABELS = {
    'inconsistent_single_history; insufficient_exact_assignments': 'inconsistent',
    'inconsistent_in_both_clauses': 'inconsistent',
    'inconsistent_independent_assignment; zero_exposure_not_established_by_label': 'inconsistent',
}


def strict_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            strict_equal(actual[k], expected[k]) for k in expected)
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            strict_equal(a, e) for a, e in zip(actual, expected))
    return actual == expected


def downstream_exact(group_id, actual, expected):
    return isinstance(actual, dict) and all(
        key in actual and strict_equal(actual[key], expected[key]) for key in FIELDS[group_id])


def score(group, refs, row):
    gid = group['group_id']
    answers, derived = row['answers'], row['derived']
    semantic = [strict_equal(answers.get(q['question_id']), refs['answers'][q['question_id']])
                for q in group['questions']]
    reference = refs['outcomes'][gid]
    biological = group['package'] == 'biology'
    expected = reference['counts'] if biological else reference
    actual = (derived or {}).get('counts' if biological else 'output')
    downstream = downstream_exact(gid, actual, expected)
    label = reference['final_label' if biological else 'claim_assessment']
    return {
        'planned_semantic_answers': len(semantic),
        'received_semantic_answers': sum(q['question_id'] in answers for q in group['questions']),
        'semantic_correct': sum(semantic),
        'downstream_exact': downstream,
        'joint_correct': downstream and all(semantic),
        'label_correct': strict_equal((derived or {}).get('final_label'), LABELS.get(label, label)),
    }


def verify_cohort(name):
    package, directory = COHORTS[name]
    sys.path.insert(0, str(ROOT / 'development' / package))
    import run
    import providers
    from scoring import load_references

    socket.socket = socket.create_connection = blocked
    run.http_transport = providers.http_transport = blocked
    path = ROOT / 'results' / directory
    groups, config, plan = (read(path / f'{n}.json') for n in ('inputs', 'config', 'plan'))
    refs = read(path / 'evaluation_only/references.json')
    assert groups == run.load_inputs(), 'Published inputs differ from executed inputs'
    assert refs == load_references(groups), 'Published references differ from executed references'
    assert plan == run.matrix(groups, config), 'Request assembly changed'
    records = run.validate_attempts(path)
    jobs = {job['job_id']: job for job in plan['jobs']}
    assert {r['job_id'] for r in records} == set(jobs), 'Incomplete request records'
    by_group = {g['group_id']: g for g in groups}
    models = {m['id']: m for m in config['models']}
    report = read(sorted((path / 'reports').glob('*.json'))[-1])
    rows = []
    for saved in records:
        mid, gid, jid = saved['model_id'], saved['group_id'], saved['job_id']
        if mid not in PAPER_MODELS:
            assert mid == 'glm_flash', 'Unexpected excluded model'
            continue
        group = by_group[gid]
        receipt = read(path / 'attempts' / jid / 'receipt.json')
        fresh = run.finish(jobs[jid], models[mid], group, receipt)
        assert strict_equal(fresh['answers'], saved['answers']), jid
        assert strict_equal(fresh['derived'], saved['derived']), jid
        assert not fresh['simulated'], 'Expected a recorded model request'
        metrics = score(group, refs, fresh)
        historical = report['model_scores'][mid]
        claim = next(r for r in historical['per_claim']
                     if r['group_id'] == gid and r['repeat'] == saved['repeat'])
        outcome = next(r for r in historical['per_group']
                       if r['group_id'] == gid and r['repeat'] == saved['repeat'])
        rows.append({'model_id': mid, 'group_id': gid, 'job_id': jid,
                     'complete': fresh['status'] == 'complete', **metrics,
                     'historical_full_exact': claim['exact'],
                     'historical_counts_exact': claim['counts_exact'],
                     'historical_joint_correct': outcome['semantic_and_outcome_exact'],
                     'historical_label_correct': claim['label_exact']})
    return {'requests_reparsed': len(records), 'rows': rows}


def summarize(rows):
    return {'planned_requests': len(rows), 'complete_responses': sum(r['complete'] for r in rows),
            **{key: sum(r[key] for r in rows) for key in (
                'planned_semantic_answers', 'received_semantic_answers', 'semantic_correct',
                'downstream_exact', 'joint_correct', 'label_correct')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort', choices=COHORTS, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.cohort:
        print(json.dumps(verify_cohort(args.cohort)))
        return
    verify_files()
    # Each execution cohort has its own modules named run/providers/scoring.
    cohorts = []
    for name in COHORTS:
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--cohort', name],
                                check=True, capture_output=True, text=True)
        cohorts.append(json.loads(result.stdout))
    rows = [r for cohort in cohorts for r in cohort['rows']]
    assert {r['model_id'] for r in rows} == set(PAPER_MODELS)
    for mid in PAPER_MODELS:
        model_rows = [r for r in rows if r['model_id'] == mid]
        assert len(model_rows) == 50 and {r['group_id'] for r in model_rows} == set(FIELDS)
    comparisons = {
        'downstream_vs_full': ('downstream_exact', 'historical_full_exact'),
        'downstream_vs_counts': ('downstream_exact', 'historical_counts_exact'),
        'joint': ('joint_correct', 'historical_joint_correct'),
        'label': ('label_correct', 'historical_label_correct'),
    }
    differences = {name: [r['job_id'] for r in rows if r[a] != r[b]]
                   for name, (a, b) in comparisons.items()}
    passed = not any(differences.values())
    print(json.dumps({
        'status': 'passed' if passed else 'failed',
        'requests_reparsed': sum(c['requests_reparsed'] for c in cohorts),
        'totals': summarize(rows),
        'per_model': {mid: summarize([r for r in rows if r['model_id'] == mid]) for mid in PAPER_MODELS},
        'request_level_differences': differences,
        'network_calls': 0, 'result_files_written': 0,
    }, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit((exc.stdout or '') + (exc.stderr or ''))
