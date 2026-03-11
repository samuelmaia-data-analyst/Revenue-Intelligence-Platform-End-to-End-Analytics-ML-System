from __future__ import annotations

import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main() -> None:
    app_path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)]
    raise SystemExit(stcli.main())
