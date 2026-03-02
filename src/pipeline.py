import argparse
from pathlib import Path

from main import run_pipeline
from src.config import PipelineConfig


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
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command != "run":
        parser.print_help()
        return

    cfg = PipelineConfig.from_env(Path(__file__).resolve().parents[1])
    if args.data_dir:
        data_dir = Path(args.data_dir)
        cfg = PipelineConfig(
            project_root=cfg.project_root,
            data_dir=data_dir,
            raw_dir=data_dir / "raw",
            bronze_dir=data_dir / "bronze",
            silver_dir=data_dir / "silver",
            gold_dir=data_dir / "gold",
            processed_dir=data_dir / "processed",
            seed=args.seed if args.seed is not None else cfg.seed,
            log_level=args.log_level or cfg.log_level,
        )
    elif args.seed is not None or args.log_level:
        cfg = PipelineConfig(
            project_root=cfg.project_root,
            data_dir=cfg.data_dir,
            raw_dir=cfg.raw_dir,
            bronze_dir=cfg.bronze_dir,
            silver_dir=cfg.silver_dir,
            gold_dir=cfg.gold_dir,
            processed_dir=cfg.processed_dir,
            seed=args.seed if args.seed is not None else cfg.seed,
            log_level=args.log_level or cfg.log_level,
        )

    run_pipeline(cfg)


if __name__ == "__main__":
    main()
