"""
data_loader.py
--------------
Data Ingestion & Validation module.

Responsibilities (per project methodology):
- Load the raw customer dataset
- Validate engagement and product fields
- Ensure binary variables (HasCrCard, IsActiveMember, Exited) are consistent (0/1)
- Confirm churn labeling accuracy
- Surface a validation report the rest of the pipeline / dashboard can display
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List

REQUIRED_COLUMNS = [
    "CustomerId",
    "Surname",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
]

BINARY_COLUMNS = ["HasCrCard", "IsActiveMember", "Exited"]
NUMERIC_COLUMNS = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "EstimatedSalary",
]
VALID_GEOGRAPHIES = {"France", "Spain", "Germany"}
VALID_GENDERS = {"Male", "Female"}


@dataclass
class ValidationReport:
    passed: bool = True
    row_count: int = 0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_issue(self, msg: str):
        self.issues.append(msg)
        self.passed = False

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def summary(self) -> str:
        lines = [f"Rows validated: {self.row_count}", f"Status: {'PASSED' if self.passed else 'FAILED'}"]
        if self.issues:
            lines.append("Issues:")
            lines += [f"  - {i}" for i in self.issues]
        if self.warnings:
            lines.append("Warnings:")
            lines += [f"  - {w}" for w in self.warnings]
        return "\n".join(lines)


def load_dataset(path: str) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    df = pd.read_csv(path)
    return df


def validate_dataset(df: pd.DataFrame) -> ValidationReport:
    """
    Run structural and business-rule validation on the dataset.
    Does not mutate df; returns a report describing what was found.
    """
    report = ValidationReport(row_count=len(df))

    # 1. Required columns present
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        report.add_issue(f"Missing required columns: {missing_cols}")
        return report  # can't validate further meaningfully

    # 2. Null checks
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    for col, cnt in null_counts.items():
        if cnt > 0:
            report.add_warning(f"Column '{col}' has {cnt} null value(s)")

    # 3. Duplicate CustomerId
    dup_count = df["CustomerId"].duplicated().sum()
    if dup_count > 0:
        report.add_issue(f"{dup_count} duplicate CustomerId value(s) found")

    # 4. Binary field consistency
    for col in BINARY_COLUMNS:
        bad_vals = df.loc[~df[col].isin([0, 1]), col].unique()
        if len(bad_vals) > 0:
            report.add_issue(f"Column '{col}' contains non-binary values: {list(bad_vals)}")

    # 5. Categorical domain checks
    bad_geo = set(df["Geography"].unique()) - VALID_GEOGRAPHIES
    if bad_geo:
        report.add_warning(f"Unexpected Geography values found: {bad_geo}")

    bad_gender = set(df["Gender"].unique()) - VALID_GENDERS
    if bad_gender:
        report.add_warning(f"Unexpected Gender values found: {bad_gender}")

    # 6. Range checks
    if (df["Age"] < 18).any() or (df["Age"] > 100).any():
        report.add_warning("Age values outside plausible 18-100 range detected")

    if (df["NumOfProducts"] < 1).any() or (df["NumOfProducts"] > 4).any():
        report.add_warning("NumOfProducts outside expected 1-4 range detected")

    if (df["Balance"] < 0).any():
        report.add_issue("Negative Balance values found")

    if (df["CreditScore"] < 300).any() or (df["CreditScore"] > 900).any():
        report.add_warning("CreditScore outside plausible 300-900 range detected")

    # 7. Churn label sanity: Exited must be binary (already checked) and not all-one-class
    churn_rate = df["Exited"].mean()
    if churn_rate == 0 or churn_rate == 1:
        report.add_issue("Exited column has no variation (single-class target) - check labeling")
    else:
        report.add_warning(f"Overall churn rate: {churn_rate:.2%}")

    return report


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply light, non-destructive cleaning:
    - Drop exact duplicate rows
    - Cast binary/categorical dtypes
    - Strip whitespace from string columns
    """
    df = df.drop_duplicates().copy()

    for col in BINARY_COLUMNS:
        df[col] = df[col].astype(int)

    for col in ["Geography", "Gender", "Surname"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/Churn_Modelling.csv"
    df = load_dataset(path)
    report = validate_dataset(df)
    print(report.summary())
