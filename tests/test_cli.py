from __future__ import annotations

from src.pipeline import _build_parser


def test_cli_parser_accepts_run_command() -> None:
    args = _build_parser().parse_args(["run", "--seed", "99", "--log-level", "DEBUG"])

    assert args.command == "run"
    assert args.seed == 99
    assert args.log_level == "DEBUG"
