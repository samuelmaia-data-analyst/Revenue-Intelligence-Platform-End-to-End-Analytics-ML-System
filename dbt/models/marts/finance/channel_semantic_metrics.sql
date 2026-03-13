with recommendations as (
    select * from {{ ref('stg_recommendations') }}
),
scored as (
    select * from {{ ref('stg_scored_customers') }}
)

select
    recommendations.channel,
    count(*) as customers_in_scope,
    avg(recommendations.ltv) as avg_ltv,
    avg(recommendations.cac) as avg_cac,
    avg(recommendations.ltv_cac_ratio) as avg_ltv_cac_ratio,
    avg(scored.arpu) as avg_arpu,
    avg(case when recommendations.churn_probability >= 0.70 then 1.0 else 0.0 end) as high_churn_risk_pct
from recommendations
inner join scored
    on recommendations.customer_id = scored.customer_id
group by recommendations.channel
