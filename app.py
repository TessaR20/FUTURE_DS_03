"""
Marketing Funnel & Conversion Performance Dashboard
------------------------------------------------------
Interactive analytics dashboard for a simulated B2B marketing funnel.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Expects `marketing_funnel.csv` in the same folder. If missing, you'll be
prompted to upload a CSV with the same column structure.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Marketing Funnel Dashboard", page_icon="🎯", layout="wide")

NAVY = "#1F3864"; BLUE = "#2E5EAA"; TEAL = "#1B998B"; ORANGE = "#F0913B"; RED = "#C94277"; PURPLE = "#6C63A5"
PALETTE = [BLUE, TEAL, ORANGE, RED, PURPLE, "#8A8A8A"]
STAGES = ["Visitors", "Leads", "MQLs", "SQLs", "Customers"]

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] { background-color: #F5F7FA; border: 1px solid #E3E8EF; border-radius: 10px; padding: 14px 16px 10px 16px; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem; color: #595959; }
    [data-testid="stMetricValue"] { font-size: 1.45rem; color: #1F3864; }
    h1, h2, h3 { color: #1F3864; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(path_or_buffer):
    df = pd.read_csv(path_or_buffer, parse_dates=["Date"])
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Week"] = df["Date"].dt.to_period("W").dt.start_time
    return df


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "marketing_funnel.csv")

if os.path.exists(DEFAULT_PATH):
    df_raw = load_data(DEFAULT_PATH)
else:
    st.title("🎯 Marketing Funnel & Conversion Dashboard")
    st.info("No `marketing_funnel.csv` found next to this script. Upload a CSV with the expected columns to continue.")
    uploaded = st.file_uploader("Upload funnel data (CSV)", type=["csv"])
    if uploaded is None:
        st.stop()
    df_raw = load_data(uploaded)

# ---------------- Sidebar filters ----------------
st.sidebar.title("🎯 Funnel Dashboard")
st.sidebar.caption("Filter the data below — all views update live.")

min_date, max_date = df_raw["Date"].min().date(), df_raw["Date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

channels = st.sidebar.multiselect("Channel", sorted(df_raw["Channel"].unique()), default=sorted(df_raw["Channel"].unique()))
avail_campaigns = sorted(df_raw.loc[df_raw["Channel"].isin(channels), "Campaign"].unique())
campaigns = st.sidebar.multiselect("Campaign", avail_campaigns, default=avail_campaigns)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit + Plotly · Simulated data")

mask = (
    (df_raw["Date"].dt.date >= start_date)
    & (df_raw["Date"].dt.date <= end_date)
    & (df_raw["Channel"].isin(channels))
    & (df_raw["Campaign"].isin(campaigns))
)
df = df_raw.loc[mask].copy()

if df.empty:
    st.warning("No data matches the current filters. Adjust the sidebar.")
    st.stop()

# ---------------- Header + KPIs ----------------
st.title("🎯 Marketing Funnel & Conversion Performance")
st.caption(f"Showing data from {start_date} to {end_date} across {df['Channel'].nunique()} channel(s)")

tot = df[STAGES + ["Spend (USD)", "Revenue (USD)"]].sum()
v2c = tot["Customers"] / tot["Visitors"] if tot["Visitors"] else 0
cac = tot["Spend (USD)"] / tot["Customers"] if tot["Customers"] else np.nan
roi = (tot["Revenue (USD)"] - tot["Spend (USD)"]) / tot["Spend (USD)"] if tot["Spend (USD)"] else np.nan

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Visitors", f"{tot['Visitors']:,.0f}")
k2.metric("Leads", f"{tot['Leads']:,.0f}")
k3.metric("Customers", f"{tot['Customers']:,.0f}")
k4.metric("Conversion", f"{v2c:.2%}")
k5.metric("CAC", f"${cac:,.0f}" if pd.notna(cac) else "n/a")
k6.metric("ROI", f"{roi:.0%}" if pd.notna(roi) else "n/a")

st.markdown("---")

tab_funnel, tab_trend, tab_channel, tab_campaign, tab_data = st.tabs(
    ["🔻 Funnel", "📈 Trend", "📊 Channel Performance", "🏆 Campaigns", "🔎 Raw Data"]
)

# ---- Funnel tab ----
with tab_funnel:
    funnel_vals = [tot[s] for s in STAGES]
    fig = go.Figure(go.Funnel(
        y=STAGES, x=funnel_vals, textinfo="value+percent initial+percent previous",
        marker=dict(color=PALETTE[:len(STAGES)]),
    ))
    fig.update_layout(title="Overall Funnel", height=480, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    stage_pairs = [("Visitors", "Leads"), ("Leads", "MQLs"), ("MQLs", "SQLs"), ("SQLs", "Customers")]
    conv = [tot[b] / tot[a] * 100 if tot[a] else 0 for a, b in stage_pairs]
    labels = ["Visitor→Lead", "Lead→MQL", "MQL→SQL", "SQL→Customer"]
    fig2 = px.bar(x=labels, y=conv, color=labels, color_discrete_sequence=PALETTE, text=[f"{v:.1f}%" for v in conv])
    fig2.update_traces(textposition="outside")
    fig2.update_layout(title="Stage-to-Stage Conversion Rate", showlegend=False, yaxis_title="Conversion Rate (%)",
                         margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ---- Trend tab ----
with tab_trend:
    gran = st.radio("Granularity", ["Monthly", "Weekly", "Daily"], horizontal=True)
    freq_col = {"Monthly": "Month", "Weekly": "Week", "Daily": "Date"}[gran]
    trend = df.groupby(freq_col)[STAGES].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend[freq_col], y=trend["Visitors"], name="Visitors", line=dict(color=BLUE)))
    fig.add_trace(go.Scatter(x=trend[freq_col], y=trend["Leads"], name="Leads", line=dict(color=TEAL)))
    fig.add_trace(go.Scatter(x=trend[freq_col], y=trend["Customers"], name="Customers", line=dict(color=RED), yaxis="y2"))
    fig.update_layout(
        title=f"{gran} Trend: Visitors, Leads & Customers",
        yaxis=dict(title="Visitors / Leads"),
        yaxis2=dict(title="Customers", overlaying="y", side="right"),
        margin=dict(t=50, l=10, r=10, b=10), hovermode="x unified", legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

    spend_rev = df.groupby(freq_col)[["Spend (USD)", "Revenue (USD)"]].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_bar(x=spend_rev[freq_col], y=spend_rev["Spend (USD)"], name="Spend", marker_color=ORANGE)
    fig2.add_bar(x=spend_rev[freq_col], y=spend_rev["Revenue (USD)"], name="Revenue", marker_color=TEAL)
    fig2.update_layout(title=f"{gran} Spend vs Revenue", barmode="group", margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ---- Channel Performance tab ----
with tab_channel:
    chan = df.groupby("Channel").agg(
        Visitors=("Visitors", "sum"), Leads=("Leads", "sum"), Customers=("Customers", "sum"),
        Spend=("Spend (USD)", "sum"), Revenue=("Revenue (USD)", "sum"),
    ).reset_index()
    chan["V2C"] = chan["Customers"] / chan["Visitors"] * 100
    chan["CAC"] = chan["Spend"] / chan["Customers"].replace(0, np.nan)
    chan["ROI"] = (chan["Revenue"] - chan["Spend"]) / chan["Spend"].replace(0, np.nan) * 100

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(chan.sort_values("Customers", ascending=False), x="Channel", y="Customers",
                      color="Channel", color_discrete_sequence=PALETTE, text="Customers")
        fig.update_traces(textposition="outside")
        fig.update_layout(title="Customers by Channel", showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(chan, x="CAC", y="ROI", size="Customers", color="Channel", color_discrete_sequence=PALETTE,
                           hover_name="Channel", size_max=45)
        fig.update_layout(title="CAC vs ROI (bubble size = customers)", margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        chan.assign(V2C=chan["V2C"].round(2), CAC=chan["CAC"].round(0), ROI=chan["ROI"].round(0))
            .rename(columns={"V2C": "V2C (%)", "CAC": "CAC ($)", "ROI": "ROI (%)"}),
        use_container_width=True, hide_index=True,
    )

    st.markdown("**Stage conversion rate by channel**")
    chan_stage = df.groupby("Channel")[STAGES].sum()
    chan_conv = pd.DataFrame(index=chan_stage.index)
    chan_conv["Visitor→Lead"] = chan_stage["Leads"] / chan_stage["Visitors"] * 100
    chan_conv["Lead→MQL"] = chan_stage["MQLs"] / chan_stage["Leads"] * 100
    chan_conv["MQL→SQL"] = chan_stage["SQLs"] / chan_stage["MQLs"] * 100
    chan_conv["SQL→Customer"] = chan_stage["Customers"] / chan_stage["SQLs"] * 100
    fig = px.imshow(chan_conv, text_auto=".1f", color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ---- Campaigns tab ----
with tab_campaign:
    top_n = st.slider("Number of campaigns to show", 5, 20, 10)
    camp = df.groupby(["Channel", "Campaign"]).agg(
        Visitors=("Visitors", "sum"), Leads=("Leads", "sum"), Customers=("Customers", "sum"),
        Spend=("Spend (USD)", "sum"), Revenue=("Revenue (USD)", "sum"),
    ).reset_index()
    camp["Label"] = camp["Channel"] + " – " + camp["Campaign"]
    camp["V2C"] = camp["Customers"] / camp["Visitors"] * 100
    camp["CAC"] = camp["Spend"] / camp["Customers"].replace(0, np.nan)
    camp_top = camp.sort_values("Customers", ascending=False).head(top_n)

    fig = px.bar(camp_top.sort_values("Customers"), x="Customers", y="Label", orientation="h",
                  color="Channel", color_discrete_sequence=PALETTE, text="Customers")
    fig.update_traces(textposition="outside")
    fig.update_layout(title=f"Top {top_n} Campaigns by Customers", margin=dict(t=50, l=10, r=10, b=10),
                        height=max(400, top_n * 32))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        camp.sort_values("Customers", ascending=False)
            .assign(V2C=lambda d: d["V2C"].round(2), CAC=lambda d: d["CAC"].round(0))
            .rename(columns={"V2C": "V2C (%)", "CAC": "CAC ($)"})
            [["Channel", "Campaign", "Visitors", "Leads", "Customers", "Spend", "Revenue", "V2C (%)", "CAC ($)"]],
        use_container_width=True, hide_index=True,
    )

# ---- Raw Data tab ----
with tab_data:
    st.markdown(f"**{len(df):,} rows** match the current filters.")
    st.dataframe(df.drop(columns=["Month", "Week"], errors="ignore"), use_container_width=True, height=450)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", csv, "filtered_marketing_funnel.csv", "text/csv")
