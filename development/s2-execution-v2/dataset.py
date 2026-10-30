"""Input-only assembly. No reference or review-decision file is read here."""
from collections import Counter
from common import OLD, NONBIO, BIO, ROOT, read

INDEPENDENT_REVIEW_GROUPS = {'E002', 'E003', 'E006', 'E007', 'E008', 'E010',
                             'B001', 'B002', 'B003', 'B004'}
ZERO_EXPANSION = {'E001', 'E002', 'E003', 'E008'}


def reject_reference_fields(value):
    forbidden = {'reference_option', 'expected_option', 'expected_code_output', 'expected_outcome',
                 'review_status', 'review_rationale', 'evidence_rationale', 'reference_provenance',
                 'approved_questions', 'deterministic_work', 'evaluation_only',
                 'reviewer', 'reviewed_by', 'reviewed_on', 'review_attribution', 'approval_scope',
                 'approval_evidence', 'approval_decision_id', 'approved_problem_ids',
                 'approved_by_author', 'approved_by_user',
                 'author_choice_review', 'user_choice_review',
                 'author_reviewed_question_ids', 'user_approved_question_ids',
                 'author_review_decision_id', 'user_review_decision_id',
                 'author_review_summary_english', 'user_review_summary_english',
                 'author_statement', 'user_statement',
                 'case_content_approved_by_author', 'case_content_approved_by_user',
                 'case_content_approved_by_author_definition', 'case_content_approved_by_user_definition',
                 'per_question_author_choice_review', 'per_question_user_choice_review'}
    if isinstance(value, dict):
        if forbidden & set(value):
            raise ValueError('Reference/review field in model-facing state')
        for child in value.values():
            reject_reference_fields(child)
    elif isinstance(value, list):
        for child in value:
            reject_reference_fields(child)


def load_inputs():
    original = read(OLD / 'choice-review-v1/inputs.json')
    cases = read(OLD / 'inputs/cases.json')
    evidence = {g['group_id']: g for g in read(OLD / 'inputs/evidence.json')}
    groups = []
    for gid, ev in evidence.items():
        qs = [q for q in original['questions'] if q['group_id'] == gid]
        groups.append({'group_id': gid, 'package': 'original', 'route': 'code',
                       'source_ids': [ev['source_id']],
                       'source_families': ['NIST-HANDBOOK' if ev['source_id'] == 'N' else 'original:' + ev['source_id']],
                       'input_file': str((OLD / 'choice-review-v1/inputs.json').relative_to(ROOT)),
                       'input_pointer': '/questions',
                       'cases': [c for c in cases if c['group_id'] == gid],
                       'problem': None,
                       'questions': [{'question_id': q['question_id'], 'case_ids': q['case_ids'],
                                      'input_pointer': f"/questions/{original['questions'].index(q)}",
                                      'reference_pointer': '/questions/' + q['question_id'] + '/expected_option',
                                      'engineering': q['role'] == 'engineering_simulation_only',
                                      'state': q['state'], 'question': q['question']} for q in qs]})
    for package, base in [('nonbio', NONBIO), ('biology', BIO)]:
        sources = read(base / 'sources.json')
        rows = sources.get('source_records', sources.get('sources', []))
        source_map = {s['source_id']: s['source_family'] for s in rows}
        for index, p in enumerate(read(base / 'inputs.json')['problems']):
            # Deliberately omit claims, filenames, review annotations and titles.
            state = {k: p[k] for k in ('target_treatment', 'scope', 'evidence', 'records')}
            groups.append({'group_id': p['problem_id'], 'package': package,
                           'route': 'code' if p['problem_id'] in ZERO_EXPANSION else 'model',
                           'source_ids': p['source_ids'],
                           'source_families': sorted({source_map[s] for s in p['source_ids']}),
                           'input_file': str((base / 'inputs.json').relative_to(ROOT)),
                           'input_pointer': f'/problems/{index}', 'cases': [], 'problem': p,
                           'questions': [{'question_id': q['question_id'], 'case_ids': [p['problem_id']],
                                          'input_pointer': f'/problems/{index}/questions/{qi}',
                                          'reference_pointer': f'/problems/{index}/questions/{qi}/reference_option',
                                          'engineering': False, 'state': state,
                                          'question': {'type': 'choice', 'instructions': q['instruction'],
                                                       'criteria': q['options']}} for qi, q in enumerate(p['questions'])]})
    qs = [q for g in groups for q in g['questions']]
    if len(groups) != 20 or len({g['group_id'] for g in groups}) != 20:
        raise ValueError('Current scope must contain 20 unique groups')
    if len(qs) != 41 or len({q['question_id'] for q in qs}) != 41:
        raise ValueError('Current scope must contain 41 unique Choices')
    for g in groups:
        for q in g['questions']:
            if set(q['question']) != {'type', 'instructions', 'criteria'}:
                raise ValueError('Unexpected Choice fields')
            if not q['case_ids'] or not all(isinstance(v, str) for v in q['question']['criteria'].values()):
                raise ValueError('Invalid Choice mapping')
    for c in cases:
        mapped = [q['question_id'] for q in qs if c['case_id'] in q['case_ids']]
        if mapped != original['case_question_map'][c['case_id']]:
            raise ValueError('Case/Choice mapping mismatch: ' + c['case_id'])
    return groups


def bundle(group):
    """Identical evidence and candidate content for every provider; opaque keys."""
    questions, mapping = {}, {}
    states = [q['state'] for q in group['questions']]
    shared = all(s == states[0] for s in states)
    state = states[0] if shared else {'contexts': {f'q{i+1}': s for i, s in enumerate(states)}}
    for i, q in enumerate(group['questions']):
        key = f'q{i+1}'
        questions[key] = dict(q['question'])
        if not shared:
            questions[key]['instructions'] = f'Use only state.contexts.{key}. ' + questions[key]['instructions']
        mapping[key] = q['question_id']
    packet = {'state': state, 'questions': questions}
    reject_reference_fields(packet)
    return packet, mapping


def inventory(groups):
    rows = []
    for g in groups:
        for i, q in enumerate(g['questions']):
            gid, qid = g['group_id'], q['question_id']
            rows.append({'group_id': gid, 'question_id': qid, 'case_ids': q['case_ids'],
                         'package': g['package'], 'route': g['route'], 'engineering': q['engineering'],
                         'source_ids': g['source_ids'], 'source_families': g['source_families'],
                         'input_file': g['input_file'], 'group_pointer': g['input_pointer'],
                         'input_pointer': q['input_pointer'],
                         'recent_independent_review': gid in INDEPENDENT_REVIEW_GROUPS,
                         'reference_file': g['input_file'].replace('inputs.json', 'evaluation.json'),
                         'reference_locator': q['reference_pointer'],
                         'derivation': 'original_cases' if g['package'] == 'original' else gid})
    return {'split': 'reviewed_development', 'groups': len(groups), 'choices': len(rows),
            'scientific_choices': sum(not r['engineering'] for r in rows), 'engineering_choices': 1,
            'scientific_claims': 25, 'engineering_cases': 1,
            'source_records': len({s for g in groups for s in g['source_ids']}),
            'source_families': len({s for g in groups for s in g['source_families']}),
            'recent_independent_review_groups': len(INDEPENDENT_REVIEW_GROUPS),
            'recent_independent_review_choices': sum(r['recent_independent_review'] for r in rows),
            'route_choices': dict(Counter(r['route'] for r in rows)),
            'route_groups': dict(Counter(g['route'] for g in groups)), 'rows': rows}
