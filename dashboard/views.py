from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.components import (
    read_metadata_file,
    render_empty_state,
    render_metric_card_with_delta,
    render_section_intro,
    render_status_card,
)
from dashboard.data_access import DashboardData, RunHistoryData


def artifact_metadata(gold_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, str | int]] = []
    for metadata_path in sorted(gold_dir.glob("*.metadata.json")):
        payload = read_metadata_file(metadata_path)
        row_count = payload.get("row_count", 0)
        rows.append(
            {
                "artifact": str(payload.get("dataset_name", metadata_path.name)),
                "rows": int(row_count) if isinstance(row_count, (int, str)) else 0,
                "updated_utc": str(payload.get("generated_at_utc", "")),
                "run_id": str(payload.get("run_id", "")) if payload.get("run_id") else "-",
            }
        )
    return pd.DataFrame(rows)


def format_currency(value: float) -> str:
    return f"{value:,.2f}"


def summarize_period_performance(monthly_view: pd.DataFrame) -> dict[str, float | str | None]:
    if monthly_view.empty:
        return {
            "current_month": None,
            "current_revenue": 0.0,
            "prior_month": None,
            "prior_revenue": 0.0,
            "delta_ratio": None,
        }

    current_row = monthly_view.iloc[-1]
    summary: dict[str, float | str | None] = {
        "current_month": str(current_row["order_month"]),
        "current_revenue": float(current_row["revenue"]),
        "prior_month": None,
        "prior_revenue": 0.0,
        "delta_ratio": None,
    }
    if len(monthly_view) > 1:
        prior_row = monthly_view.iloc[-2]
        summary["prior_month"] = str(prior_row["order_month"])
        summary["prior_revenue"] = float(prior_row["revenue"])
        if float(prior_row["revenue"]) != 0:
            summary["delta_ratio"] = (
                float(current_row["revenue"]) - float(prior_row["revenue"])
            ) / float(prior_row["revenue"])
    return summary


def rolling_revenue_signals(monthly_view: pd.DataFrame) -> dict[str, float | None]:
    if monthly_view.empty:
        return {"rolling_3m_avg": None, "quarter_delta_ratio": None}

    revenue_series = monthly_view["revenue"].astype(float)
    rolling_3m_avg = float(revenue_series.tail(3).mean())

    if len(revenue_series) < 6:
        quarter_delta_ratio: float | None = None
    else:
        current_quarter = float(revenue_series.tail(3).sum())
        prior_quarter = float(revenue_series.tail(6).head(3).sum())
        quarter_delta_ratio = (
            None if prior_quarter == 0 else (current_quarter - prior_quarter) / prior_quarter
        )

    return {
        "rolling_3m_avg": rolling_3m_avg,
        "quarter_delta_ratio": quarter_delta_ratio,
    }


def calculate_mom_delta(monthly_view: pd.DataFrame) -> tuple[str | None, str]:
    if len(monthly_view) < 2:
        return None, "neutral"
    latest_value = float(monthly_view.iloc[-1]["revenue"])
    prior_value = float(monthly_view.iloc[-2]["revenue"])
    if prior_value == 0:
        return None, "neutral"
    delta = (latest_value - prior_value) / prior_value
    if delta > 0:
        return f"+{abs(delta):.1%}", "up"
    if delta < 0:
        return f"-{abs(delta):.1%}", "down"
    return "0.0%", "neutral"


def format_delta_label(
    labels: dict[str, str],
    delta_text: str | None,
    delta_state: str,
) -> str | None:
    if delta_text is None:
        return None
    state_label = {
        "up": labels["delta_up"],
        "down": labels["delta_down"],
        "neutral": labels["delta_flat"],
    }.get(delta_state, labels["delta_flat"])
    return f"{delta_text} {state_label} {labels['delta_vs_prior']}"


def build_customer_focus(
    customer_360: pd.DataFrame,
    *,
    search_term: str,
    minimum_orders: int,
) -> pd.DataFrame:
    filtered = customer_360[customer_360["total_orders"].fillna(0) >= minimum_orders].copy()
    if search_term:
        filtered = filtered[
            filtered["customer_id"].astype(str).str.contains(search_term, case=False, na=False)
        ]
    return filtered.sort_values(
        ["total_spent", "days_since_last_purchase"],
        ascending=[False, True],
    )


def customer_segments(customer_360: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if customer_360.empty:
        empty_df = pd.DataFrame(columns=["segment", "customers"])
        return empty_df, empty_df

    segment_df = customer_360.copy()
    segment_df["value_segment"] = pd.cut(
        segment_df["total_spent"].fillna(0.0),
        bins=[-1.0, 100.0, 250.0, float("inf")],
        labels=["Low value", "Mid value", "High value"],
    )
    segment_df["recency_segment"] = pd.cut(
        segment_df["days_since_last_purchase"].fillna(9999),
        bins=[-1.0, 30.0, 90.0, float("inf")],
        labels=["0-30 days", "31-90 days", "90+ days"],
    )
    value_mix = (
        segment_df.groupby("value_segment", observed=False)
        .size()
        .reset_index(name="customers")
        .rename(columns={"value_segment": "segment"})
    )
    recency_mix = (
        segment_df.groupby("recency_segment", observed=False)
        .size()
        .reset_index(name="customers")
        .rename(columns={"recency_segment": "segment"})
    )
    return value_mix, recency_mix


def cohort_extremes(retention: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if retention.empty:
        empty = pd.DataFrame(columns=retention.columns)
        return empty, empty
    strongest = retention.sort_values(
        ["retention_rate", "customers"],
        ascending=[False, False],
    ).head(3)
    weakest = retention.sort_values(
        ["retention_rate", "customers"],
        ascending=[True, False],
    ).head(3)
    return strongest, weakest


def freshness_summary(
    artifact_df: pd.DataFrame,
    labels: dict[str, str],
) -> tuple[str, str, str]:
    if artifact_df.empty:
        return "Unknown", labels["run_missing"], labels["freshness_unknown"]

    timestamps = pd.to_datetime(artifact_df["updated_utc"], errors="coerce", utc=True).dropna()
    if timestamps.empty:
        return "Unknown", labels["run_missing"], labels["freshness_unknown"]

    latest_timestamp = timestamps.max().to_pydatetime()
    age_hours = (datetime.now(UTC) - latest_timestamp).total_seconds() / 3600
    freshness_value = f"{age_hours:.1f}h"
    freshness_copy = labels["freshness_healthy"] if age_hours <= 24 else labels["freshness_stale"]
    latest_run = next(
        (
            run_id
            for run_id in artifact_df["run_id"].tolist()
            if isinstance(run_id, str) and run_id != "-"
        ),
        labels["run_missing"],
    )
    return freshness_value, latest_run, freshness_copy


def compare_run_artifacts(
    run_history: RunHistoryData,
    left_run: str,
    right_run: str,
) -> dict[str, list[str]]:
    left_artifacts = set(
        run_history.artifact_history.loc[
            run_history.artifact_history["run_id"] == left_run,
            "artifact_path",
        ].tolist()
    )
    right_artifacts = set(
        run_history.artifact_history.loc[
            run_history.artifact_history["run_id"] == right_run,
            "artifact_path",
        ].tolist()
    )
    return {
        "left_only": sorted(left_artifacts.difference(right_artifacts)),
        "shared": sorted(left_artifacts.intersection(right_artifacts)),
        "right_only": sorted(right_artifacts.difference(left_artifacts)),
    }


def render_overview(
    labels: dict[str, str],
    data: DashboardData,
    monthly_view: pd.DataFrame,
) -> None:
    render_section_intro(
        labels["metrics_label"],
        labels["metrics_title"],
        labels["metrics_copy"],
    )
    delta_text, delta_state = calculate_mom_delta(monthly_view)
    delta_label = format_delta_label(labels, delta_text, delta_state)

    metric_columns = st.columns(4)
    metric_specs = [
        (
            labels["gmv"],
            format_currency(data.metrics.get("gmv_total", 0.0)),
            labels["gmv_caption"],
            delta_label,
            delta_state,
        ),
        (
            labels["aov"],
            format_currency(data.metrics.get("aov", 0.0)),
            labels["aov_caption"],
            delta_label,
            delta_state,
        ),
        (
            labels["active_customers"],
            f"{int(data.metrics.get('active_customers', 0)):,}",
            labels["active_customers_caption"],
            None,
            "neutral",
        ),
        (
            labels["churn_rate_proxy"],
            f"{data.metrics.get('churn_rate_proxy', 0.0):.1%}",
            labels["churn_caption"],
            None,
            "neutral",
        ),
    ]
    for column, (title, value, caption, card_delta, card_state) in zip(
        metric_columns,
        metric_specs,
        strict=True,
    ):
        with column:
            render_metric_card_with_delta(
                title,
                value,
                caption,
                delta_text=card_delta,
                delta_state=card_state,
            )

    trend_col, retention_col = st.columns([1.35, 1.0], gap="large")
    with trend_col:
        render_section_intro(
            labels["trend_label"],
            labels["trend_title"],
            labels["trend_copy"],
        )
        if monthly_view.empty:
            render_empty_state(labels["trend_title"], labels["artifacts_empty"])
        else:
            period_summary = summarize_period_performance(monthly_view)
            revenue_signals = rolling_revenue_signals(monthly_view)
            summary_cols = st.columns(2, gap="medium")
            current_revenue = float(period_summary["current_revenue"] or 0.0)
            prior_revenue = float(period_summary["prior_revenue"] or 0.0)
            with summary_cols[0]:
                render_status_card(
                    labels["current_period"],
                    format_currency(current_revenue),
                    str(period_summary["current_month"]),
                )
            with summary_cols[1]:
                prior_month = (
                    str(period_summary["prior_month"])
                    if period_summary["prior_month"] is not None
                    else labels["prior_period"]
                )
                render_status_card(
                    labels["prior_period"],
                    format_currency(prior_revenue),
                    prior_month,
                )
            signal_cols = st.columns(2, gap="medium")
            rolling_average = revenue_signals["rolling_3m_avg"]
            quarter_delta_ratio = revenue_signals["quarter_delta_ratio"]
            with signal_cols[0]:
                render_status_card(
                    labels["rolling_average"],
                    format_currency(float(rolling_average or 0.0)),
                    labels["trend_copy"],
                )
            with signal_cols[1]:
                quarter_delta_text = (
                    f"{quarter_delta_ratio:.1%}" if quarter_delta_ratio is not None else "n/a"
                )
                render_status_card(
                    labels["quarter_delta"],
                    quarter_delta_text,
                    labels["trend_copy"],
                )
            st.area_chart(
                monthly_view.set_index("order_month")["revenue"],
                color="#0f766e",
                width="stretch",
            )

    with retention_col:
        render_section_intro(
            labels["retention_label"],
            labels["retention_title"],
            labels["retention_copy"],
        )
        if data.retention.empty:
            render_empty_state(labels["retention_title"], labels["artifacts_empty"])
        else:
            retention_chart = data.retention.set_index("cohort_month")["retention_rate"]
            st.bar_chart(retention_chart, color="#1d4ed8", width="stretch")
            strongest, weakest = cohort_extremes(data.retention)
            cohort_tabs = st.tabs([labels["top_cohorts"], labels["risk_cohorts"]])
            with cohort_tabs[0]:
                st.dataframe(strongest, width="stretch", hide_index=True)
            with cohort_tabs[1]:
                st.dataframe(weakest, width="stretch", hide_index=True)
            with st.expander(labels["retention_title"], expanded=False):
                retention_display = data.retention.copy()
                retention_display["retention_rate"] = retention_display["retention_rate"].map(
                    lambda value: f"{value:.1%}"
                )
                st.dataframe(retention_display, width="stretch", hide_index=True)


def render_customer_health(labels: dict[str, str], customer_360: pd.DataFrame) -> None:
    render_section_intro(
        labels["customers_label"],
        labels["customers_title"],
        labels["customers_copy"],
    )
    filter_col, search_col = st.columns([0.35, 0.65], gap="large")
    with filter_col:
        minimum_orders = st.slider(labels["min_orders"], min_value=0, max_value=10, value=1)
    with search_col:
        search_term = st.text_input(labels["customer_search"], value="", placeholder="c1")

    filtered_customers = build_customer_focus(
        customer_360,
        search_term=search_term.strip(),
        minimum_orders=minimum_orders,
    )
    if filtered_customers.empty:
        render_empty_state(labels["customers_title"], labels["artifacts_empty"])
        return

    value_mix, recency_mix = customer_segments(filtered_customers)
    segments_col, top_customers_col, table_col = st.columns([0.28, 0.26, 0.46], gap="large")

    with segments_col:
        render_section_intro(
            labels["segments_title"],
            labels["segment_value"],
            labels["segments_copy"],
        )
        segment_tabs = st.tabs([labels["segment_value"], labels["segment_recency"]])
        with segment_tabs[0]:
            st.bar_chart(value_mix.set_index("segment")["customers"], color="#0f766e")
        with segment_tabs[1]:
            st.bar_chart(recency_mix.set_index("segment")["customers"], color="#1d4ed8")

    with top_customers_col:
        st.markdown(f"### {labels['top_customers']}")
        top_customers = filtered_customers[
            ["customer_id", "total_spent", "total_orders", "days_since_last_purchase"]
        ].head(8)
        st.dataframe(top_customers, width="stretch", hide_index=True)

        at_risk = filtered_customers[
            filtered_customers["days_since_last_purchase"].fillna(9999) > 90
        ].head(8)
        st.markdown(f"### {labels['customer_opportunity']}")
        st.dataframe(
            (
                at_risk[["customer_id", "total_spent", "days_since_last_purchase"]]
                if not at_risk.empty
                else pd.DataFrame(
                    columns=["customer_id", "total_spent", "days_since_last_purchase"]
                )
            ),
            width="stretch",
            hide_index=True,
        )

    with table_col:
        st.markdown(f"### {labels['customer_table']}")
        display_columns = [
            "customer_id",
            "total_orders",
            "total_spent",
            "avg_order_value",
            "days_since_last_purchase",
            "first_purchase",
            "last_purchase",
        ]
        st.dataframe(
            filtered_customers[display_columns].head(25),
            width="stretch",
            hide_index=True,
        )


def render_run_history(
    labels: dict[str, str],
    run_history: RunHistoryData,
) -> None:
    render_section_intro(
        labels["run_history_title"],
        labels["run_history_title"],
        labels["run_history_copy"],
    )
    if run_history.manifests.empty:
        render_empty_state(labels["run_history_title"], labels["run_history_empty"])
        return

    history_tabs = st.tabs(
        [
            labels["run_history_title"],
            labels["run_catalog_title"],
            labels["run_sql_title"],
        ]
    )
    manifest_display = run_history.manifests.copy()
    with history_tabs[0]:
        st.dataframe(manifest_display, width="stretch", hide_index=True)
    with history_tabs[1]:
        if run_history.catalog.empty:
            render_empty_state(labels["run_catalog_title"], labels["run_history_empty"])
        else:
            st.caption(labels["run_catalog_copy"])
            st.dataframe(run_history.catalog, width="stretch", hide_index=True)
    with history_tabs[2]:
        if run_history.sql_history.empty:
            render_empty_state(labels["run_sql_title"], labels["run_history_empty"])
        else:
            st.caption(labels["run_sql_copy"])
            st.dataframe(run_history.sql_history, width="stretch", hide_index=True)

    st.markdown(f"### {labels['run_compare_title']}")
    compare_cols = st.columns(2, gap="large")
    run_options = run_history.manifests["run_id"].tolist()
    with compare_cols[0]:
        left_run = st.selectbox(labels["run_compare_left"], options=run_options, index=0)
    with compare_cols[1]:
        right_run = st.selectbox(
            labels["run_compare_right"],
            options=run_options,
            index=1 if len(run_options) > 1 else 0,
        )

    run_comparison = compare_run_artifacts(run_history, left_run, right_run)
    left_only = run_comparison["left_only"]
    shared_artifacts = run_comparison["shared"]
    right_only = run_comparison["right_only"]

    summary_cols = st.columns(3, gap="large")
    with summary_cols[0]:
        render_status_card(
            labels["run_compare_only_left"],
            str(len(left_only)),
            labels["run_compare_summary"],
        )
    with summary_cols[1]:
        render_status_card(
            labels["run_compare_shared"],
            str(len(shared_artifacts)),
            labels["run_compare_summary"],
        )
    with summary_cols[2]:
        render_status_card(
            labels["run_compare_only_right"],
            str(len(right_only)),
            labels["run_compare_summary"],
        )

    detail_tabs = st.tabs(
        [
            labels["run_compare_only_left"],
            labels["run_compare_shared"],
            labels["run_compare_only_right"],
        ]
    )
    detail_frames = [
        pd.DataFrame({"artifact_path": left_only}),
        pd.DataFrame({"artifact_path": shared_artifacts}),
        pd.DataFrame({"artifact_path": right_only}),
    ]
    for tab, frame in zip(detail_tabs, detail_frames, strict=True):
        with tab:
            if frame.empty:
                render_empty_state(labels["run_compare_title"], labels["run_history_empty"])
            else:
                st.dataframe(frame, width="stretch", hide_index=True)


def render_operations(labels: dict[str, str], gold_dir: Path) -> None:
    render_section_intro(
        labels["operations_label"],
        labels["operations_title"],
        labels["operations_copy"],
    )
    artifact_df = artifact_metadata(gold_dir)
    freshness_value, latest_run, freshness_copy = freshness_summary(artifact_df, labels)

    status_columns = st.columns(3, gap="large")
    with status_columns[0]:
        render_status_card(labels["freshness_title"], freshness_value, freshness_copy)
    with status_columns[1]:
        render_status_card(labels["run_title"], latest_run, labels["quality_copy"])
    with status_columns[2]:
        render_status_card(
            labels["artifact_count_title"],
            f"{len(artifact_df):,}",
            labels["artifact_count_copy"],
        )

    left_col, right_col = st.columns([0.65, 0.35], gap="large")
    with left_col:
        st.markdown(f"### {labels['artifacts_title']}")
        if artifact_df.empty:
            render_empty_state(labels["artifacts_title"], labels["artifacts_empty"])
        else:
            renamed = artifact_df.rename(
                columns={
                    "artifact": labels["artifact_name"],
                    "rows": labels["artifact_rows"],
                    "updated_utc": labels["artifact_updated"],
                    "run_id": labels["artifact_run"],
                }
            )
            st.dataframe(renamed, width="stretch", hide_index=True)

    with right_col:
        with st.expander(labels["quality_title"], expanded=True):
            st.write(labels["quality_copy"])
            st.code("ridp run-pipeline all --run-id ops-review-001", language="bash")
