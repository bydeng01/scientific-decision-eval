"""Deterministic accounting conditional on supplied Choices; no answer-key reads."""
from collections import defaultdict
import re
from common import OLD, BIO, module

old_rules = module('s2_original_rules', OLD / 'rules.py')
bio_rules = module('s2_biology_derivation', BIO / 'derive.py')


def validate_answers(group, answers):
    questions = {q['question_id']: q['question']['criteria'] for q in group['questions']}
    if set(answers) != set(questions):
        raise ValueError('missing_or_extra_answers')
    if any(not isinstance(a, str) or a not in questions[q] for q, a in answers.items()):
        raise ValueError('invalid_option')


def stop(status):
    return {'status': status, 'output': None, 'final_label': None}


def compare(actual, claimed):
    return 'insufficient_evidence' if actual is None else 'consistent' if actual == claimed else 'inconsistent'


def compose(clauses):
    return bio_rules.compose(clauses)


def old_answer(q):
    state = q['state']
    extraction = old_rules.extract(state['evidence_text'], state['target_treatment'], state['scope'])
    if extraction['status'] != 'parsed':
        raise ValueError('zero_call_parser_unresolved')
    r, qid = extraction['relation'], q['question_id']
    field = qid.split('.')[-1]
    if qid.startswith('D03.'):
        option = r['atoms'][field]
    elif field == 'membership':
        parents = [p for _, p in r['memberships']]
        n = len(set(parents))
        option = 'shared' if n == 1 else 'distinct' if n == len(parents) else 'partly_shared'
    elif field == 'identifier':
        if [row['part'] for row in r['scan_rows']] != [p for _, p in r['memberships']]:
            raise ValueError('event identifier mismatch')
        option = 'part_id'
    else:
        option = {'column': 'column_region', 'treated_whole_sample': 'whole_specimen'}.get(r['unit'], r['unit'])
        if option not in q['question']['criteria']:
            option = 'other'
    return option, extraction['evidence_audit']


# Deliberately narrow development grammar. Every evidence block must match in
# full; a new clause, negation or conflicting account cannot inherit an answer.
ZERO_PATTERNS = {
    'E001': [
        r'Each implant setting processes (?P<n>\w+) wafers together\. After all implant batches, every anneal batch receives one wafer from each implant batch and is annealed at its assigned D/E/F setting\. Thus annealing regroups the wafers\. The first implant setting executed is 3 and the first anneal setting executed is 5; treatment codes are not execution-order indices\.',
        r'The handbook assigns implant effects to implant batches, anneal effects to anneal batches, and cross-stage interactions to individual wafers\. The figure is one block or replicate\. Without replicated blocks, it describes using A\*B\*C and D\*E\*F as error terms only under models excluding those three-factor interactions; each then supplies one degree of freedom\.'],
    'E002': [
        r'Measurements are downsampled to one-minute records\. Figure 5 switches SMV6 between baseline and wake-steering control hourly\. The offset within controlled periods follows the wind-dependent controller schedule; hourly mode assignment is different from instantaneous yaw offset\.',
        r'After operational and power-curve filtering, the first ten minutes after each mode switch are removed for yaw-controller transients\. Further power and lidar-availability filters apply to yaw analyses\. The authors bootstrap one-minute observations at least 2,000 times, by wind-direction bin where applicable, resampling baseline and controlled observations separately\.'],
    'E003': [
        r'The recycling reaction uses 2a \(0\.25 mmol\), 3a \(0\.38 mmol\), catalyst \(10 mg, 5 mol%\), and t-BuOH/water \(1:1\) at 70 degrees C for two hours\. Solids are separated, washed, and the recovered catalyst is used in the next cycle\. Figure 2 reports (?P<cycles>\w+) consecutive cycles with high endpoint conversion\.',
        r'The source reports that reaction rates begin to decrease after two cycles, despite completion before the two-hour endpoint\. Figure 3 distinguishes C1, C2, and C3\. Catalyst synthesis is described separately from recovery and reuse\.'],
    'E008': [
        r'The ethylene experiment uses 20 runs and eight process factors\. The authors prepare a fresh salt sample for each run and clean the vessel\. Oxidation and regeneration steps include gas collection\. Table 7 treats each column as a run; the preceding text explicitly describes the arrangement as replicates and foldover pairs\. The source reports p=2 pure-error degrees of freedom and f=1 fake-factor degree of freedom\.',
        r'Foldover reverses coded factor signs to create additional treatment settings and address aliasing\. Complementary settings can belong to a foldover pair without being the same complete treatment condition\. The full Table 7 transcription is supplied below; no repeated columns are removed\.']}


def zero_answers(group):
    if group['route'] != 'code':
        return {'status': 'unresolved_by_code', 'answers': {}, 'audit': []}
    if group['package'] == 'original':
        answers, audit = {}, []
        for q in group['questions']:
            answers[q['question_id']], evidence = old_answer(q)
            audit.append({'question_id': q['question_id'], 'matched_evidence': evidence})
    else:
        p, gid = group['problem'], group['group_id']
        patterns = ZERO_PATTERNS[gid]
        if len(p['evidence']) != len(patterns):
            raise ValueError('zero_call_parser_unresolved')
        audit = []
        for ev, pattern in zip(p['evidence'], patterns):
            match = re.fullmatch(pattern, ev['text'])
            if not match:
                raise ValueError('zero_call_parser_unresolved: ' + gid)
            audit.append({'pattern': pattern, 'matched_text': ev['text'], 'captures': match.groupdict()})
        options = {'E001': ['crossed_regrouping', 'wafer'],
                   'E002': ['hourly_switch', 'transition_exclusion'],
                   'E003': ['recovered_carryover'],
                   'E008': ['complete_setting_equality']}[gid]
        answers = dict(zip([q['question_id'] for q in group['questions']], options))
        if gid == 'E001' and old_rules.number(audit[0]['captures']['n']) != len(p['records']['anneal_setting_codes']):
            raise ValueError('wafer count/record conflict')
    validate_answers(group, answers)
    return {'status': 'resolved', 'answers': answers, 'audit': audit}


def derive_original(group, answers):
    """Retain the original claim labels and the separate omission-check branch."""
    outcomes = {}
    for case in group['cases']:
        qs = [q for q in group['questions'] if case['case_id'] in q['case_ids']]
        selected = {q['question_id']: answers[q['question_id']] for q in qs}
        values = list(selected.values())
        if any(v in {'conflicting', 'conflicting_assignment'} for v in values):
            outcomes[case['case_id']] = stop('evidence_conflict')
            continue
        if case.get('engineering'):
            outcomes[case['case_id']] = {'engineering': {'choice': values[0],
                'action': 'complete_candidates_or_transfer' if values[0] == 'other' else 'review_input_or_parser',
                'downstream_count': None}}
            continue
        if 'other' in values:
            outcomes[case['case_id']] = stop('candidate_completion_required')
            continue
        state = qs[0]['state']
        ext = old_rules.extract(state['evidence_text'], case['target_treatment'], case['scope'])
        if ext['status'] != 'parsed':
            raise ValueError('original record extraction failed')
        # These finite Choices do not supply a new membership table. A distinct
        # or partly shared counterfactual must not reuse the original parents.
        if group['group_id'] == 'D03':
            result = {'count': None, 'label': 'insufficient',
                      'action': 'request_run_boundary_and_specimen_run_records'}
            if all(v not in {'not_stated', 'partial_identification', 'partial_assignment'} for v in values):
                result = stop('membership_records_required')
        elif any(v in {'not_stated', 'partly_shared'} for v in values):
            result = stop('insufficient_evidence')
        else:
            r = ext['relation']
            unit = next((v for k, v in selected.items() if k.endswith('.unit')), None)
            count = None
            unit_map = {'column_region': 'column', 'whole_specimen': 'treated_whole_sample'}
            if unit_map.get(unit, unit) == r['unit']:
                count = len({p for _, p in r['memberships']})
                if 'distinct' in values:
                    count = len(r['entities'].get('prism', r['memberships']))
            elif unit in r['entities']:
                count = len(set(r['entities'][unit]))
            elif unit == 'strip':
                count = len(r['memberships'])
            elif unit == 'whole_plot_group':
                count = int(bool(r['memberships']))
            if group['group_id'] == 'C02' and unit == 'wear_event':
                field = answers['C02.identifier']
                rows = r['scan_rows']
                keys = {'part_id': lambda x: x['part'], 'cutter_character': lambda x: x['part'][0],
                        'scar_character': lambda x: x['part'][1:], 'operator': lambda x: x['operator'],
                        'scan_row': lambda x: x['row']}
                count = len({keys[field](x) for x in rows})
            counts = {'target': count, **{k: len(set(v)) for k, v in r['entities'].items()}}
            clauses = {k: compare(counts.get(k), v) for k, v in case['declared_counts'].items()}
            label = {'consistent': 'supported', 'inconsistent': 'inconsistent',
                     'insufficient_evidence': 'insufficient'}[compose(clauses)]
            result = {'count': count, 'label': label, 'action': {
                'supported': 'accept_scoped_claim', 'inconsistent': 'revise_scoped_claim',
                'insufficient': 'request_run_boundary_and_specimen_run_records'}[label]}
        outcomes[case['case_id']] = result
    return {'status': 'derived', 'cases': outcomes}


def derive_nonbio(p, answers):
    pid, r = p['problem_id'], p['records']
    a = [answers[q['question_id']] for q in p['questions']]
    x, y = a[0], a[1] if len(a) > 1 else None
    clauses = {}
    if pid == 'E001':
        ni, na, w = len(r['implant_setting_codes']), len(r['anneal_setting_codes']), r['wafers_per_intersection']
        crossed = x == 'crossed_regrouping'
        cells = ni * na if crossed else None
        out = dict(implant_batches=ni, anneal_batches=na, wafer_records=ni*na*w,
                   full_setting_combinations=cells, wafers_per_full_setting=w if crossed else None,
                   complete_blocks=r['illustrated_blocks'])
        clauses = {'per_setting_replicates': compare(out['wafers_per_full_setting'], 8),
                   'interaction_unit': 'consistent' if y == 'wafer' else 'inconsistent'}
    elif pid == 'E002':
        out = {'actual_eligible_application_count': None, 'minute_rows_are_new_assignments': x == 'minute_randomization'}
        clauses = {'new_minute_assignments': 'consistent' if out['minute_rows_are_new_assignments'] else 'inconsistent'}
    elif pid == 'E003':
        match = re.search(r'Figure 2 reports (\w+) consecutive cycles', p['evidence'][0]['text'])
        n = old_rules.number(match[1])
        out = {'reported_reaction_cycles': n, 'documented_recycling_series': 1 if x == 'recovered_carryover' else 0,
               'independent_synthesis_count_established_by_cycles': n if x == 'fresh_preparation' else None}
        clauses = {'fresh_preparation_per_cycle': 'consistent' if x == 'fresh_preparation' else 'inconsistent'}
    elif pid == 'E004':
        out = {'exact_parent_lot_count': None, 'complete_assignment_available': y == 'complete_assignment'}
        clauses = {'single_history': 'inconsistent' if x == 'mixed_histories' else 'consistent' if x == 'one_common_history' else 'inconsistent',
                   'exact_assignments': 'consistent' if y == 'complete_assignment' else 'insufficient_evidence'}
    elif pid == 'E005':
        start, step = r['starting_stress_MPa'], r['step_MPa']
        out = {'next_stress_after_initial_failure_MPa': start-step if x == 'response_adaptive' else start if x == 'fixed_level' else None,
               'next_stress_after_initial_runout_MPa': start+step if x == 'response_adaptive' else start if x == 'fixed_level' else None,
               'observed_replicates_at_any_fixed_stress': None}
        clauses = {'independently_randomized_stresses': 'consistent' if x == 'independent_randomization' else 'inconsistent'}
    elif pid == 'E006':
        n = r['paired_realizations']; executions = n*r['executions_per_paired_realization']
        out = {'paired_realizations': n, 'paired_execution_count': executions,
               'values_entering_pair_ensemble': executions if y == 'individual_execution' else 1 if y == 'all_runs_average' else n}
        clauses = {'independent_phase_draws': 'consistent' if x == 'independent_draws' else 'inconsistent'}
    elif pid == 'E007':
        n0 = len(r['macro_start_dates'])*r['original_micro_members_per_date']+len(r['original_extra_start_years'])
        n1 = len(r['macro_start_dates'])*r['smbb_micro_members_per_date']+len(r['smbb_extra_start_years'])
        total = n0+n1
        out = {'original_members': total if x == 'all_original' else 0 if x == 'all_smbb' else n0 if x == 'two_protocol_groups' else None,
               'smbb_members': total if x == 'all_smbb' else 0 if x == 'all_original' else n1 if x == 'two_protocol_groups' else None,
               'total_members': total, 'smoothing_only_contrast': y == 'smoothing_only'}
        clauses = {'single_protocol': 'consistent' if x == 'all_original' else 'inconsistent',
                   'single_change': 'consistent' if y == 'smoothing_only' else 'inconsistent'}
    elif pid == 'E008':
        bins = defaultdict(list)
        if x != 'complete_setting_equality':
            # Non-equivalence proposals do not define exact replication. Do
            # not silently apply equality after the selected relation was wrong.
            return stop('exact_replication_relation_not_selected')
        for row in r['runs']:
            bins[tuple(row['factor_settings'])].append(row['column'])
        out = {'run_count': len(r['runs']), 'distinct_complete_settings': len(bins),
               'repeated_column_groups': sorted(v for v in bins.values() if len(v)>1),
               'singleton_settings': sum(len(v)==1 for v in bins.values()),
               'pure_error_df': sum(len(v)-1 for v in bins.values())}
        clauses = {'ten_settings_twice_each': 'consistent' if len(bins)==10 and all(len(v)==2 for v in bins.values()) else 'inconsistent'}
    elif pid == 'E009':
        out = {'compared_laboratory_results': 3 if y == 'two_laboratories' else 2,
               'calibration_visits': 3,
               'shared_covariance_term': '2*u_B(std_DCV)^2' if x == 'shared_reference' else '0' if x == 'independent_reference' else None,
               'exact_effective_replication_count': None}
        clauses = {'drop_shared_covariance': 'consistent' if x == 'independent_reference' else 'inconsistent'}
    elif pid == 'E010':
        n = r['initial_EUs']-r['precipitation_QC_exclusions']-r['generator_exclusions']
        if n != r['reported_retained_EUs']:
            raise ValueError('author-reported totals inconsistent with supplied records')
        out = {'original_EUs': r['initial_EUs'], 'retained_EUs': n,
               'joint_assignment_events': n if x in {'complementary_assignment', 'both_seeded'} else 0 if x == 'permanent_range' else None,
               'range_level_records': n*r['ranges_per_EU'], 'independent_range_draws_claim': x == 'independent_assignments'}
        clauses = {'independent_assignment': 'consistent' if x == 'independent_assignments' else 'inconsistent',
                   'zero_exposure': 'consistent' if y == 'zero_exposure_established' else 'insufficient_evidence' if y == 'assignment_only' else 'inconsistent'}
    else:
        raise ValueError('unknown nonbio group')
    label = compose(clauses)
    # Preserve the reviewed compound-label spelling in the reference projection.
    assessment = label
    if pid == 'E004' and clauses == {'single_history': 'inconsistent', 'exact_assignments': 'insufficient_evidence'}:
        assessment = 'inconsistent_single_history; insufficient_exact_assignments'
    if pid == 'E007' and all(v == 'inconsistent' for v in clauses.values()):
        assessment = 'inconsistent_in_both_clauses'
    if pid == 'E010' and clauses == {'independent_assignment': 'inconsistent', 'zero_exposure': 'insufficient_evidence'}:
        assessment = 'inconsistent_independent_assignment; zero_exposure_not_established_by_label'
    out['claim_assessment'] = assessment
    return {'status': 'derived', 'output': out, 'clauses': clauses, 'final_label': label}


def derive(group, answers):
    validate_answers(group, answers)
    if group['package'] == 'original':
        return derive_original(group, answers)
    if group['package'] == 'biology':
        return bio_rules.derive(group['problem'], answers)
    for value, status in [('conflicting', 'evidence_conflict'), ('other', 'candidate_completion_required'),
                          ('not_stated', 'insufficient_evidence')]:
        if value in answers.values():
            return stop(status)
    return derive_nonbio(group['problem'], answers)
