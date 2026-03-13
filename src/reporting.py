import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.business_rules import RECOMMENDATION_POLICIES


def build_executive_report(
    recommendations_df: pd.DataFrame,
    churn_results: dict,
    next_purchase_results: dict,
    kpi_snapshot: dict,
    output_path: Path,
) -> dict:
    top_20 = (
        recommendations_df.sort_values("strategic_score", ascending=False)
        .head(20)[
            [
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
        ]
        .to_dict(orient="records")
    )

    report = {
        "data_refresh_utc": datetime.now(UTC).isoformat(),
        "base_size": {
            "customers_in_scope": int(recommendations_df["customer_id"].nunique()),
            "rows_in_recommendation_table": int(len(recommendations_df)),
        },
        "top_kpis": {
            "avg_ltv": float(kpi_snapshot["avg_ltv"]),
            "avg_cac": float(kpi_snapshot["avg_cac"]),
            "avg_ltv_cac_ratio": float(kpi_snapshot["avg_ltv_cac_ratio"]),
            "avg_churn_probability": float(recommendations_df["churn_probability"].mean()),
            "avg_next_purchase_probability": float(
                recommendations_df["next_purchase_probability"].mean()
            ),
        },
        "business_context": {
            "revenue_proxy": float(kpi_snapshot["revenue_proxy"]),
            "portfolio_size": int(kpi_snapshot["portfolio_size"]),
            "best_channel_efficiency": kpi_snapshot["best_channel_efficiency"],
        },
        "model_performance": {
            "churn": churn_results,
            "next_purchase_30d": next_purchase_results,
        },
        "recommendations_top_20": top_20,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    return report


def build_executive_summary(
    recommendations_df: pd.DataFrame,
    scored_df: pd.DataFrame,
    unit_economics_df: pd.DataFrame,
    kpi_snapshot: dict,
    output_path: Path,
    top_n: int = 20,
) -> dict:
    top_churn = (
        recommendations_df.sort_values("churn_probability", ascending=False)
        .head(top_n)[["customer_id", "segment", "channel", "churn_probability"]]
        .to_dict(orient="records")
    )
    top_actions = (
        recommendations_df.sort_values("strategic_score", ascending=False)
        .head(top_n)[["customer_id", "recommended_action", "strategic_score", "ltv_cac_ratio"]]
        .to_dict(orient="records")
    )
    ltv_cac_channel = (
        unit_economics_df[["channel", "ltv_cac_ratio"]]
        .sort_values("ltv_cac_ratio", ascending=False)
        .to_dict(orient="records")
    )

    summary = {
        "data_refresh_utc": datetime.now(UTC).isoformat(),
        "kpis": {
            "total_revenue_proxy": float(kpi_snapshot["revenue_proxy"]),
            "avg_arpu": float(kpi_snapshot["avg_arpu"]),
            "avg_churn_probability": float(recommendations_df["churn_probability"].mean()),
            "portfolio_size": int(kpi_snapshot["portfolio_size"]),
        },
        "ltv_cac_by_channel": ltv_cac_channel,
        "top_churn_risk_customers": top_churn,
        "top_20_recommended_actions": top_actions,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
    return summary


def build_business_outcomes(
    recommendations_df: pd.DataFrame,
    unit_economics_df: pd.DataFrame,
    outcomes_path: Path,
    top_actions_path: Path,
    top_n: int = 10,
) -> dict:
    top_actions = (
        recommendations_df.sort_values("strategic_score", ascending=False).head(top_n).copy()
    )

    def _simulate_row(row: pd.Series) -> pd.Series:
        action = row["recommended_action"]
        policy = RECOMMENDATION_POLICIES.get(action, RECOMMENDATION_POLICIES["Nurture"])
        if action == "Retention Campaign":
            expected_uplift = row["ltv"] * row["churn_probability"] * policy.uplift_rate
        elif action == "Upsell Offer":
            expected_uplift = row["ltv"] * row["next_purchase_probability"] * policy.uplift_rate
        elif action == "Reduce Acquisition Spend":
            expected_uplift = row["cac"] * policy.uplift_rate
        else:
            expected_uplift = row["ltv"] * row["next_purchase_probability"] * policy.uplift_rate

        cost_base = row["ltv"] if policy.base_metric == "ltv" else row["cac"]
        action_cost = cost_base * policy.cost_rate
        net_impact = expected_uplift - action_cost
        roi = net_impact / action_cost if action_cost > 0 else 0.0
        return pd.Series(
            {
                "expected_uplift": expected_uplift,
                "action_cost": action_cost,
                "net_impact": net_impact,
                "roi_simulated": roi,
            }
        )

    simulated = top_actions.apply(_simulate_row, axis=1)
    top_actions = pd.concat([top_actions, simulated], axis=1)
    top_actions["priority_rank"] = range(1, len(top_actions) + 1)
    top_actions["baseline_revenue_90d"] = (
        top_actions["ltv"] * top_actions["next_purchase_probability"]
    )
    top_actions["scenario_revenue_90d"] = (
        top_actions["baseline_revenue_90d"] + top_actions["expected_uplift"]
    )

    top_actions_export = top_actions[
        [
            "priority_rank",
            "customer_id",
            "channel",
            "segment",
            "recommended_action",
            "strategic_score",
            "expected_uplift",
            "action_cost",
            "net_impact",
            "roi_simulated",
            "baseline_revenue_90d",
            "scenario_revenue_90d",
            "ltv_cac_ratio",
        ]
    ].rename(
        columns={
            "recommended_action": "action",
            "strategic_score": "strategic_priority_score",
        }
    )

    top_actions_path.parent.mkdir(parents=True, exist_ok=True)
    top_actions_export.to_csv(top_actions_path, index=False)

    baseline_revenue = float(top_actions_export["baseline_revenue_90d"].sum())
    scenario_revenue = float(top_actions_export["scenario_revenue_90d"].sum())
    total_action_cost = float(top_actions_export["action_cost"].sum())
    delta_revenue = scenario_revenue - baseline_revenue
    net_impact = float(top_actions_export["net_impact"].sum())
    roi = net_impact / total_action_cost if total_action_cost > 0 else 0.0

    ltv_cac_by_channel = (
        unit_economics_df[["channel", "ltv_cac_ratio"]]
        .sort_values("ltv_cac_ratio", ascending=False)
        .to_dict(orient="records")
    )

    high_churn_risk_pct = float((recommendations_df["churn_probability"] >= 0.7).mean())
    avg_ltv_cac_ratio = float(recommendations_df["ltv_cac_ratio"].mean())

    outcomes = {
        "data_refresh_utc": datetime.now(UTC).isoformat(),
        "kpis": {
            "avg_ltv_cac_ratio": avg_ltv_cac_ratio,
            "high_churn_risk_pct": high_churn_risk_pct,
            "simulated_net_impact_top10": net_impact,
        },
        "ltv_cac_by_channel": ltv_cac_by_channel,
        "simulation_assumptions": {
            name: {
                "uplift_rate": policy.uplift_rate,
                "cost_rate": policy.cost_rate,
                "base": policy.base_metric,
            }
            for name, policy in RECOMMENDATION_POLICIES.items()
        },
        "simulation_summary_top10": {
            "baseline_revenue_90d": baseline_revenue,
            "scenario_revenue_90d": scenario_revenue,
            "delta_revenue_90d": delta_revenue,
            "total_action_cost": total_action_cost,
            "net_impact": net_impact,
            "roi_simulated": roi,
        },
        "top_10_actions": top_actions_export.to_dict(orient="records"),
    }

    outcomes_path.parent.mkdir(parents=True, exist_ok=True)
    with outcomes_path.open("w", encoding="utf-8") as file:
        json.dump(outcomes, file, indent=2, ensure_ascii=False)
    return outcomes
