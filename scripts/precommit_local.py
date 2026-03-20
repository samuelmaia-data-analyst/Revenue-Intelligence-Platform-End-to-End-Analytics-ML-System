from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml  # type: ignore[import-untyped]

MERGE_MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


def _iter_files(paths: list[str]) -> list[Path]:
    return [Path(path) for path in paths if Path(path).is_file()]


def trim_trailing_whitespace(paths: list[str]) -> int:
    changed = False
    for path in _iter_files(paths):
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        normalized = []
        for line in lines:
            ending = ""
            content = line
            if line.endswith("\r\n"):
                ending = "\r\n"
                content = line[:-2]
            elif line.endswith("\n"):
                ending = "\n"
                content = line[:-1]
            normalized.append(content.rstrip(" \t") + ending)
        updated = "".join(normalized)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed = True
    return 1 if changed else 0


def fix_end_of_file(paths: list[str]) -> int:
    changed = False
    for path in _iter_files(paths):
        content = path.read_bytes()
        if not content:
            continue
        if content.endswith(b"\n"):
            continue
        path.write_bytes(content + b"\n")
        changed = True
    return 1 if changed else 0


def check_merge_conflict(paths: list[str]) -> int:
    failed = False
    for path in _iter_files(paths):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if any(line.startswith(marker) for line in lines for marker in MERGE_MARKERS):
            print(f"merge conflict markers found in {path}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def validate_yaml(paths: list[str]) -> int:
    failed = False
    for path in _iter_files(paths):
        if path.suffix not in {".yml", ".yaml"}:
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            print(f"invalid YAML in {path}: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def validate_toml(paths: list[str]) -> int:
    failed = False
    for path in _iter_files(paths):
        if path.suffix != ".toml":
            continue
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            print(f"invalid TOML in {path}: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def run_subprocess(command: list[str]) -> int:
    completed = subprocess.run(command, check=False)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local pre-commit helpers without network fetches."
    )
    parser.add_argument(
        "hook",
        choices=[
            "trim-trailing-whitespace",
            "fix-end-of-file",
            "check-merge-conflict",
            "check-yaml",
            "check-toml",
            "ruff-fix",
            "black",
            "mypy",
        ],
    )
    parser.add_argument("paths", nargs="*")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    python = sys.executable

    if args.hook == "trim-trailing-whitespace":
        return trim_trailing_whitespace(args.paths)
    if args.hook == "fix-end-of-file":
        return fix_end_of_file(args.paths)
    if args.hook == "check-merge-conflict":
        return check_merge_conflict(args.paths)
    if args.hook == "check-yaml":
        return validate_yaml(args.paths)
    if args.hook == "check-toml":
        return validate_toml(args.paths)
    if args.hook == "ruff-fix":
        return run_subprocess([python, "-m", "ruff", "check", "--fix", *args.paths])
    if args.hook == "black":
        return run_subprocess([python, "-m", "black", *args.paths])
    if args.hook == "mypy":
        return run_subprocess([python, "-m", "mypy", "."])
    raise SystemExit(f"Unsupported hook: {args.hook}")


if __name__ == "__main__":
    raise SystemExit(main())
