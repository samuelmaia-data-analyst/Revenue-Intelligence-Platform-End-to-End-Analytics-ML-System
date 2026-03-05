"""Backward-compatible import path for data contracts.

Prefer importing from `contracts.data_contract`.
"""

from contracts.data_contract import (  # noqa: F401
    GOLD_CONTRACT_MODELS,
    DimChannelContract,
    DimCustomersContract,
    DimDateContract,
    FactOrdersContract,
    ScoreInputRecord,
    ScorePrediction,
    ScoreRequest,
    ScoreResponse,
    required_columns_for,
    validate_gold_table,
)
