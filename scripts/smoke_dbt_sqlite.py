from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt"
DBT_PROFILE_TEMPLATE = DBT_PROJECT_DIR / "profiles" / "profiles.yml.example"
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "data" / "warehouse" / "revenue_intelligence.db"
DEFAULT_DBT_VENV_EXECUTABLE = PROJECT_ROOT / ".dbt-venv" / "Scripts" / "dbt.exe"
EXPECTED_MODELS = [
    "stg_scored_customers",
    "stg_recommendations",
    "stg_unit_economics",
    "portfolio_semantic_metrics",
    "channel_semantic_metrics",
    "action_priority_board",
]


def _resolve_dbt_executable() -> str:
    configured = os.getenv("DBT_EXECUTABLE")
    candidates = [
        Path(configured) if configured else None,
        Path(shutil.which("dbt")) if shutil.which("dbt") else None,
        DEFAULT_DBT_VENV_EXECUTABLE,
        Path(sys.executable).with_name("dbt.exe"),
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return str(candidate)
    raise RuntimeError(
        "dbt executable was not found. Install it into .dbt-venv or set DBT_EXECUTABLE."
    )


def _run(command: list[str], env: dict[str, str]) -> None:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            f"{' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def _drop_existing_models(sqlite_path: Path) -> None:
    with sqlite3.connect(sqlite_path) as connection:
        for model_name in EXPECTED_MODELS:
            row = connection.execute(
                "SELECT type FROM sqlite_master WHERE name = ? AND type IN ('table', 'view')",
                (model_name,),
            ).fetchone()
            if row is None:
                continue
            object_type = row[0]
            if object_type == "view":
                connection.execute(f'DROP VIEW IF EXISTS "{model_name}"')
            else:
                connection.execute(f'DROP TABLE IF EXISTS "{model_name}"')
        connection.commit()


def _assert_expected_models(sqlite_path: Path) -> None:
    with sqlite3.connect(sqlite_path) as connection:
        rows = connection.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY name"
        ).fetchall()
    observed = {row[0] for row in rows}
    missing = sorted(set(EXPECTED_MODELS).difference(observed))
    if missing:
        raise RuntimeError(f"dbt smoke validation missing expected models: {missing}")


def main() -> int:
    dbt_executable = _resolve_dbt_executable()

    sqlite_path = Path(os.getenv("DBT_SQLITE_PATH", str(DEFAULT_SQLITE_PATH))).resolve()
    schema_dir = Path(os.getenv("DBT_SQLITE_SCHEMA_DIR", str(sqlite_path.parent))).resolve()

    if not sqlite_path.exists():
        raise RuntimeError(f"SQLite warehouse not found for dbt smoke: {sqlite_path}")

    _drop_existing_models(sqlite_path)

    with tempfile.TemporaryDirectory(prefix="dbt-profiles-") as profiles_dir:
        profiles_path = Path(profiles_dir)
        shutil.copy2(DBT_PROFILE_TEMPLATE, profiles_path / "profiles.yml")

        env = os.environ.copy()
        env["DBT_TARGET"] = env.get("DBT_TARGET", "ci")
        env["DBT_SQLITE_PATH"] = str(sqlite_path)
        env["DBT_SQLITE_SCHEMA_DIR"] = str(schema_dir)

        dbt_args = [
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(profiles_path),
        ]
        _run([dbt_executable, "debug", *dbt_args], env)
        _run([dbt_executable, "run", *dbt_args], env)
        _run([dbt_executable, "test", *dbt_args], env)

        target_dir = DBT_PROJECT_DIR / "target"
        for required in ["manifest.json", "run_results.json"]:
            if not (target_dir / required).exists():
                raise RuntimeError(f"dbt smoke validation missing target artifact: {required}")

    _assert_expected_models(sqlite_path)
    print("dbt SQLite smoke validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
