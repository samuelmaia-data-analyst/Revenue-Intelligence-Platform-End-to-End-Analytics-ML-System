select
    customer_id,
    channel,
    segment,
    recommended_action,
    strategic_score,
    ltv,
    cac,
    ltv_cac_ratio,
    churn_probability,
    next_purchase_probability
from {{ ref('stg_recommendations') }}
