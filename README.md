# Customer Engagement & Product Utilization Analytics for Retention Strategy

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
<!-- Once deployed, replace the link above with your live app URL, e.g.:
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://customer-retention-analytics.streamlit.app) -->

See `DEPLOYMENT.md` for step-by-step Streamlit Cloud deployment instructions.


Behavior- and relationship-depth-driven churn analysis for a retail bank, built to answer one question:
**does customer engagement and product depth predict retention better than demographics or balance alone?**

## Why this project

Banks often see customers who look financially strong (high balance, high salary) but still churn, because
strength on paper doesn't capture engagement, product adoption, or relationship depth. This project reframes
retention analysis around customer *behavior* rather than demographics, and ships the analysis as an
interactive Streamlit dashboard.

## Project Objectives

- Evaluate the relationship between engagement and churn
- Measure retention impact of product count and product mix
- Identify disengaged yet high-value ("silent churn risk") customers
- Support engagement-driven retention strategy, product bundling, and premium-customer retention

## Repository Structure

```
customer-retention-analytics/
├── app/
│   └── app.py                     # Streamlit dashboard (4 core modules, filters, KPIs)
├── src/
│   ├── data_loader.py             # Ingestion & validation
│   ├── engagement.py              # Engagement profiles + Relationship Strength Index
│   ├── product_utilization.py     # Product depth / churn analysis
│   ├── financial_engagement.py    # Balance vs activity, at-risk premium customers
│   ├── retention_strength.py      # Sticky-customer definition, RSI tiers, thresholds
│   ├── kpis.py                    # Central KPI aggregator (5 headline KPIs)
│   └── generate_sample_data.py    # Synthetic data generator (matches real schema)
├── notebooks/
│   └── eda_report.py              # Generates charts + reports/findings.md (research write-up)
├── reports/
│   ├── findings.md                # Auto-generated EDA + insights + recommendations
│   ├── executive_summary.md       # Stakeholder-facing summary
│   └── eda_charts/                # PNG charts referenced by findings.md
├── data/
│   └── Churn_Modelling.csv        # Dataset goes here (see Data section below)
├── .streamlit/
│   └── config.toml                # Dashboard theme
├── requirements.txt
└── README.md
```

## Dataset

Expected columns (standard bank-churn schema):

| Column | Description |
|---|---|
| CustomerId | Unique customer identifier |
| Surname | Customer surname |
| CreditScore | Customer creditworthiness |
| Geography | France, Spain, Germany |
| Gender | Male / Female |
| Age | Customer age |
| Tenure | Years with the bank |
| Balance | Account balance |
| NumOfProducts | Number of bank products |
| HasCrCard | Credit card ownership (0/1) |
| IsActiveMember | Activity indicator (0/1) |
| EstimatedSalary | Estimated annual salary |
| Exited | Churn indicator, target (0/1) |

The real dataset (10,000 rows, European retail bank customers, ~20% churn rate) is bundled at
`data/Churn_Modelling.csv`. To regenerate a synthetic dataset with the same schema instead:

```bash
python -m src.generate_sample_data --rows 10000 --out data/Churn_Modelling.csv
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt         # dashboard only (lean, fast Streamlit Cloud builds)
pip install -r requirements-dev.txt     # adds matplotlib/seaborn/scipy for notebooks/eda_report.py
```

## Running the Dashboard

```bash
streamlit run app/app.py
```

Dashboard modules:
1. **Engagement vs Churn Overview** — churn by engagement profile, segment sizes, retention ratio
2. **Product Utilization Impact Analysis** — churn by product count, single vs multi-product, card stickiness
3. **High-Value Disengaged Customer Detector** — at-risk premium customer list with adjustable thresholds
4. **Retention Strength Scoring** — Relationship Strength Index distribution, tiering, threshold scan

Sidebar filters: geography, engagement profile, product count, balance range, salary range. You can also
upload your own CSV directly from the sidebar instead of using the bundled file.

## Regenerating the Research Report

```bash
python -m notebooks.eda_report
```

Writes chart PNGs to `reports/eda_charts/` and a findings write-up to `reports/findings.md`.

## Methodology

Following the analytical methodology in the project brief:

1. **Data Ingestion & Validation** — schema check, binary-field consistency, churn-label sanity (`src/data_loader.py`)
2. **Engagement Classification** — Active Engaged / Active Low-Product / Inactive Disengaged / Inactive High-Balance (`src/engagement.py`)
3. **Product Utilization Analysis** — churn by product count, single vs multi-product retention (`src/product_utilization.py`)
4. **Financial Commitment vs Engagement Analysis** — balance/activity cross-analysis, salary-balance mismatch, at-risk premium detection (`src/financial_engagement.py`)
5. **Retention Strength Assessment** — sticky-customer definition, RSI tiers, engagement thresholds (`src/retention_strength.py`)

## KPIs

| KPI | What it measures |
|---|---|
| Engagement Retention Ratio | Active vs inactive churn comparison |
| Product Depth Index | Products used vs loyalty |
| High-Balance Disengagement Rate | Premium churn risk |
| Credit Card Stickiness Score | Card ownership retention impact |
| Relationship Strength Index | Combined engagement & product score |

## Tech Stack

Python, pandas, NumPy, Streamlit, Plotly, Matplotlib/Seaborn.

## License

MIT (see `LICENSE`).
