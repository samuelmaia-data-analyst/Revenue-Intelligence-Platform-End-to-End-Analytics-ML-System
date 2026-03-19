from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from ridp.config import DataDirectories

REQUIRED_GOLD_ARTIFACTS = (
    "business_kpis.csv",
    "kpi_monthly_revenue.csv",
    "customer_360.csv",
)


@dataclass(frozen=True)
class HealthCheckReport:
    checks: pd.DataFrame

    @property
    def failed(self) -> pd.DataFrame:
        return self.checks[self.checks["status"] == "fail"].copy()

    @property
    def warnings(self) -> pd.DataFrame:
        return self.checks[self.checks["status"] == "warn"].copy()

    @property
    def passed(self) -> pd.DataFrame:
        return self.checks[self.checks["status"] == "pass"].copy()


def _metadata_path(artifact_path: Path) -> Path:
    return artifact_path.with_suffix(".metadata.json")


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def _build_check_row(
    *,
    check_name: str,
    target: str,
    status: str,
    detail: str,
) -> dict[str, str]:
    return {
        "check_name": check_name,
        "target": target,
        "status": status,
        "detail": detail,
    }


def evaluate_platform_health(
    directories: DataDirectories,
    *,
    freshness_sla_hours: int,
) -> HealthCheckReport:
    rows: list[dict[str, str]] = []

    for artifact_name in REQUIRED_GOLD_ARTIFACTS:
        artifact_path = directories.gold / artifact_name
        metadata_path = _metadata_path(artifact_path)
        if not artifact_path.exists():
            rows.append(
                _build_check_row(
                    check_name="required_artifact_present",
                    target=artifact_name,
                    status="fail",
                    detail=f"Missing required gold artifact at {artifact_path}",
                )
            )
            continue
        rows.append(
            _build_check_row(
                check_name="required_artifact_present",
                target=artifact_name,
                status="pass",
                detail=f"Artifact present at {artifact_path}",
            )
        )
        if not metadata_path.exists():
            rows.append(
                _build_check_row(
                    check_name="artifact_metadata_present",
                    target=artifact_name,
                    status="fail",
                    detail=f"Missing metadata sidecar at {metadata_path}",
                )
            )
            continue

        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        row_count = payload.get("row_count")
        if not isinstance(row_count, int) or row_count <= 0:
            rows.append(
                _build_check_row(
                    check_name="artifact_non_empty",
                    target=artifact_name,
                    status="fail",
                    detail=f"Metadata row_count is invalid or empty: {row_count}",
                )
            )
        else:
            rows.append(
                _build_check_row(
                    check_name="artifact_non_empty",
                    target=artifact_name,
                    status="pass",
                    detail=f"Metadata row_count={row_count}",
                )
            )

        generated_at = _parse_timestamp(payload.get("generated_at_utc"))
        if generated_at is None:
            rows.append(
                _build_check_row(
                    check_name="artifact_freshness",
                    target=artifact_name,
                    status="fail",
                    detail="generated_at_utc is missing or invalid",
                )
            )
            continue

        age_hours = (datetime.now(UTC) - generated_at).total_seconds() / 3600
        freshness_status = "pass" if age_hours <= freshness_sla_hours else "warn"
        rows.append(
            _build_check_row(
                check_name="artifact_freshness",
                target=artifact_name,
                status=freshness_status,
                detail=(f"Age={age_hours:.1f}h against SLA {freshness_sla_hours}h"),
            )
        )

    runtime_checks = [
        ("serving_store_available", directories.serving, directories.serving.exists()),
        (
            "run_history_db_available",
            directories.run_history_db,
            directories.run_history_db.exists(),
        ),
        ("run_manifests_dir_available", directories.runs, directories.runs.exists()),
    ]
    for check_name, path, exists in runtime_checks:
        rows.append(
            _build_check_row(
                check_name=check_name,
                target=str(path),
                status="pass" if exists else "warn",
                detail="Present" if exists else "Not found yet",
            )
        )

    checks = (
        pd.DataFrame(rows).sort_values(["status", "check_name", "target"]).reset_index(drop=True)
    )
    return HealthCheckReport(checks=checks)
