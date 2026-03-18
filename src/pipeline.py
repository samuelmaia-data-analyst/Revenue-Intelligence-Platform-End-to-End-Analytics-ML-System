import argparse
import json
from pathlib import Path

from src.config import PipelineConfig
from src.governance import build_data_dictionary
from src.orchestration import run_pipeline


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
    return cfg.with_overrides(data_dir=data_dir, seed=seed, log_level=log_level)


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
