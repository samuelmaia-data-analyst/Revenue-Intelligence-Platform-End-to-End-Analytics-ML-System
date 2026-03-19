from __future__ import annotations

import altair as alt
import pandas as pd

ChartLike = alt.Chart | alt.LayerChart


def _apply_chart_theme(chart: ChartLike) -> ChartLike:
    return chart.configure(
        view=alt.ViewConfig(strokeOpacity=0),
        axis=alt.AxisConfig(
            labelColor="#526072",
            titleColor="#334155",
            labelFontSize=12,
            titleFontSize=12,
            gridColor="rgba(148, 163, 184, 0.18)",
            domainColor="rgba(148, 163, 184, 0.28)",
            tickColor="rgba(148, 163, 184, 0.28)",
        ),
        legend=alt.LegendConfig(
            labelColor="#334155",
            titleColor="#0f172a",
        ),
    )


def _base_chart(data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(data)


def build_revenue_trend_chart(monthly_view: pd.DataFrame) -> ChartLike:
    chart_data = monthly_view.copy()
    chart_data["revenue"] = chart_data["revenue"].astype(float)
    month_order = chart_data["order_month"].astype(str).tolist()

    base = _base_chart(chart_data).encode(
        x=alt.X(
            "order_month:N",
            sort=month_order,
            title="Month",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("revenue:Q", title="Revenue"),
        tooltip=[
            alt.Tooltip("order_month:N", title="Month"),
            alt.Tooltip("revenue:Q", title="Revenue", format=",.2f"),
        ],
    )
    area = base.mark_area(color="#ccfbf1", opacity=0.75)
    line = base.mark_line(color="#0f766e", strokeWidth=3, point=alt.OverlayMarkDef(filled=True))
    return _apply_chart_theme(area + line)


def build_retention_chart(retention: pd.DataFrame) -> ChartLike:
    chart_data = retention.copy()
    chart_data["retention_rate"] = chart_data["retention_rate"].astype(float)
    order = chart_data["cohort_month"].astype(str).tolist()
    chart = (
        _base_chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X(
                "cohort_month:N",
                sort=order,
                title="Cohort",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y("retention_rate:Q", title="Retention rate", axis=alt.Axis(format="%")),
            color=alt.Color(
                "retention_rate:Q",
                scale=alt.Scale(range=["#bfdbfe", "#1d4ed8"]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("cohort_month:N", title="Cohort"),
                alt.Tooltip("customers:Q", title="Customers"),
                alt.Tooltip("retention_rate:Q", title="Retention", format=".1%"),
            ],
        )
    )
    return _apply_chart_theme(chart)


def build_segment_chart(
    segment_mix: pd.DataFrame,
    *,
    segment_column: str = "segment",
    value_column: str = "customers",
    color: str,
) -> ChartLike:
    chart_data = segment_mix.copy()
    chart_data[value_column] = chart_data[value_column].astype(float)
    chart = (
        _base_chart(chart_data)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X(f"{value_column}:Q", title="Customers"),
            y=alt.Y(f"{segment_column}:N", sort="-x", title=None),
            color=alt.value(color),
            tooltip=[
                alt.Tooltip(f"{segment_column}:N", title="Segment"),
                alt.Tooltip(f"{value_column}:Q", title="Customers", format=",.0f"),
            ],
        )
    )
    return _apply_chart_theme(chart)


def build_top_customers_chart(customers: pd.DataFrame) -> ChartLike:
    chart_data = customers.copy()
    chart_data["total_spent"] = chart_data["total_spent"].astype(float)
    chart = (
        _base_chart(chart_data)
        .mark_bar(
            cornerRadiusTopRight=6,
            cornerRadiusBottomRight=6,
            color="#0f766e",
        )
        .encode(
            x=alt.X("total_spent:Q", title="Total spent"),
            y=alt.Y("customer_id:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("customer_id:N", title="Customer"),
                alt.Tooltip("total_spent:Q", title="Total spent", format=",.2f"),
                alt.Tooltip("total_orders:Q", title="Orders", format=",.0f"),
                alt.Tooltip(
                    "days_since_last_purchase:Q",
                    title="Days since last purchase",
                    format=",.0f",
                ),
            ],
        )
    )
    return _apply_chart_theme(chart)
