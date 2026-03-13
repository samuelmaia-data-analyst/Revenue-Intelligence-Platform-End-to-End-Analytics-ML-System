from __future__ import annotations

import json
from pathlib import Path


def load_semantic_metrics(definitions_path: Path) -> dict:
    with definitions_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_metric_catalog(definitions_path: Path, output_path: Path) -> dict:
    catalog = load_semantic_metrics(definitions_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(catalog, file, indent=2, ensure_ascii=False)
    return catalog
