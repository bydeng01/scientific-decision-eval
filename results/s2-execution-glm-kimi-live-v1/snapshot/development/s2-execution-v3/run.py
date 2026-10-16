"""Prepare, verify, simulate, resume and score the current S2 development suite."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import fcntl
import json
import math
import platform
import random
import shutil
import subprocess
import statistics
import sys
import time
from pathlib import Path

from common import BASE, ROOT, OLD, NONBIO, BIO, digest, encoded, loads, module, read, sha, write_new
from dataset import bundle, inventory, load_inputs
from derive import derive, zero_answers
from providers import ENDPOINTS, ResponseError, http_transport, parse_response, request_body, usage_record


def now():
    return datetime.now(timezone.utc).isoformat()


def config_check(config):
    if config['budget']['cap_usd'] is not None or config['budget']['historical_caps_apply']:
        raise ValueError('This development configuration supersedes historical monetary caps')
    for key, value in [('concurrency', 1), ('max_retries', 0), ('max_fallbacks', 0)]:
        if config[key] != value:
            raise ValueError(f'{key} is unsupported by this first-attempt runner')
    if type(config['repetitions']) is not int or config['repetitions'] < 1:
        raise ValueError('invalid repetitions')
    ids = [m['id'] for m in config['models']]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('duplicate or empty model roster')
    for model in config['models']:
        if model['provider'] not in ENDPOINTS or not model['accepted_response_models']:
            raise ValueError('unsupported model contract')
        if model['provider'] == 'openrouter_chat':
            if not model.get('provider_slug') or not model.get('accepted_response_providers'):
                raise ValueError('OpenRouter Chat requires a fixed upstream provider')


def dependencies():
    files = [ROOT/'JEV_SCIENCE_CONTRIBUTION_V1.md', ROOT/'scripts/configure_science_keys.py']
    for folder in (OLD, NONBIO, BIO):
        files += [p for p in folder.rglob('*') if p.is_file() and not {'history', '__pycache__'} & set(p.parts)]
    files += [p for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}


def matrix(groups, config):
    jobs = []
    routed = [g for g in groups if g['route'] == 'model']
    rng = random.Random(config['schedule_seed'])
    for repeat in range(config['repetitions']):
        ordered = routed.copy()
        rng.shuffle(ordered)
        for i, g in enumerate(ordered):
            offset = (repeat+i) % len(config['models'])
            models = config['models'][offset:] + config['models'][:offset]
            packet, mapping = bundle(g)
            for m in models:
                body = request_body(m, packet)
                if len(encoded(body)) > config['request_size_limit_bytes']:
                    raise ValueError('request size guard exceeded')
                job = {'job_id': f"r{repeat+1:02d}-{g['group_id']}-{m['id']}",
                       'repeat': repeat, 'group_id': g['group_id'], 'model_id': m['id'],
                       'endpoint': ENDPOINTS[m['provider']], 'packet': packet,
                       'question_map': mapping, 'request': body, 'request_sha256': digest(body)}
                jobs.append(job)
    return {'condition': 'model_semantics_plus_code', 'requests': len(jobs),
            'semantic_answers': sum(len(j['question_map']) for j in jobs),
            'max_attempts': len(jobs), 'retries': 0, 'fallbacks': 0, 'jobs': jobs}


def run_code(groups):
    rows = []
    for g in groups:
        start, cpu = time.perf_counter(), time.process_time()
        resolved = zero_answers(g)
        result = derive(g, resolved['answers']) if resolved['status'] == 'resolved' else None
        rows.append({'group_id': g['group_id'], **resolved, 'derived': result,
                     'wall_seconds': time.perf_counter()-start, 'cpu_seconds': time.process_time()-cpu,
                     'model_calls': 0, 'api_cost_usd': 0})
    return rows


def prepare(output, config_path=BASE/'config.json', mode='live'):
    if output.exists():
        raise ValueError('Output already exists; use run to resume, or choose a new directory')
    start = time.perf_counter()
    config = read(config_path)
    config_check(config)
    groups = load_inputs()
    inv, plan, code = inventory(groups), matrix(groups, config), run_code(groups)
    # This import and reference read happen after request assembly and code prediction.
    from scoring import load_references, oracle
    refs = load_references(groups)
    oracle_started = time.perf_counter()
    oracle_result = oracle(groups, refs)
    oracle_result['wall_seconds'] = time.perf_counter()-oracle_started
    if oracle_result['groups_correct'] != oracle_result['groups_denominator']:
        failed = [r['group_id'] for r in oracle_result['rows'] if not r['exact']]
        raise ValueError('oracle derivation failed: ' + ', '.join(failed))
    source_hashes = dependencies()
    output.mkdir(parents=True, exist_ok=False)
    mapping = [{**row, 'reference_option': refs['answers'][row['question_id']],
                'reference_downstream': refs['outcomes'][row['group_id']],
                'oracle_output_locator': f"evaluation_only/oracle.json#/rows/{next(i for i, g in enumerate(groups) if g['group_id']==row['group_id'])}/derived"}
               for row in inv['rows']]
    for name, data in [('config.json', config), ('inputs.json', groups), ('inventory.json', inv),
                       ('plan.json', plan), ('code_predictions.json', code),
                       ('evaluation_only/references.json', refs), ('evaluation_only/oracle.json', oracle_result),
                       ('evaluation_only/mapping.json', mapping)]:
        write_new(output/name, data)
    # Preserve executable code and the direct input/evaluation sources as bytes.
    # Large source assets stay at their archived paths and are bound by hashes.
    for relative in source_hashes:
        p = ROOT/relative
        if p.suffix in {'.py', '.json', '.md'}:
            dest = output/'snapshot'/relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
    version = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    artifacts = {str(p.relative_to(output)): sha(p) for p in output.rglob('*') if p.is_file()}
    write_new(output/'manifest.json', {'created_at': now(), 'mode': mode,
        'status': 'development_execution_snapshot_not_protocol_freeze', 'source_sha256': source_hashes,
        'artifact_sha256': artifacts, 'config_sha256': digest(config),
        'git_head': version.stdout.strip() if version.returncode == 0 else None,
        'git_status': 'head_recorded_files_authoritative' if version.returncode == 0 else 'unavailable_not_a_git_checkout',
        'python': sys.version, 'platform': platform.platform(),
        'preparation_wall_seconds': time.perf_counter()-start,
        'unmeasured_resources': ['historical source localization', 'human review', 'adaptation and implementation time',
                                 'development tool tokens/cost', 'local compute cost'],
        'api_calls_during_preparation': 0})
    return {'output': str(output), **{k: v for k, v in inv.items() if k != 'rows'},
            'planned_requests': plan['requests'], 'planned_semantic_answers': plan['semantic_answers']}


def verify(output):
    manifest = read(output/'manifest.json')
    for relative, expected in manifest['source_sha256'].items():
        if sha(ROOT/relative) != expected:
            raise ValueError('Source changed since preparation: ' + relative)
    for relative, expected in manifest['artifact_sha256'].items():
        if sha(output/relative) != expected:
            raise ValueError('Prepared artifact changed: ' + relative)
    plan, config = read(output/'plan.json'), read(output/'config.json')
    config_check(config)
    if plan != matrix(read(output/'inputs.json'), config):
        raise ValueError('Prepared requests differ from reproducible assembly')
    return manifest


def fake_transport(model, packet, repeat):
    """Format fixtures use option order, never reference answers."""
    answers = {k: list(q['criteria'])[(repeat+i) % len(q['criteria'])]
               for i, (k, q) in enumerate(packet['questions'].items())}
    obj = {'id': 'offline-fixture', 'model': model['accepted_response_models'][0],
           'usage': {'input_tokens': 0, 'output_tokens': 0, 'cost': 0}}
    if model['provider'] == 'openrouter':
        obj.update(provider='TypeSafe', answers={k: {'type': 'choice', 'choice': a, 'confidence': 1,
            'probabilities': {option: int(option == a) for option in packet['questions'][k]['criteria']}}
                                                 for k, a in answers.items()})
    elif model['provider'] == 'openai':
        obj.update(status='completed', output=[{'type': 'message', 'content': [
            {'type': 'output_text', 'text': json.dumps(answers)}]}])
    elif model['provider'] == 'openrouter_chat':
        obj.update(provider=model['accepted_response_providers'][0],
                   choices=[{'index': 0, 'finish_reason': 'stop', 'message': {
                       'role': 'assistant', 'content': json.dumps(answers)}}],
                   usage={'prompt_tokens': 0, 'completion_tokens': 0, 'cost': 0})
    else:
        obj.update(stop_reason='end_turn', content=[{'type': 'text', 'text': json.dumps(answers)}])
    return {'http_status': 200, 'raw_body': json.dumps(obj), 'response_headers': {},
            'latency_seconds': 0, 'transport_error': None, 'simulated': True}


def finish(job, model, group, receipt):
    errors, answers, diagnostics = {}, {}, {}
    response = None
    failure = None
    if receipt['transport_error']:
        failure = 'transport_uncertain'
    else:
        if receipt['http_status'] != 200:
            failure = f"http_{receipt['http_status']}"
        try:
            response = loads(receipt['raw_body'])
            if failure is None:
                parsed = parse_response(model, job['packet'], response)
                answers = {job['question_map'][k]: v for k, v in parsed['answers'].items()}
                errors = {job['question_map'][k]: v for k, v in parsed['errors'].items()}
                diagnostics = {job['question_map'][k]: v for k, v in parsed['diagnostics'].items()}
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            failure = failure or (str(exc) if isinstance(exc, ResponseError) else 'malformed_response')
    if failure:
        errors = {qid: failure for qid in job['question_map'].values()}
    start, cpu = time.perf_counter(), time.process_time()
    result = derive(group, answers) if not errors else None
    return {'job_id': job['job_id'], 'group_id': job['group_id'], 'model_id': model['id'],
            'repeat': job['repeat'], 'answers': answers, 'errors': errors, 'derived': result,
            'diagnostics': diagnostics, 'status': 'complete' if not errors else 'failed',
            'served_model': response.get('model') if isinstance(response, dict) else None,
            'served_provider': response.get('provider') if isinstance(response, dict) else None,
            'response_id': response.get('id') if isinstance(response, dict) else None,
            'resources': {**usage_record(model, response), 'latency_seconds': receipt['latency_seconds'],
                          'derivation_wall_seconds': time.perf_counter()-start,
                          'derivation_cpu_seconds': time.process_time()-cpu},
            'request_sha256': job['request_sha256'], 'receipt_sha256': digest(receipt),
            'simulated': receipt.get('simulated', False),
            'halt_model': receipt['http_status'] in {400, 401, 402, 403, 404, 413} or failure in {'model_version_mismatch', 'provider_mismatch'}}


def execute(output, live=False, limit=None, transport=None):
    manifest = verify(output)
    simulated = manifest['mode'] == 'dry-run'
    if live == simulated:
        raise ValueError('Live mode requires --live and a live preparation; dry-run artifacts cannot be used live')
    config, plan = read(output/'config.json'), read(output/'plan.json')
    groups = {g['group_id']: g for g in read(output/'inputs.json')}
    models = {m['id']: m for m in config['models']}
    keys = {}
    if live and transport is None:
        credentials = module('s2_credentials', ROOT/'scripts/configure_science_keys.py')
        keys = {m['provider']: credentials.load_key(m.get('credential_provider', m['provider'])) for m in models.values()}
        missing = [p for p, key in keys.items() if not key]
        if missing:
            raise ValueError('Missing local API credentials: ' + ', '.join(missing))
    with (output/'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        validate_attempts(output)
        halted, new_attempts, recovered = set(), 0, 0
        for job in plan['jobs']:
            directory = output/'attempts'/job['job_id']
            result_path, receipt_path, intent_path = [directory/name for name in ('prediction.json', 'receipt.json', 'intent.json')]
            if result_path.exists():
                result = read(result_path)
                if result['request_sha256'] != job['request_sha256'] or not receipt_path.exists() or result['receipt_sha256'] != digest(read(receipt_path)):
                    raise ValueError('Existing attempt integrity mismatch: ' + job['job_id'])
                if result['halt_model']:
                    halted.add(job['model_id'])
                continue
            model = models[job['model_id']]
            if intent_path.exists():
                intent = read(intent_path)
                if intent['request_sha256'] != job['request_sha256'] or intent['request'] != job['request']:
                    raise ValueError('Existing intent differs from prepared request')
                if not receipt_path.exists():
                    write_new(receipt_path, {'http_status': None, 'raw_body': None, 'response_headers': {},
                        'latency_seconds': None, 'transport_error': 'InterruptedWithoutReceipt', 'simulated': simulated})
                recovered += 1
            else:
                if job['model_id'] in halted or (limit is not None and new_attempts >= limit):
                    continue
                if receipt_path.exists():
                    raise ValueError('Receipt has no matching request intent')
                write_new(intent_path, {'started_at': now(), 'request_sha256': job['request_sha256'],
                    'request': job['request'], 'endpoint': job['endpoint'], 'job_id': job['job_id'],
                    'attempt': 1, 'repeat': job['repeat'], 'simulated': simulated})
                if simulated:
                    receipt = fake_transport(model, job['packet'], job['repeat'])
                else:
                    print(json.dumps({'event': 'request_started', 'job_id': job['job_id'],
                                      'started_at': now()}, ensure_ascii=False), flush=True)
                    receipt = (transport or http_transport)(model, job['request'], keys.get(model['provider'], ''), config['timeout_seconds'])
                receipt['received_at'] = now()
                write_new(receipt_path, receipt)
                new_attempts += 1
            result = finish(job, model, groups[job['group_id']], read(receipt_path))
            write_new(result_path, result)
            if live:
                print(json.dumps({'event': 'request_finished', 'job_id': job['job_id'],
                                  'status': result['status'], 'failures': sorted(set(result['errors'].values())),
                                  'latency_seconds': result['resources']['latency_seconds']}, ensure_ascii=False), flush=True)
            if result['halt_model']:
                halted.add(job['model_id'])
        report = report_run(output)
    return {'new_attempts': new_attempts, 'recovered_without_call': recovered,
            'real_api_calls_this_invocation': 0 if simulated else new_attempts,
            'halted_models': sorted(halted), 'report': str(report)}


def validate_attempts(output):
    """Reparse saved receipts offline before trusting persisted predictions."""
    jobs = {j['job_id']: j for j in read(output/'plan.json')['jobs']}
    models = {m['id']: m for m in read(output/'config.json')['models']}
    groups = {g['group_id']: g for g in read(output/'inputs.json')}
    rows, response_ids = [], set()
    for directory in sorted((output/'attempts').glob('*')):
        if not directory.is_dir() or directory.name not in jobs:
            raise ValueError('Unplanned attempt artifact: ' + directory.name)
        job = jobs[directory.name]
        intent = read(directory/'intent.json')
        if intent['request'] != job['request'] or intent['request_sha256'] != job['request_sha256']:
            raise ValueError('Attempt intent changed')
        if not (directory/'prediction.json').exists():
            continue
        receipt = read(directory/'receipt.json')
        actual = read(directory/'prediction.json')
        expected = finish(job, models[job['model_id']], groups[job['group_id']], receipt)
        for key in expected:
            if key != 'resources' and actual.get(key) != expected[key]:
                raise ValueError('Persisted prediction differs from saved receipt: ' + job['job_id'])
        for key in expected['resources']:
            if key not in {'derivation_wall_seconds', 'derivation_cpu_seconds'} and actual['resources'].get(key) != expected['resources'][key]:
                raise ValueError('Persisted usage differs from saved receipt')
        rid = actual['response_id']
        if rid and not actual['simulated']:
            identity = (models[job['model_id']]['provider'], rid)
            if identity in response_ids:
                raise ValueError('Duplicate provider response ID across logical requests')
            response_ids.add(identity)
        rows.append(actual)
    return rows


def report_run(output):
    from scoring import score_lane
    start = time.perf_counter()
    groups, config = read(output/'inputs.json'), read(output/'config.json')
    refs = read(output/'evaluation_only/references.json')
    code = read(output/'code_predictions.json')
    manifest = read(output/'manifest.json')
    records = validate_attempts(output)
    resources = {}
    for model in config['models']:
        rows = [r for r in records if r['model_id'] == model['id']]
        res = {'attempts': len(rows), 'failed_requests': sum(r['status'] == 'failed' for r in rows),
               'failure_types': dict(Counter(e for r in rows for e in set(r['errors'].values()))),
               'resource_error_types': dict(Counter(e for r in rows for e in r['resources']['resource_errors'])),
               'served_models': sorted({r['served_model'] for r in rows if r['served_model']}),
               'served_providers': sorted({r['served_provider'] for r in rows if r['served_provider']}),
               'latency_seconds': [r['resources']['latency_seconds'] for r in rows]}
        latencies = sorted(v for v in res['latency_seconds'] if v is not None)
        res['latency_summary_seconds'] = ({'mean': statistics.mean(latencies), 'median': statistics.median(latencies),
            'p95_nearest_rank': latencies[math.ceil(.95*len(latencies))-1], 'min': latencies[0], 'max': latencies[-1]}
            if latencies else None)
        for field in ('input_tokens', 'output_tokens', 'cached_input_tokens', 'cache_creation_tokens',
                      'reasoning_tokens', 'reported_cost_usd', 'usage_cost_estimate_usd', 'usage_cost_upper_estimate_usd'):
            values = [r['resources'][field] for r in rows]
            known = [v for v in values if v is not None]
            res[field] = {'known_subtotal': sum(known), 'missing_records': len(values)-len(known),
                          'total': sum(known) if values and len(known)==len(values) else None}
        resources[model['id']] = res
    metrics = {}
    if manifest['mode'] != 'dry-run':
        for model in config['models']:
            lane = {(rep, row['group_id']): row for rep in range(config['repetitions']) for row in code}
            lane.update({(r['repeat'], r['group_id']): r for r in records if r['model_id']==model['id']})
            metrics[model['id']] = score_lane(groups, refs, lane, config['repetitions'])
            completed = sum(r['model_id']==model['id'] for r in records)
            planned = sum(g['route']=='model' for g in groups)*config['repetitions']
            metrics[model['id']]['execution_completion'] = {'recorded_requests': completed, 'planned_requests': planned,
                'status': 'complete' if completed==planned else 'incomplete_fixed_denominator_scores_are_provisional'}
    code_lane = {(0, r['group_id']): r for r in code}
    report = {'created_at': now(), 'mode': manifest['mode'], 'split': 'reviewed_development',
              'model_quality_status': 'not_measured_simulated_responses' if manifest['mode']=='dry-run' else 'development_first_attempts',
              'model_scores': metrics if manifest['mode']!='dry-run' else None,
              'code_only': score_lane(groups, refs, code_lane, 1),
              'code_processing_seconds': {'wall': sum(r['wall_seconds'] for r in code), 'cpu': sum(r['cpu_seconds'] for r in code)},
              'oracle': {'groups_exact': read(output/'evaluation_only/oracle.json')['groups_correct'],
                         'denominator': 20, 'model_performance': False,
                         'wall_seconds': read(output/'evaluation_only/oracle.json')['wall_seconds']},
              'resource_records_are_simulated': manifest['mode']=='dry-run', 'resources_by_model': resources,
              'planned_requests': read(output/'plan.json')['requests'], 'completed_request_records': len(records),
              'real_api_attempts': len(records) if manifest['mode']!='dry-run' else 0,
              'retries': 0, 'fallbacks': 0, 'scoring_wall_seconds': time.perf_counter()-start,
              'cohort': config.get('cohort'),
              'attempt_artifact_sha256': {str(p.relative_to(output)): sha(p) for p in sorted((output/'attempts').rglob('*.json'))},
              'unmeasured_resources': manifest['unmeasured_resources'],
              'interpretation': 'Finite reviewed development inputs; no unseen-source generalization or independent sample size from repeats.'}
    directory = output/'reports'
    directory.mkdir(exist_ok=True)
    path = directory/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    write_new(path, report)
    return path


def source_checks():
    commands = [OLD/'choice-review-v1/verify_review.py', NONBIO/'verify_batch.py', BIO/'verify_batch.py',
                OLD/'test_preflight.py', OLD/'check_counts.py']
    checks = []
    for path in commands:
        proc = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT, text=True, capture_output=True)
        checks.append({'command': str(path.relative_to(ROOT)), 'returncode': proc.returncode,
                       'stdout': proc.stdout, 'stderr': proc.stderr})
        if proc.returncode:
            raise ValueError(json.dumps(checks[-1]))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'prepare', 'dry-run', 'verify', 'run', 'score'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--config', type=Path, default=BASE/'config.json')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error('--limit must be nonnegative')
    if args.command == 'check':
        checks = source_checks()
        tests = []
        for name in ('test_execution.py', 'test_extension.py'):
            test = subprocess.run([sys.executable, '-B', str(BASE/name)], cwd=ROOT, text=True, capture_output=True)
            if test.returncode:
                raise ValueError(test.stdout + test.stderr)
            tests.append({'file': name, 'output': test.stdout+test.stderr})
        result = {'source_checks': checks, 'execution_tests': tests, 'status': 'passed', 'api_calls': 0}
        if args.output:
            write_new(args.output, result)
    else:
        if args.output is None:
            parser.error('--output is required')
        output = args.output.resolve()
        if args.command in {'prepare', 'dry-run'}:
            result = prepare(output, args.config, 'dry-run' if args.command=='dry-run' else 'live')
            if args.command == 'dry-run':
                result['execution'] = execute(output)
        elif args.command == 'verify':
            verify(output)
            result = {'status': 'passed', 'api_calls': 0}
        elif args.command == 'run':
            result = execute(output, args.live, args.limit)
        else:
            verify(output)
            result = {'report': str(report_run(output))}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
