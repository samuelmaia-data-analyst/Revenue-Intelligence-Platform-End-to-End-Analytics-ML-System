select
    customer_id,
    channel,
    segment,
    ltv,
    cac,
    ltv_cac_ratio,
    churn_probability,
    next_purchase_probability,
    strategic_score,
    recommended_action
from {{ source('warehouse', 'recommendations') }}
