from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence


def _run(command: Sequence[str]) -> None:
    subprocess.run(command, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Developer task runner for local setup, validation, and dashboard workflows."
    )
    parser.add_argument(
        "task",
        choices=[
            "install",
            "bootstrap",
            "pipeline",
            "health",
            "test",
            "lint",
            "build",
            "check",
            "format",
            "precommit",
            "dashboard",
        ],
        help="Task to execute.",
    )
    return parser


def main() -> None:
    task = build_parser().parse_args().task
    python = sys.executable

    if task == "install":
        _run([python, "-m", "pip", "install", "-e", ".[dev]"])
        return

    if task == "bootstrap":
        _run([python, "-m", "ridp.cli", "bootstrap-sample-data"])
        return

    if task == "pipeline":
        _run([python, "-m", "ridp.cli", "run-pipeline", "all"])
        return

    if task == "health":
        _run([python, "-m", "ridp.cli", "check-health"])
        return

    if task == "test":
        _run([python, "-m", "pytest"])
        return

    if task == "lint":
        _run([python, "-m", "ruff", "check", "."])
        _run([python, "-m", "black", "--check", "."])
        _run([python, "-m", "mypy", "."])
        return

    if task == "build":
        _run([python, "-m", "build", "--sdist", "--wheel"])
        return

    if task == "check":
        commands = [
            [python, "-m", "ruff", "check", "."],
            [python, "-m", "black", "--check", "."],
            [python, "-m", "mypy", "."],
            [python, "-m", "pytest"],
            [python, "-m", "build", "--sdist", "--wheel"],
        ]
        for command in commands:
            _run(command)
        return

    if task == "format":
        _run([python, "-m", "ruff", "check", ".", "--fix"])
        _run([python, "-m", "black", "."])
        return

    if task == "precommit":
        _run([python, "-m", "pre_commit", "run", "--all-files"])
        return

    if task == "dashboard":
        _run([python, "-m", "ridp.dashboard_launcher"])
        return

    raise SystemExit(f"Unsupported task: {task}")
