from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ui_snapshot import SNAPSHOT_PATH, build_ui_snapshot

pytestmark = [
    pytest.mark.filterwarnings(
        "ignore:\\*scattermapbox\\* is deprecated!.*:DeprecationWarning:_plotly_utils.basevalidators"
    ),
    pytest.mark.filterwarnings(
        "ignore:'oneOf' deprecated - use 'one_of':pyparsing.exceptions.PyparsingDeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:'parseString' deprecated - use 'parse_string':pyparsing.exceptions.PyparsingDeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:'resetCache' deprecated - use 'reset_cache':pyparsing.exceptions.PyparsingDeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:'enablePackrat' deprecated - use 'enable_packrat':pyparsing.exceptions.PyparsingDeprecationWarning"
    ),
]


def test_dashboard_ui_snapshot_matches_baseline() -> None:
    expected = json.loads(Path(SNAPSHOT_PATH).read_text(encoding="utf-8"))
    assert build_ui_snapshot() == expected
