from __future__ import annotations

import json
from pathlib import Path

from src.io_utils import atomic_write_json


def load_semantic_metrics(definitions_path: Path) -> dict:
    with definitions_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_metric_catalog(definitions_path: Path, output_path: Path) -> dict:
    catalog = load_semantic_metrics(definitions_path)
    atomic_write_json(output_path, catalog)
    return catalog
