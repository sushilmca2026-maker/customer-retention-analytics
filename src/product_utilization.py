"""
product_utilization.py
-----------------------
Product Utilization Analysis module.

- Churn rate by number of products
- Single-product vs multi-product retention comparison
- Product depth vs churn relationship (Product Depth Index KPI)
- Credit Card Stickiness Score KPI
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def churn_by_product_count(df: pd.DataFrame) -> pd.DataFrame:
    """Churn rate and volume for each distinct NumOfProducts value."""
    return (
        df.groupby("NumOfProducts")
        .agg(
            CustomerCount=("CustomerId", "count"),
            ChurnRate=("Exited", "mean"),
            AvgBalance=("Balance", "mean"),
        )
        .reset_index()
        .sort_values("NumOfProducts")
    )


def single_vs_multi_product(df: pd.DataFrame) -> dict:
    """Compare retention between single-product and multi-product (2+) customers."""
    single = df.loc[df["NumOfProducts"] == 1, "Exited"]
    multi = df.loc[df["NumOfProducts"] >= 2, "Exited"]
    return {
        "single_product_churn_rate": single.mean(),
        "single_product_count": int(single.shape[0]),
        "multi_product_churn_rate": multi.mean(),
        "multi_product_count": int(multi.shape[0]),
        "retention_lift_pct_points": (single.mean() - multi.mean()) * 100,
    }


def product_depth_index(df: pd.DataFrame) -> float:
    """
    Product Depth Index (KPI): correlation-based indicator of whether
    more products used associates with lower churn.
    Returned as -corr(NumOfProducts, Exited) so a HIGHER index = products
    more strongly protective against churn.
    """
    corr = df["NumOfProducts"].corr(df["Exited"])
    return -corr if pd.notnull(corr) else np.nan


def credit_card_stickiness_score(df: pd.DataFrame) -> dict:
    """
    Credit Card Stickiness Score (KPI): churn rate delta between
    card holders and non-holders. Positive value = card ownership
    is associated with better retention.
    """
    with_card = df.loc[df["HasCrCard"] == 1, "Exited"].mean()
    without_card = df.loc[df["HasCrCard"] == 0, "Exited"].mean()
    return {
        "churn_with_card": with_card,
        "churn_without_card": without_card,
        "stickiness_score_pct_points": (without_card - with_card) * 100,
    }
