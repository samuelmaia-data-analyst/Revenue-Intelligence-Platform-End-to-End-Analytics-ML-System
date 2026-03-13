# Deployment Examples

This folder contains production-style orchestration examples for the platform.

## Airflow

- DAG path: `orchestration/airflow/dags/revenue_intelligence_platform_dag.py`
- runs the pipeline daily through a PythonOperator

## Prefect

- deployment example: `orchestration/prefect/revenue_intelligence_deployment.yaml`
- uses the `src.prefect_flow:run_prefect_flow` entrypoint

These assets are examples for deployment configuration and repository portability.
