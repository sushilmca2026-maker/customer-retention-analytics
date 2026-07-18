"""
generate_sample_data.py
------------------------
Generates a synthetic dataset matching the exact schema in the project spec
(same columns as the classic Kaggle "Churn_Modelling.csv" bank dataset), so
the pipeline and Streamlit app are fully runnable before the real dataset
is dropped into data/Churn_Modelling.csv.

Usage:
    python -m src.generate_sample_data --rows 10000 --out data/Churn_Modelling.csv
"""

from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

SURNAMES = [
    "Hargrave", "Hill", "Onio", "Boni", "Mitchell", "Chu", "Bartlett", "Obinna",
    "He", "H?", "Bearce", "Andrews", "Kay", "Chin", "Fanucci", "Cameron",
    "Yin", "Chukwuemeka", "Yuille", "Nkemakolam", "Yobachukwu", "Ajuluchukwu",
]


def generate(n_rows: int = 10000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    customer_id = np.arange(15600000, 15600000 + n_rows)
    surname = rng.choice(SURNAMES, size=n_rows)
    credit_score = rng.normal(650, 96, n_rows).clip(350, 850).round().astype(int)
    geography = rng.choice(["France", "Germany", "Spain"], size=n_rows, p=[0.5, 0.25, 0.25])
    gender = rng.choice(["Male", "Female"], size=n_rows, p=[0.545, 0.455])
    age = rng.gamma(shape=9, scale=4.2, size=n_rows).clip(18, 92).round().astype(int)
    tenure = rng.integers(0, 11, n_rows)
    has_balance = rng.random(n_rows) > 0.36
    balance = np.where(
        has_balance,
        rng.normal(97000, 62000, n_rows).clip(0, None),
        0.0,
    ).round(2)
    num_products = rng.choice([1, 2, 3, 4], size=n_rows, p=[0.51, 0.46, 0.02, 0.01])
    has_cr_card = rng.choice([0, 1], size=n_rows, p=[0.29, 0.71])
    is_active_member = rng.choice([0, 1], size=n_rows, p=[0.485, 0.515])
    estimated_salary = rng.uniform(11.58, 199992, n_rows).round(2)

    # Build churn probability from behavioral signal, mirroring real-world patterns
    # described in the project background (engagement/product depth drive churn,
    # not balance alone).
    logit = (
        -2.35
        + 1.15 * (is_active_member == 0)
        + 0.55 * (num_products == 1)
        + 0.9 * (num_products >= 3)  # 3-4 products is actually a churn-risk edge case
        + 0.35 * ((age - 40) / 15).clip(0, None)
        + 0.25 * (geography == "Germany")
        - 0.2 * (has_cr_card == 1)
        + 0.4 * ((balance > np.quantile(balance, 0.75)) & (is_active_member == 0))
    )
    churn_prob = 1 / (1 + np.exp(-logit))
    exited = (rng.random(n_rows) < churn_prob).astype(int)

    df = pd.DataFrame({
        "CustomerId": customer_id,
        "Surname": surname,
        "CreditScore": credit_score,
        "Geography": geography,
        "Gender": gender,
        "Age": age,
        "Tenure": tenure,
        "Balance": balance,
        "NumOfProducts": num_products,
        "HasCrCard": has_cr_card,
        "IsActiveMember": is_active_member,
        "EstimatedSalary": estimated_salary,
        "Exited": exited,
    })
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--out", type=str, default="data/Churn_Modelling.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate(args.rows, args.seed)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")
    print(f"Overall churn rate: {df['Exited'].mean():.2%}")
