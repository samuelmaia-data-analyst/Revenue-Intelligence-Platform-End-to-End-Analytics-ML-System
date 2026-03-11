# Dataset Source

## Primary Dataset

- Name: Brazilian E-Commerce Public Dataset by Olist
- URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Publisher: Olist (via Kaggle)
- Format: CSV (multiple relational tables)

## Why This Dataset

This dataset is the strongest option for a Senior-level analytics engineering portfolio because it mirrors real-world data platform challenges:

- Multiple source tables with business entities (orders, customers, products, payments)
- Natural joins and dimensional modeling opportunities
- Suitable for Bronze/Silver/Gold layering
- Supports advanced analytics (cohort, retention, forecasting)

## Suggested Mapping to Data Platform Layers

- Raw: original Kaggle CSV files in `data/raw/`
- Bronze: standardized schema, typed columns, ingestion metadata
- Silver: cleaned and conformed tables (deduplication, null handling, key normalization)
- Gold: business marts and KPI tables for BI and ML

## Notes on Usage

- Keep original files unchanged in `data/raw/`.
- Document all transformation assumptions in pipeline code.
- If publishing outputs, include attribution to the dataset source URL above.
