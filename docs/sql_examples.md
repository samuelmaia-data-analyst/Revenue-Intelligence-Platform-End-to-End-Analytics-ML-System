# SQL Consumption Examples

These queries are intentionally small and practical. They show how a downstream analyst or partner team would consume the warehouse outputs without re-implementing pipeline logic.

## Channel Economics

```sql
SELECT
    acquisition_channel,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(avg_order_value), 2) AS avg_order_value
FROM fact_orders
GROUP BY acquisition_channel
ORDER BY total_revenue DESC;
```

## Best Recommendation Opportunities

```sql
SELECT
    customer_id,
    recommended_action,
    ROUND(potential_impact, 2) AS potential_impact,
    ROUND(churn_probability, 4) AS churn_probability
FROM mart_customer_recommendations
ORDER BY potential_impact DESC
LIMIT 10;
```

## Cohort Retention Snapshot

```sql
SELECT
    cohort_month,
    retention_month,
    ROUND(retention_rate, 4) AS retention_rate
FROM fct_cohort_retention
WHERE cohort_month >= '2025-01-01'
ORDER BY cohort_month, retention_month;
```

## Executive Revenue Lens

```sql
SELECT
    segment,
    COUNT(*) AS customers_in_scope,
    ROUND(AVG(ltv_cac_ratio), 2) AS avg_ltv_cac_ratio,
    ROUND(AVG(churn_probability), 4) AS avg_churn_probability
FROM mart_customer_recommendations
GROUP BY segment
ORDER BY avg_ltv_cac_ratio DESC;
```
