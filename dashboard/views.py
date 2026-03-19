from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.charts import (
    build_retention_chart,
    build_revenue_trend_chart,
    build_segment_chart,
    build_top_customers_chart,
)
from dashboard.components import (
    hydrate_session_from_query_params,
    read_metadata_file,
    render_empty_state,
    render_metric_card_with_delta,
    render_panel_header,
    render_section_intro,
    render_share_snapshot,
    render_status_card,
    render_table_card,
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


def risk_band(days_since_last_purchase: float) -> str:
    if days_since_last_purchase > 120:
        return "Critical"
    if days_since_last_purchase > 90:
        return "At risk"
    if days_since_last_purchase > 45:
        return "Monitor"
    return "Healthy"


def value_band(total_spent: float) -> str:
    if total_spent >= 250:
        return "High value"
    if total_spent >= 100:
        return "Mid value"
    return "Low value"


def build_run_comparison_table(
    left_only: list[str],
    shared_artifacts: list[str],
    right_only: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    rows.extend(
        {"artifact_path": artifact_path, "comparison_status": "Reference only"}
        for artifact_path in left_only
    )
    rows.extend(
        {"artifact_path": artifact_path, "comparison_status": "Shared"}
        for artifact_path in shared_artifacts
    )
    rows.extend(
        {"artifact_path": artifact_path, "comparison_status": "Comparison only"}
        for artifact_path in right_only
    )
    return pd.DataFrame(rows)


def build_customer_spotlight(customer_row: pd.Series) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "Customer", "value": str(customer_row["customer_id"])},
            {
                "metric": "Health",
                "value": risk_band(float(customer_row["days_since_last_purchase"])),
            },
            {"metric": "Value tier", "value": value_band(float(customer_row["total_spent"]))},
            {"metric": "Orders", "value": f"{float(customer_row['total_orders']):,.0f}"},
            {"metric": "Total spent", "value": format_currency(float(customer_row["total_spent"]))},
            {
                "metric": "AOV",
                "value": format_currency(float(customer_row["avg_order_value"])),
            },
            {
                "metric": "Days inactive",
                "value": f"{float(customer_row['days_since_last_purchase']):,.0f}",
            },
            {"metric": "First purchase", "value": str(customer_row["first_purchase"])},
            {"metric": "Last purchase", "value": str(customer_row["last_purchase"])},
        ]
    )


def build_cohort_spotlight(retention: pd.DataFrame, cohort_month: str) -> pd.DataFrame:
    cohort_row = retention.loc[retention["cohort_month"] == cohort_month].iloc[0]
    return pd.DataFrame(
        [
            {"metric": "Cohort", "value": str(cohort_row["cohort_month"])},
            {"metric": "Customers", "value": f"{float(cohort_row['customers']):,.0f}"},
            {
                "metric": "Retained customers",
                "value": f"{float(cohort_row['retained_customers']):,.0f}",
            },
            {"metric": "Retention", "value": f"{float(cohort_row['retention_rate']):.1%}"},
        ]
    )


def build_run_spotlight(run_history: RunHistoryData, run_id: str) -> pd.DataFrame:
    run_rows = run_history.manifests.loc[run_history.manifests["run_id"] == run_id]
    if run_rows.empty:
        return pd.DataFrame(columns=["metric", "value"])
    run_row = run_rows.iloc[0]
    artifact_count = int(
        run_history.artifact_history.loc[run_history.artifact_history["run_id"] == run_id].shape[0]
    )
    return pd.DataFrame(
        [
            {"metric": "Run ID", "value": str(run_row["run_id"])},
            {"metric": "Command", "value": str(run_row["command"])},
            {"metric": "Stage", "value": str(run_row["stage"])},
            {"metric": "Started at", "value": str(run_row["started_at_utc"])},
            {"metric": "Recorded at", "value": str(run_row["recorded_at_utc"])},
            {"metric": "Artifact groups", "value": f"{float(run_row['artifact_groups']):,.0f}"},
            {"metric": "Artifacts", "value": f"{artifact_count:,}"},
        ]
    )


def build_executive_briefing(
    monthly_view: pd.DataFrame,
    retention: pd.DataFrame,
    metrics: dict[str, float],
) -> list[str]:
    if monthly_view.empty:
        return ["No monthly revenue periods are available for the current filter window."]

    period_summary = summarize_period_performance(monthly_view)
    revenue_signals = rolling_revenue_signals(monthly_view)
    churn_proxy = float(metrics.get("churn_rate_proxy", 0.0))
    strongest, weakest = cohort_extremes(retention)
    strongest_cohort = (
        str(strongest.iloc[0]["cohort_month"]) if not strongest.empty else "no cohort available"
    )
    weakest_cohort = (
        str(weakest.iloc[0]["cohort_month"]) if not weakest.empty else "no cohort available"
    )
    current_month = str(period_summary["current_month"] or "current period")
    current_revenue = float(period_summary["current_revenue"] or 0.0)
    delta_ratio = period_summary["delta_ratio"]
    rolling_average = float(revenue_signals["rolling_3m_avg"] or 0.0)

    movement = (
        f"{delta_ratio:.1%} versus the prior month"
        if delta_ratio is not None
        else "with no prior month available for comparison"
    )
    return [
        (
            f"Revenue closed at {format_currency(current_revenue)} in {current_month}, "
            f"{movement}."
        ),
        (
            f"The rolling 3M average is {format_currency(rolling_average)} and the churn proxy "
            f"currently sits at {churn_proxy:.1%}."
        ),
        (
            f"Retention strength is anchored by cohort {strongest_cohort}, while cohort "
            f"{weakest_cohort} deserves closer review."
        ),
    ]


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")


def render_overview(
    labels: dict[str, str],
    data: DashboardData,
    monthly_view: pd.DataFrame,
) -> None:
    hydrate_session_from_query_params(["overview_selected_cohort"])
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
    with st.expander(labels["executive_briefing_title"], expanded=True):
        render_panel_header(labels["executive_briefing_title"], labels["executive_briefing_copy"])
        briefing_lines = build_executive_briefing(monthly_view, data.retention, data.metrics)
        for insight in briefing_lines:
            st.markdown(f"- {insight}")
        st.download_button(
            labels["export_briefing"],
            data="\n".join(briefing_lines),
            file_name="executive_briefing.txt",
            mime="text/plain",
        )
        st.download_button(
            labels["export_monthly_view"],
            data=dataframe_to_csv_bytes(monthly_view),
            file_name="monthly_revenue_view.csv",
            mime="text/csv",
        )

    trend_col, retention_col = st.columns([1.35, 1.0], gap="large")
    with trend_col:
        with st.container():
            render_section_intro(
                labels["trend_label"],
                labels["trend_title"],
                labels["trend_copy"],
            )
            if monthly_view.empty:
                render_empty_state(labels["trend_title"], labels["artifacts_empty"])
            else:
                render_panel_header(labels["trend_title"], labels["trend_copy"])
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
                st.altair_chart(
                    build_revenue_trend_chart(monthly_view),
                    use_container_width=True,
                )

    with retention_col:
        with st.container():
            render_section_intro(
                labels["retention_label"],
                labels["retention_title"],
                labels["retention_copy"],
            )
            if data.retention.empty:
                render_empty_state(labels["retention_title"], labels["artifacts_empty"])
            else:
                render_panel_header(labels["retention_title"], labels["retention_copy"])
                st.altair_chart(
                    build_retention_chart(data.retention),
                    use_container_width=True,
                )
                strongest, weakest = cohort_extremes(data.retention)
                cohort_tabs = st.tabs([labels["top_cohorts"], labels["risk_cohorts"]])
                with cohort_tabs[0]:
                    strongest_display = strongest.copy()
                    strongest_display["retention_rate"] = strongest_display["retention_rate"].map(
                        lambda value: f"{value:.1%}"
                    )
                    render_table_card(strongest_display)
                with cohort_tabs[1]:
                    weakest_display = weakest.copy()
                    weakest_display["retention_rate"] = weakest_display["retention_rate"].map(
                        lambda value: f"{value:.1%}"
                    )
                    render_table_card(weakest_display)
                with st.expander(labels["retention_title"], expanded=False):
                    retention_display = data.retention.copy()
                    retention_display["retention_rate"] = retention_display["retention_rate"].map(
                        lambda value: f"{value:.1%}"
                    )
                    render_table_card(retention_display)
                with st.expander(labels["cohort_spotlight_title"], expanded=False):
                    cohort_options = data.retention["cohort_month"].astype(str).tolist()
                    current_cohort = st.session_state.get("overview_selected_cohort")
                    cohort_index = (
                        cohort_options.index(current_cohort)
                        if isinstance(current_cohort, str) and current_cohort in cohort_options
                        else 0
                    )
                    selected_cohort = st.selectbox(
                        labels["cohort_spotlight_select"],
                        options=cohort_options,
                        index=cohort_index,
                        key="overview_selected_cohort",
                    )
                    spotlight = build_cohort_spotlight(data.retention, selected_cohort)
                    render_table_card(spotlight)
                    cohort_row = data.retention.loc[
                        data.retention["cohort_month"].astype(str) == selected_cohort
                    ].iloc[0]
                    median_retention = float(data.retention["retention_rate"].median())
                    delta_vs_median = float(cohort_row["retention_rate"]) - median_retention
                    comparison_copy = (
                        f"{delta_vs_median:+.1%} vs median retention"
                        if not pd.isna(delta_vs_median)
                        else "Median retention unavailable"
                    )
                    render_status_card(
                        labels["cohort_benchmark_title"],
                        f"{float(cohort_row['retention_rate']):.1%}",
                        comparison_copy,
                    )
                    st.download_button(
                        labels["export_cohort_spotlight"],
                        data=dataframe_to_csv_bytes(spotlight),
                        file_name=f"cohort_spotlight_{selected_cohort}.csv",
                        mime="text/csv",
                    )
    render_share_snapshot(
        labels,
        state_keys=[
            "dashboard_language",
            "dashboard_source_mode",
            "dashboard_start_month",
            "dashboard_end_month",
            "overview_selected_cohort",
        ],
        snapshot_name="overview",
    )


def render_customer_health(labels: dict[str, str], customer_360: pd.DataFrame) -> None:
    hydrate_session_from_query_params(
        [
            "customers_min_orders",
            "customers_search_term",
            "customers_selected_customer",
        ]
    )
    render_section_intro(
        labels["customers_label"],
        labels["customers_title"],
        labels["customers_copy"],
    )
    filter_col, search_col = st.columns([0.35, 0.65], gap="large")
    with filter_col:
        minimum_orders = st.slider(
            labels["min_orders"],
            min_value=0,
            max_value=10,
            value=1,
            key="customers_min_orders",
        )
    with search_col:
        search_term = st.text_input(
            labels["customer_search"],
            value="",
            placeholder="c1",
            key="customers_search_term",
        )

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
        render_panel_header(labels["segments_title"], labels["segments_copy"])
        segment_tabs = st.tabs([labels["segment_value"], labels["segment_recency"]])
        with segment_tabs[0]:
            st.altair_chart(
                build_segment_chart(value_mix, color="#0f766e"),
                use_container_width=True,
            )
        with segment_tabs[1]:
            st.altair_chart(
                build_segment_chart(recency_mix, color="#1d4ed8"),
                use_container_width=True,
            )

    with top_customers_col:
        render_panel_header(labels["top_customers"], labels["customers_copy"])
        top_customers = filtered_customers[
            ["customer_id", "total_spent", "total_orders", "days_since_last_purchase"]
        ].head(8)
        st.altair_chart(
            build_top_customers_chart(top_customers),
            use_container_width=True,
        )
        render_table_card(
            top_customers.assign(
                health=top_customers["days_since_last_purchase"].astype(float).map(risk_band),
                value_tier=top_customers["total_spent"].astype(float).map(value_band),
            ).rename(
                columns={
                    "customer_id": "Customer",
                    "total_spent": "Total spent",
                    "total_orders": "Orders",
                    "days_since_last_purchase": "Days inactive",
                    "health": "Health",
                    "value_tier": "Value tier",
                }
            ),
            formatters={
                "Total spent": ",.2f",
                "Orders": ",.0f",
                "Days inactive": ",.0f",
            },
            chip_columns={
                "Health": {
                    "Healthy": "success",
                    "Monitor": "warning",
                    "At risk": "danger",
                    "Critical": "danger",
                },
                "Value tier": {
                    "High value": "info",
                    "Mid value": "neutral",
                    "Low value": "neutral",
                },
            },
            bar_columns={"Total spent": float(top_customers["total_spent"].max())},
        )

        at_risk = filtered_customers[
            filtered_customers["days_since_last_purchase"].fillna(9999) > 90
        ].head(8)
        render_panel_header(labels["customer_opportunity"], labels["quality_copy"])
        at_risk_display = (
            (
                at_risk[["customer_id", "total_spent", "days_since_last_purchase"]]
                if not at_risk.empty
                else pd.DataFrame(
                    columns=["customer_id", "total_spent", "days_since_last_purchase"]
                )
            )
            .assign(
                priority=(
                    at_risk["total_spent"].astype(float).map(value_band)
                    if not at_risk.empty
                    else pd.Series(dtype=str)
                ),
                health=(
                    at_risk["days_since_last_purchase"].astype(float).map(risk_band)
                    if not at_risk.empty
                    else pd.Series(dtype=str)
                ),
            )
            .rename(
                columns={
                    "customer_id": "Customer",
                    "total_spent": "Total spent",
                    "days_since_last_purchase": "Risk window",
                    "priority": "Priority",
                    "health": "Health",
                }
            )
        )
        render_table_card(
            at_risk_display,
            formatters={
                "Total spent": ",.2f",
                "Risk window": ",.0f",
            },
            chip_columns={
                "Priority": {
                    "High value": "danger",
                    "Mid value": "warning",
                    "Low value": "neutral",
                },
                "Health": {
                    "Healthy": "success",
                    "Monitor": "warning",
                    "At risk": "danger",
                    "Critical": "danger",
                },
            },
        )
        st.download_button(
            labels["export_customer_risk"],
            data=dataframe_to_csv_bytes(at_risk_display),
            file_name="at_risk_customers.csv",
            mime="text/csv",
        )

    with table_col:
        render_panel_header(labels["customer_table"], labels["customers_copy"])
        display_columns = [
            "customer_id",
            "total_orders",
            "total_spent",
            "avg_order_value",
            "days_since_last_purchase",
            "first_purchase",
            "last_purchase",
        ]
        customer_table = (
            filtered_customers[display_columns]
            .head(25)
            .assign(
                health=lambda frame: frame["days_since_last_purchase"].astype(float).map(risk_band),
                value_tier=lambda frame: frame["total_spent"].astype(float).map(value_band),
            )
            .rename(
                columns={
                    "customer_id": "Customer",
                    "total_orders": "Orders",
                    "total_spent": "Total spent",
                    "avg_order_value": "AOV",
                    "days_since_last_purchase": "Days inactive",
                    "first_purchase": "First purchase",
                    "last_purchase": "Last purchase",
                    "health": "Health",
                    "value_tier": "Value tier",
                }
            )
        )
        render_table_card(
            customer_table,
            formatters={
                "Orders": ",.0f",
                "Total spent": ",.2f",
                "AOV": ",.2f",
                "Days inactive": ",.0f",
            },
            chip_columns={
                "Health": {
                    "Healthy": "success",
                    "Monitor": "warning",
                    "At risk": "danger",
                    "Critical": "danger",
                },
                "Value tier": {
                    "High value": "info",
                    "Mid value": "neutral",
                    "Low value": "neutral",
                },
            },
            bar_columns={"Total spent": float(customer_table["Total spent"].max())},
        )
        with st.expander(labels["customer_spotlight_title"], expanded=False):
            customer_options = filtered_customers["customer_id"].astype(str).tolist()
            current_customer = st.session_state.get("customers_selected_customer")
            customer_index = (
                customer_options.index(current_customer)
                if isinstance(current_customer, str) and current_customer in customer_options
                else 0
            )
            selected_customer = st.selectbox(
                labels["customer_spotlight_select"],
                options=customer_options,
                index=customer_index,
                key="customers_selected_customer",
            )
            selected_row = filtered_customers.loc[
                filtered_customers["customer_id"].astype(str) == selected_customer
            ].iloc[0]
            spotlight = build_customer_spotlight(selected_row)
            render_table_card(spotlight)
            st.download_button(
                labels["export_customer_spotlight"],
                data=dataframe_to_csv_bytes(spotlight),
                file_name=f"customer_spotlight_{selected_customer}.csv",
                mime="text/csv",
            )
        st.download_button(
            labels["export_customer_view"],
            data=dataframe_to_csv_bytes(filtered_customers),
            file_name="customer_health_view.csv",
            mime="text/csv",
        )
    render_share_snapshot(
        labels,
        state_keys=[
            "dashboard_language",
            "dashboard_source_mode",
            "dashboard_start_month",
            "dashboard_end_month",
            "customers_min_orders",
            "customers_search_term",
            "customers_selected_customer",
        ],
        snapshot_name="customer_health",
    )


def render_run_history(
    labels: dict[str, str],
    run_history: RunHistoryData,
) -> None:
    hydrate_session_from_query_params(
        [
            "run_compare_left",
            "run_compare_right",
            "runs_selected_run",
        ]
    )
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
        render_panel_header(labels["run_history_title"], labels["run_history_copy"])
        render_table_card(manifest_display)
    with history_tabs[1]:
        if run_history.catalog.empty:
            render_empty_state(labels["run_catalog_title"], labels["run_history_empty"])
        else:
            render_panel_header(labels["run_catalog_title"], labels["run_catalog_copy"])
            st.caption(labels["run_catalog_copy"])
            render_table_card(run_history.catalog)
    with history_tabs[2]:
        if run_history.sql_history.empty:
            render_empty_state(labels["run_sql_title"], labels["run_history_empty"])
        else:
            render_panel_header(labels["run_sql_title"], labels["run_sql_copy"])
            st.caption(labels["run_sql_copy"])
            render_table_card(run_history.sql_history)

    st.markdown(f"### {labels['run_compare_title']}")
    compare_cols = st.columns(2, gap="large")
    run_options = run_history.manifests["run_id"].tolist()
    current_left_run = st.session_state.get("run_compare_left")
    current_right_run = st.session_state.get("run_compare_right")
    left_index = (
        run_options.index(current_left_run)
        if isinstance(current_left_run, str) and current_left_run in run_options
        else 0
    )
    right_index = (
        run_options.index(current_right_run)
        if isinstance(current_right_run, str) and current_right_run in run_options
        else 1 if len(run_options) > 1 else 0
    )
    with compare_cols[0]:
        left_run = st.selectbox(
            labels["run_compare_left"],
            options=run_options,
            index=left_index,
            key="run_compare_left",
        )
    with compare_cols[1]:
        right_run = st.selectbox(
            labels["run_compare_right"],
            options=run_options,
            index=right_index,
            key="run_compare_right",
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
    comparison_table = build_run_comparison_table(left_only, shared_artifacts, right_only)
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
                render_table_card(frame)
    if not comparison_table.empty:
        render_panel_header(labels["run_compare_title"], labels["run_compare_summary"])
        render_table_card(
            comparison_table,
            chip_columns={
                "comparison_status": {
                    "Reference only": "warning",
                    "Shared": "success",
                    "Comparison only": "info",
                }
            },
        )
        st.download_button(
            labels["export_run_compare"],
            data=dataframe_to_csv_bytes(comparison_table),
            file_name=f"run_compare_{left_run}_vs_{right_run}.csv",
            mime="text/csv",
        )
    with st.expander(labels["run_spotlight_title"], expanded=False):
        current_spotlight_run = st.session_state.get("runs_selected_run")
        spotlight_index = (
            run_options.index(current_spotlight_run)
            if isinstance(current_spotlight_run, str) and current_spotlight_run in run_options
            else 0
        )
        spotlight_run = st.selectbox(
            labels["run_spotlight_select"],
            options=run_options,
            index=spotlight_index,
            key="runs_selected_run",
        )
        spotlight = build_run_spotlight(run_history, spotlight_run)
        render_table_card(spotlight)
        spotlight_artifacts = run_history.artifact_history.loc[
            run_history.artifact_history["run_id"] == spotlight_run,
            ["stage_name", "artifact_path"],
        ]
        if spotlight_artifacts.empty:
            render_empty_state(labels["run_spotlight_title"], labels["run_history_empty"])
        else:
            render_table_card(spotlight_artifacts)
        st.download_button(
            labels["export_run_spotlight"],
            data=dataframe_to_csv_bytes(spotlight_artifacts),
            file_name=f"run_spotlight_{spotlight_run}.csv",
            mime="text/csv",
        )
    render_share_snapshot(
        labels,
        state_keys=[
            "dashboard_language",
            "dashboard_source_mode",
            "dashboard_start_month",
            "dashboard_end_month",
            "run_compare_left",
            "run_compare_right",
            "runs_selected_run",
        ],
        snapshot_name="run_history",
    )


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
        render_panel_header(labels["artifacts_title"], labels["operations_copy"])
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
            freshness_state = pd.to_datetime(
                artifact_df["updated_utc"],
                errors="coerce",
                utc=True,
            ).map(
                lambda timestamp: (
                    "Recent"
                    if pd.notna(timestamp)
                    and (datetime.now(UTC) - timestamp.to_pydatetime()).total_seconds() / 3600 <= 24
                    else "Stale" if pd.notna(timestamp) else "Unknown"
                )
            )
            renamed["Freshness"] = freshness_state
            render_table_card(
                renamed,
                formatters={labels["artifact_rows"]: ",.0f"},
                chip_columns={
                    labels["artifact_run"]: {"-": "neutral", "__default__": "info"},
                    "Freshness": {
                        "Recent": "success",
                        "Stale": "warning",
                        "Unknown": "neutral",
                    },
                },
                bar_columns={labels["artifact_rows"]: float(artifact_df["rows"].max() or 0)},
            )

    with right_col:
        with st.expander(labels["quality_title"], expanded=True):
            st.write(labels["quality_copy"])
            st.code("ridp run-pipeline all --run-id ops-review-001", language="bash")
