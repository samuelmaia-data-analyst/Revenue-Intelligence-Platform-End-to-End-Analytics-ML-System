select
    customer_id,
    signup_date,
    channel,
    segment,
    recency_days,
    frequency,
    monetary,
    avg_order_value,
    tenure_days,
    arpu,
    is_churned,
    next_purchase_30d,
    churn_probability,
    next_purchase_probability,
    as_of_date
from {{ source('warehouse', 'scored_customers') }}
