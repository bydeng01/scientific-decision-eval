from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from credit_diagnostic import credits


def test_only_matching_completed_nontransfer_unique_courses_count():
    base=dict(applicant="A",course="X",credits=12,completed=True,transfer=False)
    rows=[base,base.copy(),dict(base,course="Y",credits=11),dict(base,course="P",completed=False),
          dict(base,course="T",transfer=True),dict(base,applicant="B",course="Z",credits=99)]
    assert credits(dict(applicant_id="A",entries=rows))==23
    rows[2]["credits"]=12
    assert credits(dict(applicant_id="A",entries=rows))==24


def test_conflicting_duplicate_is_not_silently_repaired():
    a=dict(applicant="A",course="X",credits=12,completed=True,transfer=False)
    with pytest.raises(ValueError,match="Conflicting"):
        credits(dict(applicant_id="A",entries=[a,dict(a,credits=13)]))
