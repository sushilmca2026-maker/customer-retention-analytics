"""
engagement.py
-------------
Engagement Classification module.

Creates the four engagement profiles called for in the methodology:
- Active engaged customers            (IsActiveMember=1, NumOfProducts>=2)
- Inactive disengaged customers       (IsActiveMember=0, NumOfProducts==1)
- Active but low-product customers    (IsActiveMember=1, NumOfProducts==1)
- Inactive high-balance customers     (IsActiveMember=0, Balance >= high-balance threshold)

Also computes the Relationship Strength Index and Engagement Retention Ratio KPI inputs.
"""

from __future__ import annotations

import pandas as pd
import numpy as np

ENGAGEMENT_PROFILES = [
    "Active Engaged",
    "Active Low-Product",
    "Inactive Disengaged",
    "Inactive High-Balance",
    "Other",
]


def add_engagement_profile(df: pd.DataFrame, high_balance_percentile: float = 0.75) -> pd.DataFrame:
    """
    Adds an 'EngagementProfile' column classifying each customer into one
    of the four (+ fallback 'Other') behavioral segments.
    """
    df = df.copy()
    high_balance_threshold = df["Balance"].quantile(high_balance_percentile)
    df["HighBalanceFlag"] = (df["Balance"] >= high_balance_threshold).astype(int)

    def classify(row):
        active = row["IsActiveMember"] == 1
        multi_product = row["NumOfProducts"] >= 2
        high_balance = row["HighBalanceFlag"] == 1

        if active and multi_product:
            return "Active Engaged"
        if active and not multi_product:
            return "Active Low-Product"
        if not active and high_balance:
            return "Inactive High-Balance"
        if not active and not multi_product:
            return "Inactive Disengaged"
        return "Other"

    df["EngagementProfile"] = df.apply(classify, axis=1)
    return df


def add_relationship_strength_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Relationship Strength Index (RSI): a 0-100 composite of engagement depth.

    Components (each normalized 0-1, then averaged and scaled to 100):
      - Activity:        IsActiveMember
      - Product depth:   NumOfProducts scaled against max observed (capped at 4)
      - Tenure loyalty:  Tenure scaled against max observed
      - Card stickiness: HasCrCard
    """
    df = df.copy()
    product_score = (df["NumOfProducts"].clip(upper=4) - 1) / 3  # 1 product -> 0, 4 -> 1
    tenure_score = df["Tenure"] / df["Tenure"].replace(0, np.nan).max()
    tenure_score = tenure_score.fillna(0)

    df["RelationshipStrengthIndex"] = (
        (df["IsActiveMember"] * 0.35)
        + (product_score * 0.35)
        + (tenure_score * 0.15)
        + (df["HasCrCard"] * 0.15)
    ) * 100
    return df


def engagement_retention_ratio(df: pd.DataFrame) -> dict:
    """
    Engagement Retention Ratio KPI: compares churn rate of active vs inactive members.
    Returns a dict with both rates and the ratio (inactive churn / active churn).
    """
    active_churn = df.loc[df["IsActiveMember"] == 1, "Exited"].mean()
    inactive_churn = df.loc[df["IsActiveMember"] == 0, "Exited"].mean()
    ratio = (inactive_churn / active_churn) if active_churn > 0 else np.nan
    return {
        "active_churn_rate": active_churn,
        "inactive_churn_rate": inactive_churn,
        "engagement_retention_ratio": ratio,
    }


def profile_churn_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Churn rate and headcount by engagement profile."""
    summary = (
        df.groupby("EngagementProfile")
        .agg(
            CustomerCount=("CustomerId", "count"),
            ChurnRate=("Exited", "mean"),
            AvgBalance=("Balance", "mean"),
            AvgRelationshipStrength=("RelationshipStrengthIndex", "mean"),
        )
        .reset_index()
        .sort_values("ChurnRate", ascending=False)
    )
    return summary
