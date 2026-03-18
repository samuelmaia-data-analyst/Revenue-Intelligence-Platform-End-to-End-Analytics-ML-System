from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path


def compute_file_fingerprint(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item)):
        digest.update(path.name.encode("utf-8"))
        digest.update(str(path.stat().st_size).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass(frozen=True)
class RunContext:
    run_id: str
    started_at_utc: str
    input_fingerprint: str
    run_dir: Path
    snapshot_dir: Path
    log_path: Path
    success_manifest_path: Path
    failure_manifest_path: Path

    @classmethod
    def build(
        cls,
        manifests_dir: Path,
        runs_dir: Path,
        snapshots_dir: Path,
        input_files: list[Path],
    ) -> RunContext:
        started_at = datetime.now(UTC)
        fingerprint = compute_file_fingerprint(input_files) if input_files else "empty-input"
        run_id = f"{started_at.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:10]}"
        run_dir = runs_dir / run_id
        snapshot_dir = snapshots_dir / run_id
        return cls(
            run_id=run_id,
            started_at_utc=started_at.isoformat(),
            input_fingerprint=fingerprint,
            run_dir=run_dir,
            snapshot_dir=snapshot_dir,
            log_path=run_dir / "pipeline.log",
            success_manifest_path=manifests_dir / f"{run_id}.success.json",
            failure_manifest_path=manifests_dir / f"{run_id}.failure.json",
        )


def is_older_than(path: Path, cutoff_utc: datetime) -> bool:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return modified < cutoff_utc


def utc_now_minus_days(days: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=days)
