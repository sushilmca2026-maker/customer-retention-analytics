"""
retention_strength.py
----------------------
Retention Strength Assessment module.

- Defines "sticky customer" profiles
- Measures churn stability across engagement tiers
- Identifies engagement thresholds linked to retention
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def define_sticky_customers(df: pd.DataFrame, rsi_threshold: float = 70.0) -> pd.DataFrame:
    """
    'Sticky' customers: those with RelationshipStrengthIndex at/above the
    given threshold (default 70/100). Requires RelationshipStrengthIndex
    column (see engagement.add_relationship_strength_index).
    """
    df = df.copy()
    df["IsStickyCustomer"] = df["RelationshipStrengthIndex"] >= rsi_threshold
    return df


def churn_by_rsi_tier(df: pd.DataFrame, bins: list | None = None) -> pd.DataFrame:
    """
    Buckets customers into RelationshipStrengthIndex tiers and reports
    churn rate + stability (std dev of churn across tenure within tier)
    for each tier, to find where retention becomes stable ("sticky").
    """
    if bins is None:
        bins = [0, 25, 50, 70, 85, 100]
    df = df.copy()
    df["RSITier"] = pd.cut(df["RelationshipStrengthIndex"], bins=bins, include_lowest=True)

    tier_summary = (
        df.groupby("RSITier", observed=False)
        .agg(
            CustomerCount=("CustomerId", "count"),
            ChurnRate=("Exited", "mean"),
            ChurnRateStdByTenure=("Exited", lambda s: df.loc[s.index].groupby("Tenure")["Exited"].mean().std()),
        )
        .reset_index()
    )
    return tier_summary


def find_retention_threshold(df: pd.DataFrame, step: float = 5.0) -> pd.DataFrame:
    """
    Scans RelationshipStrengthIndex thresholds and reports churn rate
    above/below each threshold, to help identify the inflection point
    where churn drops off meaningfully (the "engagement threshold").
    """
    thresholds = np.arange(0, 100 + step, step)
    rows = []
    for t in thresholds:
        above = df.loc[df["RelationshipStrengthIndex"] >= t, "Exited"]
        below = df.loc[df["RelationshipStrengthIndex"] < t, "Exited"]
        rows.append({
            "Threshold": t,
            "ChurnRate_AtOrAbove": above.mean() if len(above) else np.nan,
            "CountAtOrAbove": len(above),
            "ChurnRate_Below": below.mean() if len(below) else np.nan,
            "CountBelow": len(below),
        })
    return pd.DataFrame(rows)
