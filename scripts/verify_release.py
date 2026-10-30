"""Verify published files and reproduce saved S2 scores without network access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COHORTS = {
    'original': ('s2-execution-v1', 's2-execution-live-v1'),
    'extension': ('s2-execution-v2', 's2-execution-extension-live-v1'),
    'glm_kimi': ('s2-execution-v3', 's2-execution-glm-kimi-live-v1'),
}


def read(path):
    return json.loads(path.read_text())


def blocked(*args, **kwargs):
    raise RuntimeError('Release verification is offline')


def distributed_paths():
    if (ROOT / '.git').exists():
        result = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=ROOT, check=True, capture_output=True, text=True)
        return {name for name in result.stdout.split('\0') if name and (ROOT / name).is_file()}
    paths = set()
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in {
            '.git', '__pycache__', '.pytest_cache', '.venv', '.mplconfig'}]
        for name in files:
            if name != '.DS_Store':
                paths.add((Path(directory) / name).relative_to(ROOT).as_posix())
    return paths


def verify_files():
    manifest = read(ROOT / 'release-sha256.json')
    for relative, expected in manifest['files'].items():
        if '.local-development' in Path(relative).parts:
            raise ValueError('Local development archive included in release: ' + relative)
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Published file differs from release manifest: ' + relative)
    for relative in manifest.get('omitted_source_assets', []):
        if relative in manifest['files'] or (ROOT / relative).exists():
            raise ValueError('Source asset excluded from release is present: ' + relative)
    unexpected = distributed_paths() - set(manifest['files']) - {'release-sha256.json'}
    if unexpected:
        raise ValueError('Files outside the release manifest: ' + ', '.join(sorted(unexpected)))
    return len(manifest['files'])


def verify_cohort(name):
    package, directory = COHORTS[name]
    sys.path.insert(0, str(ROOT / 'development' / package))
    import run
    import providers
    from scoring import load_references, oracle, score_lane

    socket.socket = socket.create_connection = blocked
    run.http_transport = providers.http_transport = blocked
    path = ROOT / 'results' / directory
    groups, config, plan = (read(path / f'{n}.json') for n in ('inputs', 'config', 'plan'))
    assert groups == run.load_inputs(), 'Published inputs differ from executed inputs'
    assert plan == run.matrix(groups, config), 'Request assembly changed'
    refs = read(path / 'evaluation_only/references.json')
    assert refs == load_references(groups), 'Reference answers or outcomes changed'
    expected_oracle = read(path / 'evaluation_only/oracle.json')
    assert oracle(groups, refs) == {k: v for k, v in expected_oracle.items() if k != 'wall_seconds'}
    code = read(path / 'code_predictions.json')
    for saved, actual in zip(code, run.run_code(groups), strict=True):
        stable = lambda row: {k: v for k, v in row.items() if k not in {'wall_seconds', 'cpu_seconds'}}
        assert stable(saved) == stable(actual), 'Deterministic output changed'
    records = run.validate_attempts(path)
    assert len(records) == len(plan['jobs'])
    report = read(sorted((path / 'reports').glob('*.json'))[-1])
    for model in config['models']:
        lane = {(rep, row['group_id']): row for rep in range(config['repetitions']) for row in code}
        lane.update({(r['repeat'], r['group_id']): r for r in records if r['model_id'] == model['id']})
        actual = score_lane(groups, refs, lane, config['repetitions'])
        saved = report['model_scores'][model['id']]
        assert actual == {k: v for k, v in saved.items() if k != 'execution_completion'}, model['id']
        assert saved['execution_completion']['recorded_requests'] == sum(r['model_id'] == model['id'] for r in records)
    return {'cohort': name, 'requests_reparsed': len(records), 'models_rescored': len(config['models']),
            'request_assembly_identical': True, 'references_identical': True,
            'deterministic_outputs_identical': True, 'saved_scores_identical': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort', choices=COHORTS, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.cohort:
        print(json.dumps(verify_cohort(args.cohort)))
        return
    files = verify_files()
    validators = [
        'development/s2-nonbio-v1/choice-review-v1/verify_review.py',
        'development/s2-nonbio-expansion/batch-001/verify_batch.py',
        'development/s2-biology-expansion/batch-001/verify_batch.py',
    ]
    for name in validators:
        subprocess.run([sys.executable, '-B', str(ROOT / name), '--release'],
                       cwd=ROOT, check=True, capture_output=True, text=True)
    cohorts = []
    for name in COHORTS:
        result = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--cohort', name],
                                cwd=ROOT, check=True, capture_output=True, text=True)
        cohorts.append(json.loads(result.stdout))
    print(json.dumps({'status': 'passed', 'published_files_verified': files,
                      'content_packages_verified': len(validators), 'cohorts': cohorts,
                      'source_assets_omitted': read(ROOT / 'release-sha256.json').get('omitted_source_assets', []),
                      'network_calls': 0, 'result_files_written': 0}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit((exc.stdout or '') + (exc.stderr or ''))
