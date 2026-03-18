from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from contracts.v1.data_contract import GOLD_CONTRACT_MODELS
from src.io_utils import atomic_write_json


def build_data_dictionary(output_path: Path) -> dict[str, Any]:
    dictionary: dict[str, Any] = {
        "version": "1.0",
        "tables": [],
    }
    for table_name, model in sorted(GOLD_CONTRACT_MODELS.items()):
        dictionary["tables"].append(
            {
                "table_name": table_name,
                "contract_model": model.__name__,
                "columns": _model_columns(model),
            }
        )
    atomic_write_json(output_path, dictionary)
    return dictionary


def _model_columns(model: type[BaseModel]) -> list[dict[str, str]]:
    columns: list[dict[str, str]] = []
    for name, field in model.model_fields.items():
        columns.append(
            {
                "name": name,
                "type": str(field.annotation),
                "required": str(field.is_required()),
            }
        )
    return columns
