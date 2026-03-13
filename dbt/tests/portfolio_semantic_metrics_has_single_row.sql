with row_count as (
    select count(*) as total_rows
    from {{ ref('portfolio_semantic_metrics') }}
)
select *
from row_count
where total_rows <> 1
