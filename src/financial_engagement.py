"""
financial_engagement.py
------------------------
Financial Commitment vs Engagement Analysis module.

- Balance vs activity cross-analysis
- Salary-balance mismatch detection
- Identification of "at-risk premium customers"
- High-Balance Disengagement Rate KPI
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def balance_activity_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab of average churn rate by (IsActiveMember x Balance quartile)."""
    df = df.copy()
    df["BalanceQuartile"] = pd.qcut(df["Balance"].rank(method="first"), 4, labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"])
    pivot = df.pivot_table(
        index="BalanceQuartile",
        columns="IsActiveMember",
        values="Exited",
        aggfunc="mean",
        observed=False,
    )
    pivot.columns = ["Inactive_ChurnRate", "Active_ChurnRate"]
    return pivot.reset_index()


def salary_balance_mismatch(df: pd.DataFrame, mismatch_ratio_threshold: float = 0.05) -> pd.DataFrame:
    """
    Flags customers whose Balance is very low relative to their EstimatedSalary
    (high earners keeping minimal balance with the bank) - a sign of shallow
    relationship depth despite apparent financial strength.
    """
    df = df.copy()
    df["BalanceToSalaryRatio"] = df["Balance"] / df["EstimatedSalary"].replace(0, np.nan)
    df["SalaryBalanceMismatch"] = (
        (df["EstimatedSalary"] >= df["EstimatedSalary"].median())
        & (df["BalanceToSalaryRatio"] <= mismatch_ratio_threshold)
    )
    return df


def at_risk_premium_customers(
    df: pd.DataFrame,
    balance_percentile: float = 0.75,
    salary_percentile: float = 0.75,
) -> pd.DataFrame:
    """
    Identifies 'at-risk premium customers': high balance AND/OR high salary,
    but inactive - the silent-churn-risk segment called out in the objectives.
    """
    balance_threshold = df["Balance"].quantile(balance_percentile)
    salary_threshold = df["EstimatedSalary"].quantile(salary_percentile)

    mask = (
        (df["IsActiveMember"] == 0)
        & ((df["Balance"] >= balance_threshold) | (df["EstimatedSalary"] >= salary_threshold))
    )
    cols = [
        "CustomerId", "Surname", "Geography", "Age", "Balance",
        "EstimatedSalary", "NumOfProducts", "Tenure", "Exited",
    ]
    return df.loc[mask, cols].sort_values("Balance", ascending=False)


def high_balance_disengagement_rate(df: pd.DataFrame, high_balance_percentile: float = 0.75) -> dict:
    """
    High-Balance Disengagement Rate (KPI): among high-balance customers,
    what fraction are inactive, and what is their churn rate vs the
    high-balance-and-active segment.
    """
    threshold = df["Balance"].quantile(high_balance_percentile)
    high_bal = df.loc[df["Balance"] >= threshold]

    disengagement_rate = (high_bal["IsActiveMember"] == 0).mean()
    churn_inactive_high_bal = high_bal.loc[high_bal["IsActiveMember"] == 0, "Exited"].mean()
    churn_active_high_bal = high_bal.loc[high_bal["IsActiveMember"] == 1, "Exited"].mean()

    return {
        "high_balance_threshold": threshold,
        "high_balance_customer_count": int(high_bal.shape[0]),
        "disengagement_rate": disengagement_rate,
        "churn_rate_inactive_high_balance": churn_inactive_high_bal,
        "churn_rate_active_high_balance": churn_active_high_bal,
    }
