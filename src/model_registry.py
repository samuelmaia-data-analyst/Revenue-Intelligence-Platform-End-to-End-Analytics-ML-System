from __future__ import annotations

import json
import pickle
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sklearn.pipeline import Pipeline

try:
    import joblib
except ModuleNotFoundError:  # pragma: no cover
    joblib = None


def _persist_pickle(model: Pipeline, path: Path) -> None:
    with path.open("wb") as model_file:
        pickle.dump(model, model_file)


def _load_model(path: Path) -> Pipeline:
    if path.suffix == ".joblib" and joblib is not None:
        return joblib.load(path)
    with path.open("rb") as model_file:
        return pickle.load(model_file)


def register_model(
    model_name: str,
    model: Pipeline,
    output_dir: Path,
    data_version: str,
    metrics: dict[str, float | int | str | None],
    input_features: list[str],
    target_name: str,
) -> dict:
    registry_dir = output_dir / "model_registry" / model_name
    registry_dir.mkdir(parents=True, exist_ok=True)

    model_path = registry_dir / "model.pkl"
    metadata_path = registry_dir / "model_metadata.json"
    _persist_pickle(model, model_path)

    metadata = {
        "model_name": model_name,
        "run_id": str(uuid4()),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "data_version": data_version,
        "metrics": metrics,
        "input_features": input_features,
        "target_name": target_name,
        "model_file": model_path.name,
    }
    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)
    return metadata


def load_registered_model(base_dir: Path, model_name: str) -> tuple[Pipeline, dict]:
    registry_dir = base_dir / "model_registry" / model_name
    model_path = registry_dir / "model.pkl"
    metadata_path = registry_dir / "model_metadata.json"

    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"Model registry not found for '{model_name}' in {registry_dir.resolve()}"
        )

    model = _load_model(model_path)
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
    return model, metadata
