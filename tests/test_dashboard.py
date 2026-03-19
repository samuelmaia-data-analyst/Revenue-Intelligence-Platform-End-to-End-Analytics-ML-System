from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

import dashboard.components as components
import dashboard.data_access as data_access
import dashboard.views as views
from dashboard.components import render_sidebar
from dashboard.data_access import load_run_history, resolve_dashboard_sources
from dashboard.views import (
    artifact_metadata,
    build_cohort_spotlight,
    build_customer_focus,
    build_customer_spotlight,
    build_executive_briefing,
    build_run_comparison_table,
    build_run_spotlight,
    cohort_extremes,
    compare_run_artifacts,
    customer_segments,
    render_customer_health,
    render_operations,
    render_overview,
    render_run_history,
    risk_band,
    rolling_revenue_signals,
    summarize_period_performance,
    value_band,
)
from ridp.config import DashboardSettings, DataDirectories
from tests.dashboard_test_utils import (
    FIXTURE_ROOT,
    FakeStreamlit,
    fixture_dashboard_data,
    fixture_run_history,
    fixture_source_paths,
    load_module_from_path,
)


def test_summarize_period_performance_returns_current_and_prior_values() -> None:
    monthly_view = pd.DataFrame(
        [
            {"order_month": "2018-01", "revenue": 100.0},
            {"order_month": "2018-02", "revenue": 140.0},
        ]
    )

    summary = summarize_period_performance(monthly_view)

    assert summary["current_month"] == "2018-02"
    assert summary["current_revenue"] == 140.0
    assert summary["prior_month"] == "2018-01"
    assert summary["prior_revenue"] == 100.0
    assert summary["delta_ratio"] == 0.4


def test_cohort_extremes_identifies_best_and_worst_retention() -> None:
    retention = pd.DataFrame(
        [
            {
                "cohort_month": "2018-01",
                "customers": 10,
                "retained_customers": 8,
                "retention_rate": 0.8,
            },
            {
                "cohort_month": "2018-02",
                "customers": 8,
                "retained_customers": 2,
                "retention_rate": 0.25,
            },
            {
                "cohort_month": "2018-03",
                "customers": 12,
                "retained_customers": 9,
                "retention_rate": 0.75,
            },
        ]
    )

    strongest, weakest = cohort_extremes(retention)

    assert strongest.iloc[0]["cohort_month"] == "2018-01"
    assert weakest.iloc[0]["cohort_month"] == "2018-02"


def test_rolling_revenue_signals_returns_moving_average_and_quarter_delta() -> None:
    monthly_view = pd.DataFrame(
        [
            {"order_month": "2018-01", "revenue": 100.0},
            {"order_month": "2018-02", "revenue": 120.0},
            {"order_month": "2018-03", "revenue": 140.0},
            {"order_month": "2018-04", "revenue": 150.0},
            {"order_month": "2018-05", "revenue": 160.0},
            {"order_month": "2018-06", "revenue": 170.0},
        ]
    )

    signals = rolling_revenue_signals(monthly_view)

    assert signals["rolling_3m_avg"] == 160.0
    assert signals["quarter_delta_ratio"] == 1 / 3


def test_customer_focus_filters_and_sorts_priority_customers() -> None:
    customer_360 = pd.DataFrame(
        [
            {
                "customer_id": "c1",
                "total_orders": 1,
                "total_spent": 100.0,
                "days_since_last_purchase": 10,
            },
            {
                "customer_id": "c2",
                "total_orders": 3,
                "total_spent": 500.0,
                "days_since_last_purchase": 120,
            },
            {
                "customer_id": "c3",
                "total_orders": 2,
                "total_spent": 220.0,
                "days_since_last_purchase": 20,
            },
        ]
    )

    filtered = build_customer_focus(customer_360, search_term="c", minimum_orders=2)

    assert filtered["customer_id"].tolist() == ["c2", "c3"]


def test_customer_segments_builds_value_and_recency_mix() -> None:
    customer_360 = pd.DataFrame(
        [
            {"customer_id": "c1", "total_spent": 50.0, "days_since_last_purchase": 10},
            {"customer_id": "c2", "total_spent": 180.0, "days_since_last_purchase": 40},
            {"customer_id": "c3", "total_spent": 400.0, "days_since_last_purchase": 120},
        ]
    )

    value_mix, recency_mix = customer_segments(customer_360)

    assert set(value_mix["segment"]) == {"Low value", "Mid value", "High value"}
    assert set(recency_mix["segment"]) == {"0-30 days", "31-90 days", "90+ days"}


def test_risk_and_value_band_classify_customer_priority() -> None:
    assert risk_band(10) == "Healthy"
    assert risk_band(70) == "Monitor"
    assert risk_band(100) == "At risk"
    assert risk_band(150) == "Critical"
    assert value_band(50.0) == "Low value"
    assert value_band(180.0) == "Mid value"
    assert value_band(400.0) == "High value"


def test_spotlight_builders_return_readable_tables() -> None:
    customer_row = pd.Series(
        {
            "customer_id": "c1",
            "total_orders": 3,
            "total_spent": 250.0,
            "avg_order_value": 83.33,
            "days_since_last_purchase": 91.0,
            "first_purchase": "2018-01-01",
            "last_purchase": "2018-03-01",
        }
    )
    retention = pd.DataFrame(
        [
            {
                "cohort_month": "2018-01",
                "customers": 10,
                "retained_customers": 8,
                "retention_rate": 0.8,
            }
        ]
    )
    run_history = fixture_run_history()

    customer_spotlight = build_customer_spotlight(customer_row)
    cohort_spotlight = build_cohort_spotlight(retention, "2018-01")
    run_spotlight = build_run_spotlight(run_history, str(run_history.manifests.iloc[0]["run_id"]))

    assert "Health" in customer_spotlight["metric"].tolist()
    assert "Retention" in cohort_spotlight["metric"].tolist()
    assert "Artifacts" in run_spotlight["metric"].tolist()


def test_build_run_comparison_table_emits_status_rows() -> None:
    frame = build_run_comparison_table(["a"], ["b"], ["c"])

    assert set(frame["comparison_status"]) == {"Reference only", "Shared", "Comparison only"}


def test_build_executive_briefing_returns_high_signal_summary() -> None:
    monthly_view = pd.DataFrame(
        [
            {"order_month": "2018-01", "revenue": 100.0},
            {"order_month": "2018-02", "revenue": 140.0},
            {"order_month": "2018-03", "revenue": 160.0},
        ]
    )
    retention = pd.DataFrame(
        [
            {
                "cohort_month": "2018-01",
                "customers": 10,
                "retained_customers": 8,
                "retention_rate": 0.8,
            },
            {
                "cohort_month": "2018-02",
                "customers": 8,
                "retained_customers": 3,
                "retention_rate": 0.375,
            },
        ]
    )

    briefing = build_executive_briefing(
        monthly_view,
        retention,
        {"churn_rate_proxy": 0.22},
    )

    assert len(briefing) == 3
    assert "Revenue closed" in briefing[0]


def test_load_run_history_reads_manifests_and_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs"
    run_dir.mkdir()
    (run_dir / "run-001.json").write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "command": "run-pipeline",
                "stage": "all",
                "started_at_utc": "2026-03-19T10:00:00+00:00",
                "recorded_at_utc": "2026-03-19T10:01:00+00:00",
                "artifacts": {
                    "ingestion": ["data/bronze/a.csv"],
                    "feature_engineering": ["data/gold/b.csv"],
                },
            }
        ),
        encoding="utf-8",
    )

    history = load_run_history(str(run_dir))

    assert history.manifests.iloc[0]["run_id"] == "run-001"
    assert set(history.artifact_history["stage_name"]) == {"ingestion", "feature_engineering"}


def test_load_run_history_reads_sqlite_registry(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs"
    run_dir.mkdir()
    with sqlite3.connect(run_dir / "run_history.db") as connection:
        connection.execute("""
            CREATE TABLE run_history (
                run_id TEXT PRIMARY KEY,
                command TEXT NOT NULL,
                stage TEXT NOT NULL,
                started_at_utc TEXT NOT NULL,
                recorded_at_utc TEXT NOT NULL,
                artifact_groups INTEGER NOT NULL,
                artifact_count INTEGER NOT NULL,
                snapshot_root TEXT
            )
            """)
        connection.execute("""
            INSERT INTO run_history VALUES (
                'run-001',
                'run-pipeline',
                'all',
                '2026-03-19T10:00:00+00:00',
                '2026-03-19T10:01:00+00:00',
                3,
                9,
                'data/run_artifacts/run-001'
            )
            """)
        connection.commit()

    history = load_run_history(str(run_dir))

    assert history.sql_history.iloc[0]["run_id"] == "run-001"
    assert int(history.sql_history.iloc[0]["artifact_count"]) == 9


def test_load_dashboard_data_prefers_serving_store_when_available(tmp_path: Path) -> None:
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    serving_db = tmp_path / "serving.db"
    pd.DataFrame(
        [{"metric": "gmv_total", "value": 999.0}, {"metric": "aov", "value": 111.0}]
    ).to_csv(gold_dir / "business_kpis.csv", index=False)
    pd.DataFrame([{"order_month": "2018-01", "revenue": 10.0}]).to_csv(
        gold_dir / "kpi_monthly_revenue.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "customer_id": "c1",
                "total_orders": 1,
                "total_spent": 10.0,
                "first_purchase": "2018-01-01 10:00:00",
                "last_purchase": "2018-01-01 10:00:00",
                "days_since_last_purchase": 10,
                "avg_order_value": 10.0,
            }
        ]
    ).to_csv(gold_dir / "customer_360.csv", index=False)
    with sqlite3.connect(serving_db) as connection:
        pd.DataFrame(
            [{"metric": "gmv_total", "value": 412.0}, {"metric": "aov", "value": 137.33}]
        ).to_sql("business_kpis", connection, if_exists="replace", index=False)
        pd.DataFrame([{"order_month": "2018-06", "revenue": 170.0}]).to_sql(
            "kpi_monthly_revenue", connection, if_exists="replace", index=False
        )
        pd.DataFrame(
            [
                {
                    "customer_id": "c9",
                    "total_orders": 2,
                    "total_spent": 170.0,
                    "first_purchase": "2018-02-01 10:00:00",
                    "last_purchase": "2018-03-01 10:00:00",
                    "days_since_last_purchase": 90,
                    "avg_order_value": 85.0,
                }
            ]
        ).to_sql("customer_360", connection, if_exists="replace", index=False)

    dashboard_data = data_access.load_dashboard_data(str(gold_dir), str(serving_db))

    assert dashboard_data.metrics["gmv_total"] == 412.0
    assert dashboard_data.monthly_revenue.iloc[0]["order_month"] == "2018-06"
    assert dashboard_data.customer_360.iloc[0]["customer_id"] == "c9"


def test_resolve_dashboard_sources_falls_back_to_demo_assets_in_auto_mode(tmp_path: Path) -> None:
    directories = DataDirectories(
        raw=tmp_path / "raw",
        bronze=tmp_path / "bronze",
        silver=tmp_path / "silver",
        gold=tmp_path / "gold",
        serving=tmp_path / "serving.db",
        models=tmp_path / "models",
        runs=tmp_path / "runs",
        run_artifacts=tmp_path / "run_artifacts",
        run_history_db=tmp_path / "runs" / "run_history.db",
    )
    settings = DashboardSettings(
        demo_mode="AUTO",
        demo_assets_root=FIXTURE_ROOT,
    )

    source_paths = resolve_dashboard_sources(directories, settings)

    assert source_paths.demo_active is True
    assert source_paths.gold_dir == FIXTURE_ROOT / "gold"
    assert source_paths.run_dir == FIXTURE_ROOT / "runs"


def test_resolve_dashboard_sources_respects_off_mode(tmp_path: Path) -> None:
    directories = DataDirectories(
        raw=tmp_path / "raw",
        bronze=tmp_path / "bronze",
        silver=tmp_path / "silver",
        gold=tmp_path / "gold",
        serving=tmp_path / "serving.db",
        models=tmp_path / "models",
        runs=tmp_path / "runs",
        run_artifacts=tmp_path / "run_artifacts",
        run_history_db=tmp_path / "runs" / "run_history.db",
    )
    settings = DashboardSettings(
        demo_mode="OFF",
        demo_assets_root=FIXTURE_ROOT,
    )

    source_paths = resolve_dashboard_sources(directories, settings)

    assert source_paths.demo_active is False
    assert source_paths.gold_dir == directories.gold
    assert source_paths.run_dir == directories.runs


def test_resolve_dashboard_sources_respects_sidebar_session_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    directories = DataDirectories(
        raw=tmp_path / "raw",
        bronze=tmp_path / "bronze",
        silver=tmp_path / "silver",
        gold=tmp_path / "gold",
        serving=tmp_path / "serving.db",
        models=tmp_path / "models",
        runs=tmp_path / "runs",
        run_artifacts=tmp_path / "run_artifacts",
        run_history_db=tmp_path / "runs" / "run_history.db",
    )
    settings = DashboardSettings(
        demo_mode="AUTO",
        demo_assets_root=FIXTURE_ROOT,
    )
    fake_st = FakeStreamlit()
    fake_st.session_state["dashboard_source_mode"] = "ON"
    monkeypatch.setattr(data_access, "st", fake_st)

    source_paths = resolve_dashboard_sources(directories, settings)

    assert source_paths.demo_active is True
    assert source_paths.demo_mode == "ON"
    assert source_paths.gold_dir == FIXTURE_ROOT / "gold"


def test_compare_run_artifacts_returns_shared_and_unique_paths(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs"
    run_dir.mkdir()
    for run_id, artifacts in {
        "run-001": {"feature_engineering": ["data/gold/a.csv", "data/gold/shared.csv"]},
        "run-002": {"feature_engineering": ["data/gold/b.csv", "data/gold/shared.csv"]},
    }.items():
        (run_dir / f"{run_id}.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "command": "run-pipeline",
                    "stage": "all",
                    "started_at_utc": "2026-03-19T10:00:00+00:00",
                    "recorded_at_utc": "2026-03-19T10:01:00+00:00",
                    "artifacts": artifacts,
                }
            ),
            encoding="utf-8",
        )

    history = load_run_history(str(run_dir))
    comparison = compare_run_artifacts(history, "run-001", "run-002")

    assert comparison["left_only"] == ["data/gold/a.csv"]
    assert comparison["shared"] == ["data/gold/shared.csv"]
    assert comparison["right_only"] == ["data/gold/b.csv"]


def test_artifact_metadata_reads_metadata_file(tmp_path: Path) -> None:
    metadata_dir = tmp_path / "gold"
    metadata_dir.mkdir()
    (metadata_dir / "business_kpis.metadata.json").write_text(
        json.dumps(
            {
                "dataset_name": "business_kpis.csv",
                "row_count": 4,
                "generated_at_utc": "2026-03-20T10:00:00+00:00",
                "run_id": "demo-run-002",
            }
        ),
        encoding="utf-8",
    )

    artifact_df = artifact_metadata(metadata_dir)

    assert artifact_df.iloc[0]["artifact"] == "business_kpis.csv"
    assert artifact_df.iloc[0]["run_id"] == "demo-run-002"


def test_render_sidebar_persists_workspace_source_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import dashboard.content as content

    fake_st = FakeStreamlit()
    monkeypatch.setattr(components, "st", fake_st)

    start_month, end_month = render_sidebar(
        content.LANGS["English"],
        available_months=["2018-01", "2018-02"],
    )

    assert start_month == "2018-01"
    assert end_month == "2018-02"
    assert fake_st.session_state["dashboard_source_mode"] == "AUTO"


def test_render_sidebar_reuses_persisted_month_range(monkeypatch: pytest.MonkeyPatch) -> None:
    import dashboard.content as content

    fake_st = FakeStreamlit()
    fake_st.session_state["dashboard_start_month"] = "2018-02"
    fake_st.session_state["dashboard_end_month"] = "2018-03"
    monkeypatch.setattr(components, "st", fake_st)

    start_month, end_month = render_sidebar(
        content.LANGS["English"],
        available_months=["2018-01", "2018-02", "2018-03"],
    )

    assert start_month == "2018-02"
    assert end_month == "2018-03"


def test_render_sidebar_hydrates_state_from_query_params(monkeypatch: pytest.MonkeyPatch) -> None:
    import dashboard.content as content

    fake_st = FakeStreamlit()
    fake_st.query_params["dashboard_start_month"] = "2018-02"
    fake_st.query_params["dashboard_end_month"] = "2018-03"
    monkeypatch.setattr(components, "st", fake_st)

    start_month, end_month = render_sidebar(
        content.LANGS["English"],
        available_months=["2018-01", "2018-02", "2018-03"],
    )

    assert start_month == "2018-02"
    assert end_month == "2018-03"
    assert fake_st.session_state["dashboard_start_month"] == "2018-02"


def test_dashboard_pages_import_and_expose_main() -> None:
    paths = [
        Path("dashboard/app.py"),
        Path("dashboard/pages/01_Customer_Health.py"),
        Path("dashboard/pages/02_Operations.py"),
        Path("dashboard/pages/03_Run_History.py"),
    ]

    for index, module_path in enumerate(paths, start=1):
        module = load_module_from_path(module_path, f"dashboard_page_{index}")
        assert hasattr(module, "main")


def test_dashboard_views_render_without_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import dashboard.content as content

    fake_st = FakeStreamlit()
    dashboard_data = fixture_dashboard_data()
    run_history = fixture_run_history()
    labels = content.LANGS["English"]
    monthly_view = dashboard_data.monthly_revenue.copy()

    monkeypatch.setattr(views, "st", fake_st)
    monkeypatch.setattr(views, "render_section_intro", lambda *args, **kwargs: None)
    monkeypatch.setattr(views, "render_metric_card_with_delta", lambda *args, **kwargs: None)
    monkeypatch.setattr(views, "render_panel_header", lambda *args, **kwargs: None)
    monkeypatch.setattr(views, "render_status_card", lambda *args, **kwargs: None)
    monkeypatch.setattr(views, "render_empty_state", lambda *args, **kwargs: None)
    monkeypatch.setattr(views, "render_table_card", lambda *args, **kwargs: None)

    render_overview(labels, dashboard_data, monthly_view)
    render_customer_health(labels, dashboard_data.customer_360)
    render_operations(labels, FIXTURE_ROOT / "gold")
    render_run_history(labels, run_history)


def test_dashboard_pages_main_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    import dashboard.content as content

    fake_st = FakeStreamlit()
    dashboard_data = fixture_dashboard_data()
    run_history = fixture_run_history()
    page_paths = [
        (Path("dashboard/app.py"), "dashboard_app_test"),
        (Path("dashboard/pages/01_Customer_Health.py"), "dashboard_customer_page_test"),
        (Path("dashboard/pages/02_Operations.py"), "dashboard_operations_page_test"),
        (Path("dashboard/pages/03_Run_History.py"), "dashboard_run_history_page_test"),
    ]

    for module_path, module_name in page_paths:
        module = load_module_from_path(module_path, module_name)
        monkeypatch.setattr(module, "st", fake_st)
        monkeypatch.setattr(module, "inject_global_styles", lambda: None)
        monkeypatch.setattr(module, "render_dashboard_source_notice", lambda *args, **kwargs: None)
        monkeypatch.setattr(module, "render_footer", lambda *args, **kwargs: None)
        monkeypatch.setattr(module, "render_hero", lambda *args, **kwargs: None)
        monkeypatch.setattr(module, "render_workspace_strip", lambda *args, **kwargs: None)
        monkeypatch.setattr(
            module, "render_sidebar", lambda *args, **kwargs: ("2018-01", "2018-06")
        )
        monkeypatch.setattr(module, "get_labels", lambda: content.LANGS["English"])
        monkeypatch.setattr(module, "load_dashboard_data", lambda *_args, **_kwargs: dashboard_data)
        monkeypatch.setattr(
            module,
            "resolve_dashboard_sources",
            lambda *_args, **_kwargs: fixture_source_paths(),
        )
        if hasattr(module, "load_run_history"):
            monkeypatch.setattr(module, "load_run_history", lambda *_args, **_kwargs: run_history)
        if hasattr(module, "render_overview"):
            monkeypatch.setattr(module, "render_overview", lambda *args, **kwargs: None)
        if hasattr(module, "render_customer_health"):
            monkeypatch.setattr(module, "render_customer_health", lambda *args, **kwargs: None)
        if hasattr(module, "render_operations"):
            monkeypatch.setattr(module, "render_operations", lambda *args, **kwargs: None)
        if hasattr(module, "render_run_history"):
            monkeypatch.setattr(module, "render_run_history", lambda *args, **kwargs: None)

        module.main()
