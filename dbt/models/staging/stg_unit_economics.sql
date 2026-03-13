select
    channel,
    customers_acquired,
    marketing_spend,
    cac,
    avg_arpu,
    ltv_cac_ratio,
    contribution_margin,
    payback_period_months
from {{ source('warehouse', 'unit_economics') }}
