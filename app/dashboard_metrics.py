from __future__ import annotations

import pandas as pd


def format_currency(value: float, lang: str) -> str:
    if lang in {"pt-br", "pt-pt"}:
        return f"R$ {value:,.0f}".replace(",", ".")
    return f"${value:,.0f}"


def auc_text(value: float | None) -> str:
    if value is None:
        return "n/a"
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return "n/a" if pd.isna(parsed) else f"{parsed:.3f}"


def potential_impact(row: pd.Series) -> float:
    action = row["recommended_action"]
    if action == "Retention Campaign":
        return row["ltv"] * row["churn_probability"] * 0.35
    if action == "Upsell Offer":
        return row["ltv"] * row["next_purchase_probability"] * 0.15
    if action == "Reduce Acquisition Spend":
        return row["cac"] * 0.50
    return row["ltv"] * row["next_purchase_probability"] * 0.03
