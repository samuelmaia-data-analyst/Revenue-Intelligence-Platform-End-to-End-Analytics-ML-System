import pandas as pd

from src.business_rules import (
    HIGH_CHURN_THRESHOLD,
    HIGH_VALUE_QUANTILE,
    LOW_CHURN_THRESHOLD,
    LOW_VALUE_QUANTILE,
)


def build_recommendations(ltv_df: pd.DataFrame, cac_df: pd.DataFrame) -> pd.DataFrame:
    channel_cac = cac_df[["channel", "cac"]].copy()
    out = ltv_df.merge(channel_cac, on="channel", how="left").fillna({"cac": 0})
    out["ltv_cac_ratio"] = out["ltv"] / out["cac"].replace(0, 1)
    high_value_cutoff = out["ltv"].quantile(HIGH_VALUE_QUANTILE)
    low_value_cutoff = out["ltv"].quantile(LOW_VALUE_QUANTILE)
    median_cac = out["cac"].median()

    def map_action(row: pd.Series) -> str:
        if row["churn_probability"] > HIGH_CHURN_THRESHOLD:
            return "Retention Campaign"
        if row["ltv"] > high_value_cutoff and row["churn_probability"] < LOW_CHURN_THRESHOLD:
            return "Upsell Offer"
        if row["ltv"] < low_value_cutoff and row["cac"] > median_cac:
            return "Reduce Acquisition Spend"
        return "Nurture"

    out["recommended_action"] = out.apply(map_action, axis=1)
    out["strategic_score"] = (
        0.45 * out["ltv"].rank(pct=True)
        + 0.35 * (1 - out["churn_probability"])
        + 0.2 * out["next_purchase_probability"]
    )
    out = out.sort_values("strategic_score", ascending=False)
    cols = [
        "customer_id",
        "channel",
        "segment",
        "ltv",
        "cac",
        "ltv_cac_ratio",
        "churn_probability",
        "next_purchase_probability",
        "strategic_score",
        "recommended_action",
    ]
    return out[cols]
