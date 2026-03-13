with scored as (
    select * from {{ ref('stg_scored_customers') }}
),
recommendations as (
    select * from {{ ref('stg_recommendations') }}
)

select
    sum(scored.monetary) as revenue_proxy,
    avg(recommendations.ltv) as avg_ltv,
    avg(recommendations.cac) as avg_cac,
    avg(recommendations.ltv_cac_ratio) as avg_ltv_cac_ratio,
    avg(case when recommendations.churn_probability >= 0.70 then 1.0 else 0.0 end) as high_churn_risk_pct
from scored
inner join recommendations
    on scored.customer_id = recommendations.customer_id
