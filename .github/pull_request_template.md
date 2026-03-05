## Summary

- What changed:
- Why it changed:

## Validation Checklist

- [ ] `ruff check .`
- [ ] `black --check .`
- [ ] `pytest -q`
- [ ] `docker build -t revenue-intelligence .`
- [ ] API contracts validated (`/health` and `/score`)
- [ ] Data contract preserved for `dim_*` and `fact_orders.csv`

## Business Impact

- KPI or artifact affected:
- Risk and rollback note:
