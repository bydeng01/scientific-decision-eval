"""The public checksum check must reject changed or missing published files."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'verify_release', Path(__file__).resolve().parents[1] / 'scripts/verify_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def prepared_release(tmp_path, monkeypatch):
    data = tmp_path / 'prediction.json'
    data.write_text('{"answer": "shared"}\n')
    manifest = {'files': {data.name: hashlib.sha256(data.read_bytes()).hexdigest()}}
    (tmp_path / 'release-sha256.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(release, 'ROOT', tmp_path)
    return data


def test_release_hashes_accept_original_files(tmp_path, monkeypatch):
    prepared_release(tmp_path, monkeypatch)
    assert release.verify_files() == 1


@pytest.mark.parametrize('change', ['modified', 'missing'])
def test_release_hashes_reject_changed_artifacts(tmp_path, monkeypatch, change):
    data = prepared_release(tmp_path, monkeypatch)
    if change == 'modified':
        data.write_text('{"answer": "separate"}\n')
    else:
        data.unlink()
    with pytest.raises(ValueError, match='prediction.json'):
        release.verify_files()


def test_release_rejects_restored_excluded_source(tmp_path, monkeypatch):
    prepared_release(tmp_path, monkeypatch)
    manifest_path = tmp_path / 'release-sha256.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['omitted_source_assets'] = ['source.pdf']
    manifest_path.write_text(json.dumps(manifest))
    assert release.verify_files() == 1
    (tmp_path / 'source.pdf').write_bytes(b'%PDF-1.4')
    with pytest.raises(ValueError, match='source.pdf'):
        release.verify_files()


@pytest.mark.parametrize('include_in_manifest', [False, True])
def test_release_rejects_restored_development_record(tmp_path, monkeypatch, include_in_manifest):
    prepared_release(tmp_path, monkeypatch)
    manifest_path = tmp_path / 'release-sha256.json'
    manifest = json.loads(manifest_path.read_text())
    name = 'snapshot/development/NOVELTY_AUDIT.md'
    manifest['omitted_development_records'] = [name]
    manifest_path.write_text(json.dumps(manifest))
    assert release.verify_files() == 1
    restored = tmp_path / name
    restored.parent.mkdir(parents=True)
    restored.write_text('Private screening notes.\n')
    if include_in_manifest:
        manifest['files'][name] = hashlib.sha256(restored.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='Development record excluded'):
        release.verify_files()


def test_release_rejects_local_archive_in_manifest(tmp_path, monkeypatch):
    prepared_release(tmp_path, monkeypatch)
    archive = tmp_path / '.local-development' / 'records.zip'
    archive.parent.mkdir()
    archive.write_bytes(b'local archive')
    manifest_path = tmp_path / 'release-sha256.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['files'][archive.relative_to(tmp_path).as_posix()] = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='Local development archive included'):
        release.verify_files()
