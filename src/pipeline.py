import argparse
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

from src.config import PipelineConfig
from src.governance import build_data_dictionary
from src.orchestration import run_pipeline


def _parse_cli_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must use YYYY-MM-DD format.") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Revenue Intelligence Platform CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_cmd = subparsers.add_parser("run", help="Run end-to-end pipeline")
    run_cmd.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Override data directory (default: <project_root>/data).",
    )
    run_cmd.add_argument("--seed", type=int, default=None, help="Override random seed.")
    run_cmd.add_argument(
        "--start-date",
        type=_parse_cli_date,
        default=None,
        help="Optional inclusive backfill start date for order data (YYYY-MM-DD).",
    )
    run_cmd.add_argument(
        "--end-date",
        type=_parse_cli_date,
        default=None,
        help="Optional inclusive backfill end date for source data (YYYY-MM-DD).",
    )
    run_cmd.add_argument(
        "--retry-attempts",
        type=int,
        default=None,
        help="Override stage retry attempts for transient failures.",
    )
    run_cmd.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override log level.",
    )
    artifacts_cmd = subparsers.add_parser(
        "artifacts",
        help="Generate governance artifacts without running the full pipeline.",
    )
    artifacts_cmd.add_argument(
        "--data-dictionary-path",
        type=str,
        default=None,
        help="Override data dictionary output path.",
    )
    return parser


def _resolve_config(args: argparse.Namespace) -> PipelineConfig:
    cfg = PipelineConfig.from_env(Path(__file__).resolve().parents[1])
    data_dir = Path(args.data_dir) if getattr(args, "data_dir", None) else None
    seed = getattr(args, "seed", None)
    log_level = getattr(args, "log_level", None)
    retry_attempts = getattr(args, "retry_attempts", None)
    resolved = cfg.with_overrides(
        data_dir=data_dir,
        seed=seed,
        log_level=log_level,
        backfill_start_date=getattr(args, "start_date", None),
        backfill_end_date=getattr(args, "end_date", None),
    )
    if retry_attempts is not None:
        return replace(resolved, retry_attempts=retry_attempts)
    return resolved


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "run":
        cfg = _resolve_config(args)
        run_pipeline(cfg)
        return

    if args.command == "artifacts":
        cfg = PipelineConfig.from_env(Path(__file__).resolve().parents[1])
        output_path = (
            Path(args.data_dictionary_path)
            if args.data_dictionary_path
            else cfg.data_dictionary_path
        )
        dictionary = build_data_dictionary(output_path)
        print(
            json.dumps(
                {"data_dictionary_path": str(output_path), "tables": len(dictionary["tables"])}
            )
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
