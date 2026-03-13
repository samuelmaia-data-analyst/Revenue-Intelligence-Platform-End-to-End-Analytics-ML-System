select *
from {{ ref('portfolio_semantic_metrics') }}
where high_churn_risk_pct < 0
   or high_churn_risk_pct > 1
