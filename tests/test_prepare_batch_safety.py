"""Initial preparation must never overwrite an existing review package."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECIPES = sorted(ROOT.rglob('prepare_batch.py'))


@pytest.mark.parametrize('recipe', RECIPES, ids=lambda p: str(p.relative_to(ROOT)))
@pytest.mark.parametrize('existing', [
    'inputs.json', 'evaluation.json', 'review_decisions.json',
    'sources.json',
])
def test_existing_package_is_not_overwritten(tmp_path, recipe, existing):
    spec = importlib.util.spec_from_file_location('prepare_batch_guard', recipe)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.B = tmp_path
    retained = tmp_path / existing
    retained.parent.mkdir(parents=True, exist_ok=True)
    retained.write_text('{"retained": true}\n')
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises(SystemExit, match='Refusing to overwrite'):
        module.main()
    after = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert before == after
