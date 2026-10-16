"""Evaluation-only references and fixed-denominator reports."""
from collections import Counter
from common import OLD, NONBIO, BIO, read
from dataset import INDEPENDENT_REVIEW_GROUPS
from derive import derive


def load_references(groups):
    old = read(OLD / 'choice-review-v1/evaluation.json')
    refs = {'answers': {q: v['expected_option'] for q, v in old['questions'].items()},
            'outcomes': {g['group_id']: {'cases': {
                c['case_id']: ({'engineering': old['case_outcomes'][c['case_id']]['engineering']}
                               if c.get('engineering') else old['case_outcomes'][c['case_id']])
                for c in g['cases']}} for g in groups if g['package'] == 'original'}}
    for base in (NONBIO, BIO):
        for p in read(base / 'evaluation.json')['problems']:
            refs['answers'].update({q['question_id']: q['reference_option'] for q in p['questions']})
            outcome = (p['deterministic_work']['expected_outcome'] if base == NONBIO else p['expected_code_output'])
            refs['outcomes'][p['problem_id']] = outcome
    qids = {q['question_id'] for g in groups for q in g['questions']}
    if set(refs['answers']) != qids:
        raise ValueError('reference coverage mismatch')
    for g in groups:
        for q in g['questions']:
            if refs['answers'][q['question_id']] not in q['question']['criteria']:
                raise ValueError('reference option outside candidates')
    return refs


def projection(group, value):
    if value is None:
        return None
    if group['package'] == 'original':
        return value.get('cases')
    if group['package'] == 'nonbio':
        return value.get('output')
    return {k: value.get(k) for k in ('status', 'counts', 'clauses', 'final_label')}


def expected_projection(group, refs):
    value = refs['outcomes'][group['group_id']]
    if group['package'] == 'original':
        return value['cases']
    if group['package'] == 'nonbio':
        return {k: v for k, v in value.items() if k != 'description'}
    return {k: value[k] for k in ('status', 'counts', 'clauses', 'final_label')}


def oracle(groups, refs):
    rows = []
    for g in groups:
        a = {q['question_id']: refs['answers'][q['question_id']] for q in g['questions']}
        result = derive(g, a)
        actual, expected = projection(g, result), expected_projection(g, refs)
        rows.append({'group_id': g['group_id'], 'answers': a, 'derived': result,
                     'expected': expected, 'exact': actual == expected})
    return {'condition': 'reference_oracle', 'model_performance': False,
            'purpose': 'Check deterministic code with reference answers; not semantic prediction or scientific re-review',
            'groups_correct': sum(r['exact'] for r in rows), 'groups_denominator': len(rows), 'rows': rows}


def fraction(correct, denominator):
    return {'correct': correct, 'denominator': denominator,
            'accuracy': correct/denominator if denominator else None}


def score_lane(groups, refs, group_results, repetitions):
    choices, claims, engineering, derived_groups = [], [], [], []
    for rep in range(repetitions):
        for g in groups:
            gid = g['group_id']
            row = group_results.get((rep, gid), {})
            predictions = row.get('answers', {})
            for q in g['questions']:
                qid = q['question_id']
                detail = {'repeat': rep, 'group_id': gid, 'question_id': qid, 'route': g['route'],
                          'reference': refs['answers'][qid], 'prediction': predictions.get(qid),
                          'correct': predictions.get(qid) == refs['answers'][qid],
                          'failure': row.get('errors', {}).get(qid, None if qid in predictions else 'not_attempted'),
                          'recent_independent_review': gid in INDEPENDENT_REVIEW_GROUPS}
                (engineering if q['engineering'] else choices).append(detail)
            actual, expected = projection(g, row.get('derived')), expected_projection(g, refs)
            derived_groups.append({'repeat': rep, 'group_id': gid, 'exact': actual == expected,
                                   'semantic_and_outcome_exact': actual == expected and all(
                                       predictions.get(q['question_id']) == refs['answers'][q['question_id']]
                                       for q in g['questions']),
                                   'status': (row.get('derived') or {}).get('status', 'missing_answers')})
            if g['package'] == 'original':
                for c in g['cases']:
                    if c.get('engineering'):
                        continue
                    cid = c['case_id']; prediction = (actual or {}).get(cid)
                    reference = expected[cid]
                    claims.append({'repeat': rep, 'group_id': gid, 'case_id': cid,
                                   'exact': prediction == reference,
                                   'counts_exact': prediction is not None and 'count' in prediction and prediction['count'] == reference['count'],
                                   'label_exact': prediction is not None and 'label' in prediction and prediction['label'] == reference['label']})
            else:
                label = 'claim_assessment' if g['package'] == 'nonbio' else 'final_label'
                count_keys = [k for k, v in expected.items() if v is None or type(v) in (int, float, list, dict)] if g['package'] == 'nonbio' else ['counts']
                claims.append({'repeat': rep, 'group_id': gid, 'case_id': gid,
                               'exact': actual == expected,
                               'counts_exact': actual is not None and all(k in actual and actual[k] == expected[k] for k in count_keys),
                               'label_exact': actual is not None and label in actual and actual[label] == expected[label]})
    subsets = {'scientific_workflow_choices': choices,
               'model_routed_semantic_choices': [r for r in choices if r['route'] == 'model'],
               'zero_call_scientific_choices': [r for r in choices if r['route'] == 'code'],
               'recent_independent_review_subset': [r for r in choices if r['recent_independent_review']]}
    result = {name: fraction(sum(r['correct'] for r in rows), len(rows)) for name, rows in subsets.items()}
    result['scientific_claims'] = {k: fraction(sum(r[k] for r in claims), len(claims))
                                   for k in ('exact', 'counts_exact', 'label_exact')}
    result['engineering_choices'] = fraction(sum(r['correct'] for r in engineering), len(engineering))
    result['group_semantic_and_outcome_exact'] = fraction(sum(r['semantic_and_outcome_exact'] for r in derived_groups), len(derived_groups))
    result['by_group'] = {g['group_id']: fraction(sum(r['correct'] for r in choices if r['group_id']==g['group_id']),
                                                sum(r['group_id']==g['group_id'] for r in choices)) for g in groups}
    result['group_macro_accuracy'] = sum(v['accuracy'] for v in result['by_group'].values())/len(groups)
    result['failure_types'] = dict(Counter(r['failure'] for r in choices if r['failure']))
    result['semantic_fallbacks'] = dict(Counter(r['prediction'] for r in choices
                                               if r['prediction'] in {'not_stated', 'other', 'conflicting', 'conflicting_assignment'}))
    result['derivation_statuses'] = dict(Counter(r['status'] for r in derived_groups))
    result['per_repeat'] = [fraction(sum(r['correct'] for r in subsets['model_routed_semantic_choices'] if r['repeat']==rep),
                                     sum(r['repeat']==rep for r in subsets['model_routed_semantic_choices'])) for rep in range(repetitions)]
    result['stability'] = {q: {'distinct_valid_answers': sorted({r['prediction'] for r in choices if r['question_id']==q and r['prediction'] is not None}),
                               'missing_executions': sum(r['prediction'] is None for r in choices if r['question_id']==q)}
                           for q in {r['question_id'] for r in choices if r['route']=='model'}}
    result['per_choice'] = choices
    result['per_claim'] = claims
    result['per_group'] = derived_groups
    result['denominator_policy'] = 'Fixed planned denominator; failed, missing and unattempted answers remain incorrect. Repetitions share inputs and sources.'
    return result
