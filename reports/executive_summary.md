# Executive Summary: Customer Engagement & Product Utilization Analytics for Retention Strategy

**Audience:** Retail banking stakeholders / regulatory & government reporting
**Prepared from:** behavioral analysis of a 10,000-customer European retail banking base
(`data/Churn_Modelling.csv`)

## The Problem

Customers who appear financially healthy — high balance, high income — still leave the bank at meaningful
rates. Demographic-only retention models miss this because they don't measure how customers actually use
the relationship. This project quantifies engagement and product depth as retention drivers, replacing
guesswork with evidence.

## Headline Findings

- **Engagement is the strongest lever.** Inactive customers churn at roughly 1.9x the rate of active
  customers (26.9% vs 14.3%). Reactivation is a higher-leverage investment than acquisition.
- **Balance does not protect against churn.** Nearly half of high-balance customers are inactive, and this
  group churns at close to 2x the rate of active high-balance customers — the "silent churn" the project
  set out to find.
- **A second product meaningfully improves retention** (27.7% churn at 1 product vs 12.8% at 2+) — but
  stacking products beyond that point does not keep helping.
- **Critical red flag: customers with 3+ products churn at ~86%.** This is far too severe to be a normal
  cross-sell ceiling effect and should be investigated as a likely product, service, or onboarding failure
  before any retention campaign is built around it.
- **A single Relationship Strength Index (0-100)**, combining activity, product depth, tenure, and card
  ownership, cleanly separates low-risk from high-risk customers and can plug directly into CRM scoring.

## Recommendations

1. Stand up a **reactivation program** targeting inactive members, prioritized by balance and tenure.
2. Build a **silent-churn watchlist**: high-balance/high-salary customers who are inactive, routed to
   relationship managers for proactive outreach — not to compliance or generic marketing.
3. Redesign cross-sell targeting around **engagement, not just eligibility** — offer a second product to
   engaged single-product customers rather than broadly upselling everyone.
4. **Open a root-cause investigation into the 3+ product segment** before designing any retention offer
   for it — the near-total churn rate suggests a systemic issue, not a targeting gap.
5. Adopt the **Relationship Strength Index** as a standing metric in retention and loyalty program design.

## Deliverables

- Interactive Streamlit dashboard for ongoing self-service analysis (`app/app.py`)
- Full reproducible analytics codebase (`src/`)
- Detailed findings report with supporting charts (`reports/findings.md`)
- This executive summary

*Note: if the underlying dataset is refreshed, re-run `python -m notebooks.eda_report` to regenerate the
figures in this document and in `reports/findings.md`.*
