"""
kpis.py
-------
Central aggregator for the five headline KPIs defined in the project spec:

  1. Engagement Retention Ratio     - Active vs inactive churn comparison
  2. Product Depth Index            - Products used vs loyalty
  3. High-Balance Disengagement Rate - Premium churn risk
  4. Credit Card Stickiness Score   - Card ownership retention impact
  5. Relationship Strength Index    - Combined engagement & product score (avg)

Run this after the engagement, product_utilization, and financial_engagement
modules have been applied to the dataframe.
"""

from __future__ import annotations

import pandas as pd

from src.engagement import engagement_retention_ratio
from src.product_utilization import product_depth_index, credit_card_stickiness_score
from src.financial_engagement import high_balance_disengagement_rate


def compute_all_kpis(df: pd.DataFrame) -> dict:
    err = engagement_retention_ratio(df)
    hbd = high_balance_disengagement_rate(df)
    ccs = credit_card_stickiness_score(df)
    pdi = product_depth_index(df)

    return {
        "engagement_retention_ratio": err["engagement_retention_ratio"],
        "active_churn_rate": err["active_churn_rate"],
        "inactive_churn_rate": err["inactive_churn_rate"],
        "product_depth_index": pdi,
        "high_balance_disengagement_rate": hbd["disengagement_rate"],
        "high_balance_churn_inactive": hbd["churn_rate_inactive_high_balance"],
        "high_balance_churn_active": hbd["churn_rate_active_high_balance"],
        "credit_card_stickiness_pct_points": ccs["stickiness_score_pct_points"],
        "avg_relationship_strength_index": df["RelationshipStrengthIndex"].mean(),
        "overall_churn_rate": df["Exited"].mean(),
        "total_customers": int(len(df)),
    }


def kpi_summary_frame(kpis: dict) -> pd.DataFrame:
    """Pretty-print-friendly frame for the dashboard / reports."""
    rows = [
        ("Engagement Retention Ratio", f"{kpis['engagement_retention_ratio']:.2f}x",
         "Inactive customers churn this many times more than active customers"),
        ("Product Depth Index", f"{kpis['product_depth_index']:.3f}",
         "Higher = more products more strongly protective against churn"),
        ("High-Balance Disengagement Rate", f"{kpis['high_balance_disengagement_rate']:.1%}",
         "Share of top-quartile-balance customers who are inactive"),
        ("Credit Card Stickiness Score", f"{kpis['credit_card_stickiness_pct_points']:+.1f} pts",
         "Churn-rate reduction (pct points) associated with card ownership"),
        ("Relationship Strength Index (avg)", f"{kpis['avg_relationship_strength_index']:.1f}/100",
         "Composite engagement + product + tenure + card score"),
    ]
    return pd.DataFrame(rows, columns=["KPI", "Value", "Interpretation"])
