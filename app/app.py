"""
app.py
------
Streamlit dashboard for the Customer Engagement & Product Utilization
Analytics for Retention Strategy project.

Run from the project root with:
    streamlit run app/app.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_dataset, validate_dataset, clean_dataset
from src.engagement import (
    add_engagement_profile,
    add_relationship_strength_index,
    engagement_retention_ratio,
    profile_churn_summary,
)
from src.product_utilization import (
    churn_by_product_count,
    single_vs_multi_product,
    product_depth_index,
    credit_card_stickiness_score,
)
from src.financial_engagement import (
    balance_activity_crosstab,
    salary_balance_mismatch,
    at_risk_premium_customers,
    high_balance_disengagement_rate,
)
from src.retention_strength import (
    define_sticky_customers,
    churn_by_rsi_tier,
    find_retention_threshold,
)
from src.kpis import compute_all_kpis, kpi_summary_frame

# ---------------------------------------------------------------------------
# Page config & palette
# ---------------------------------------------------------------------------
NAVY = "#0B2545"
SLATE = "#134074"
GOLD = "#C9A227"
TEAL = "#0F766E"
RED = "#B33A3A"
BG = "#F7F9FB"

PALETTE = [SLATE, GOLD, TEAL, RED, "#5C7A99", "#8A6D00"]

st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="\U0001F3E6",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    div[data-testid="stMetricValue"] {{ color: {NAVY}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def get_data(path: str):
    df = load_dataset(path)
    report = validate_dataset(df)
    df = clean_dataset(df)
    df = add_engagement_profile(df)
    df = add_relationship_strength_index(df)
    df = define_sticky_customers(df)
    return df, report


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "Churn_Modelling.csv")

st.sidebar.title("Data Source")
uploaded = st.sidebar.file_uploader("Upload customer CSV (optional)", type=["csv"])

if uploaded is not None:
    df_raw = pd.read_csv(uploaded)
    report = validate_dataset(df_raw)
    df = clean_dataset(df_raw)
    df = add_engagement_profile(df)
    df = add_relationship_strength_index(df)
    df = define_sticky_customers(df)
else:
    if not os.path.exists(DEFAULT_PATH):
        st.error(
            "No dataset found at data/Churn_Modelling.csv and none uploaded. "
            "Run `python -m src.generate_sample_data` to create a sample, "
            "or upload a CSV in the sidebar."
        )
        st.stop()
    df, report = get_data(DEFAULT_PATH)

if not report.passed:
    st.sidebar.error("Data validation found issues:\n" + "\n".join(report.issues))
else:
    st.sidebar.success(f"Validated {report.row_count:,} rows")
if report.warnings:
    with st.sidebar.expander("Validation warnings"):
        for w in report.warnings:
            st.write(f"- {w}")

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

geo_options = sorted(df["Geography"].unique().tolist())
geo_filter = st.sidebar.multiselect("Geography", geo_options, default=geo_options)

engagement_filter = st.sidebar.multiselect(
    "Engagement profile",
    sorted(df["EngagementProfile"].unique().tolist()),
    default=sorted(df["EngagementProfile"].unique().tolist()),
)

product_range = st.sidebar.slider(
    "Number of products",
    int(df["NumOfProducts"].min()),
    int(df["NumOfProducts"].max()),
    (int(df["NumOfProducts"].min()), int(df["NumOfProducts"].max())),
)

balance_range = st.sidebar.slider(
    "Balance range",
    float(df["Balance"].min()),
    float(df["Balance"].max()),
    (float(df["Balance"].min()), float(df["Balance"].max())),
)

salary_range = st.sidebar.slider(
    "Estimated salary range",
    float(df["EstimatedSalary"].min()),
    float(df["EstimatedSalary"].max()),
    (float(df["EstimatedSalary"].min()), float(df["EstimatedSalary"].max())),
)

mask = (
    df["Geography"].isin(geo_filter)
    & df["EngagementProfile"].isin(engagement_filter)
    & df["NumOfProducts"].between(*product_range)
    & df["Balance"].between(*balance_range)
    & df["EstimatedSalary"].between(*salary_range)
)
fdf = df.loc[mask].copy()

st.sidebar.markdown(f"**{len(fdf):,}** customers match filters (of {len(df):,} total)")

if len(fdf) == 0:
    st.warning("No customers match the current filters. Adjust the filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard \u2014 behavior and relationship depth, not just demographics")

kpis = compute_all_kpis(fdf)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Overall churn rate", f"{kpis['overall_churn_rate']:.1%}")
k2.metric("Engagement retention ratio", f"{kpis['engagement_retention_ratio']:.2f}x",
          help="Inactive customer churn rate / active customer churn rate")
k3.metric("Product depth index", f"{kpis['product_depth_index']:.3f}",
          help="Higher = more products more protective against churn")
k4.metric("High-balance disengagement", f"{kpis['high_balance_disengagement_rate']:.1%}",
          help="Share of top-quartile-balance customers who are inactive")
k5.metric("Avg relationship strength", f"{kpis['avg_relationship_strength_index']:.1f}/100")

st.divider()

# ---------------------------------------------------------------------------
# Tabs = Core Modules
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Engagement vs Churn",
    "Product Utilization",
    "High-Value Disengaged Detector",
    "Retention Strength Scoring",
])

# --- Tab 1: Engagement vs churn overview -----------------------------------
with tab1:
    st.subheader("Engagement vs Churn Overview")

    col1, col2 = st.columns([1.3, 1])
    with col1:
        summary = profile_churn_summary(fdf)
        fig = px.bar(
            summary, x="EngagementProfile", y="ChurnRate", color="EngagementProfile",
            color_discrete_sequence=PALETTE,
            text=summary["ChurnRate"].map(lambda x: f"{x:.1%}"),
            labels={"ChurnRate": "Churn Rate", "EngagementProfile": "Engagement Profile"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis_tickformat=".0%", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Segment sizes**")
        fig2 = px.pie(
            summary, names="EngagementProfile", values="CustomerCount",
            color_discrete_sequence=PALETTE, hole=0.45,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        summary.style.format({"ChurnRate": "{:.1%}", "AvgBalance": "${:,.0f}", "AvgRelationshipStrength": "{:.1f}"}),
        use_container_width=True,
    )

    err = engagement_retention_ratio(fdf)
    st.info(
        f"Active members churn at **{err['active_churn_rate']:.1%}** vs. "
        f"**{err['inactive_churn_rate']:.1%}** for inactive members \u2014 an "
        f"**{err['engagement_retention_ratio']:.2f}x** retention ratio favoring engaged customers."
    )

# --- Tab 2: Product utilization impact analysis ----------------------------
with tab2:
    st.subheader("Product Utilization Impact Analysis")

    col1, col2 = st.columns(2)
    with col1:
        by_product = churn_by_product_count(fdf)
        fig = px.bar(
            by_product, x="NumOfProducts", y="ChurnRate",
            color_discrete_sequence=[SLATE],
            text=by_product["ChurnRate"].map(lambda x: f"{x:.1%}"),
            labels={"ChurnRate": "Churn Rate", "NumOfProducts": "Number of Products"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis_tickformat=".0%", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        svm = single_vs_multi_product(fdf)
        fig2 = go.Figure(data=[
            go.Bar(
                x=["Single product", "Multi-product (2+)"],
                y=[svm["single_product_churn_rate"], svm["multi_product_churn_rate"]],
                marker_color=[RED, TEAL],
                text=[f"{svm['single_product_churn_rate']:.1%}", f"{svm['multi_product_churn_rate']:.1%}"],
                textposition="outside",
            )
        ])
        fig2.update_layout(yaxis_tickformat=".0%", plot_bgcolor="white", title="Single vs Multi-Product Retention")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(
            f"Retention lift of {svm['retention_lift_pct_points']:.1f} percentage points "
            f"moving customers from 1 product to 2+."
        )

    ccs = credit_card_stickiness_score(fdf)
    st.info(
        f"**Credit Card Stickiness:** card holders churn at {ccs['churn_with_card']:.1%} "
        f"vs {ccs['churn_without_card']:.1%} for non-holders "
        f"({ccs['stickiness_score_pct_points']:+.1f} pct-point difference)."
    )

# --- Tab 3: High-value disengaged customer detector ------------------------
with tab3:
    st.subheader("High-Value Disengaged Customer Detector")
    st.caption("At-risk premium customers: high balance and/or salary, but inactive \u2014 the silent churn risk segment.")

    col1, col2 = st.columns(2)
    with col1:
        bal_pctile = st.slider("Balance percentile threshold", 0.5, 0.95, 0.75, 0.05, key="bal_pct")
    with col2:
        sal_pctile = st.slider("Salary percentile threshold", 0.5, 0.95, 0.75, 0.05, key="sal_pct")

    at_risk = at_risk_premium_customers(fdf, bal_pctile, sal_pctile)
    hbd = high_balance_disengagement_rate(fdf, bal_pctile)

    m1, m2, m3 = st.columns(3)
    m1.metric("At-risk premium customers", f"{len(at_risk):,}")
    m2.metric("Disengagement rate (high balance)", f"{hbd['disengagement_rate']:.1%}")
    m3.metric("Churn rate (inactive + high balance)", f"{hbd['churn_rate_inactive_high_balance']:.1%}")

    st.dataframe(
        at_risk.style.format({"Balance": "${:,.0f}", "EstimatedSalary": "${:,.0f}"}),
        use_container_width=True,
        height=350,
    )

    st.markdown("**Balance vs Activity Cross-Analysis**")
    crosstab = balance_activity_crosstab(fdf)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Inactive", x=crosstab["BalanceQuartile"].astype(str),
                          y=crosstab["Inactive_ChurnRate"], marker_color=RED))
    fig.add_trace(go.Bar(name="Active", x=crosstab["BalanceQuartile"].astype(str),
                          y=crosstab["Active_ChurnRate"], marker_color=TEAL))
    fig.update_layout(barmode="group", yaxis_tickformat=".0%", plot_bgcolor="white",
                       xaxis_title="Balance Quartile", yaxis_title="Churn Rate")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Salary-balance mismatch detail"):
        mismatch_df = salary_balance_mismatch(fdf)
        mismatch_count = mismatch_df["SalaryBalanceMismatch"].sum()
        st.write(f"{mismatch_count:,} customers earn above the median salary but keep minimal balance with the bank.")
        st.dataframe(
            mismatch_df.loc[mismatch_df["SalaryBalanceMismatch"],
                            ["CustomerId", "Surname", "EstimatedSalary", "Balance", "BalanceToSalaryRatio", "Exited"]]
            .sort_values("EstimatedSalary", ascending=False)
            .style.format({"EstimatedSalary": "${:,.0f}", "Balance": "${:,.0f}", "BalanceToSalaryRatio": "{:.3f}"}),
            use_container_width=True,
        )

# --- Tab 4: Retention strength scoring panels -------------------------------
with tab4:
    st.subheader("Retention Strength Scoring")

    rsi_threshold = st.slider("Sticky-customer RSI threshold", 0, 100, 70, 5)
    sticky_count = (fdf["RelationshipStrengthIndex"] >= rsi_threshold).sum()
    st.metric("Sticky customers (RSI \u2265 threshold)", f"{sticky_count:,} of {len(fdf):,}")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            fdf, x="RelationshipStrengthIndex", color="Exited",
            color_discrete_map={0: TEAL, 1: RED},
            nbins=30, barmode="overlay", opacity=0.7,
            labels={"RelationshipStrengthIndex": "Relationship Strength Index", "Exited": "Churned"},
        )
        fig.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tier_summary = churn_by_rsi_tier(fdf)
        fig2 = px.bar(
            tier_summary, x=tier_summary["RSITier"].astype(str), y="ChurnRate",
            color_discrete_sequence=[GOLD],
            text=tier_summary["ChurnRate"].map(lambda x: f"{x:.1%}" if pd.notnull(x) else ""),
            labels={"x": "RSI Tier", "ChurnRate": "Churn Rate"},
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(yaxis_tickformat=".0%", plot_bgcolor="white", xaxis_title="RSI Tier")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Engagement Threshold Scan**")
    st.caption("Churn rate above vs. below each RSI threshold \u2014 look for where churn drops off sharply.")
    threshold_df = find_retention_threshold(fdf)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=threshold_df["Threshold"], y=threshold_df["ChurnRate_AtOrAbove"],
                               name="Churn (at/above threshold)", line=dict(color=TEAL, width=3)))
    fig3.add_trace(go.Scatter(x=threshold_df["Threshold"], y=threshold_df["ChurnRate_Below"],
                               name="Churn (below threshold)", line=dict(color=RED, width=3)))
    fig3.update_layout(yaxis_tickformat=".0%", plot_bgcolor="white",
                        xaxis_title="RSI Threshold", yaxis_title="Churn Rate")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.caption(
    "Customer Engagement & Product Utilization Analytics for Retention Strategy \u2014 "
    "portfolio project. Data is illustrative/synthetic unless a real dataset has been supplied."
)
