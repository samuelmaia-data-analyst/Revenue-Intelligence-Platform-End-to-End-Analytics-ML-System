select *
from {{ ref('channel_semantic_metrics') }}
where avg_ltv < 0
   or avg_cac < 0
   or avg_ltv_cac_ratio < 0
   or avg_arpu < 0
