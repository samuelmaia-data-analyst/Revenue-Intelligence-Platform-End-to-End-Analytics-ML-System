from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationPolicy:
    name: str
    uplift_rate: float
    cost_rate: float
    base_metric: str


GROSS_MARGIN = 0.68
DEFAULT_RETENTION_PROBABILITY = 0.20
CHURN_OVERRIDE_PROBABILITY = 0.80
HIGH_CHURN_THRESHOLD = 0.70
LOW_CHURN_THRESHOLD = 0.40
NEXT_PURCHASE_OPPORTUNITY_THRESHOLD = 0.60
LOW_VALUE_QUANTILE = 0.30
HIGH_VALUE_QUANTILE = 0.70

RECOMMENDATION_POLICIES = {
    "Retention Campaign": RecommendationPolicy(
        name="Retention Campaign",
        uplift_rate=0.35,
        cost_rate=0.08,
        base_metric="ltv",
    ),
    "Upsell Offer": RecommendationPolicy(
        name="Upsell Offer",
        uplift_rate=0.15,
        cost_rate=0.05,
        base_metric="ltv",
    ),
    "Reduce Acquisition Spend": RecommendationPolicy(
        name="Reduce Acquisition Spend",
        uplift_rate=0.50,
        cost_rate=0.01,
        base_metric="cac",
    ),
    "Nurture": RecommendationPolicy(
        name="Nurture",
        uplift_rate=0.03,
        cost_rate=0.02,
        base_metric="ltv",
    ),
}
