# Marketing Funnel & Conversion Performance Analysis

Client-ready funnel analysis built as part of a data analytics internship task. Simulates a
full year (2025) of daily channel/campaign-level marketing performance for a B2B-style
funnel — Visitors → Leads → MQLs → SQLs → Customers — across 6 channels and 12 campaigns,
then delivers a formal report and an interactive dashboard.

> **Note on the data:** This uses a transparent simulated dataset built with realistic
> funnel dynamics (channel-specific conversion rates, seasonality, gradual optimization
> improvement, cost/revenue modeling) rather than a real company's data, so the workflow
> can be shown end-to-end without any privacy or licensing concerns.

## 📁 Contents

| File | Description |
|---|---|
| `marketing_funnel.csv` | Simulated dataset — daily rows by Channel/Campaign with Visitors, Leads, MQLs, SQLs, Customers, Spend, and Revenue |
| `Marketing_Funnel_Analysis_Report.docx` | Full client-ready report: KPIs, overall funnel, monthly trend, channel efficiency (CAC/ROI), stage-by-stage drop-off heatmap, top campaigns, and 6 recommendations |
| `charts/` | All charts used in the report, exported as standalone PNGs |
| `dashboard/app.py` | Interactive Python (Streamlit + Plotly) dashboard — filter by date, channel, campaign; funnel visualization, trend charts, channel/campaign efficiency views, raw data export |
| `dashboard/requirements.txt` | Python dependencies for the dashboard |

## 📊 Key Findings

- **Overall funnel:** ~949K visitors → 67.6K leads → 34.4K MQLs → 21.7K SQLs → 8,051 customers (0.85% visitor-to-customer conversion)
- **Biggest bottleneck:** Visitor→Lead conversion (7.1%) — the single largest drop-off point in the entire funnel
- **Blended CAC:** ~$102 | **Blended ROI:** ~1,475%
- **Most efficient channels:** Referral and Email — lowest CAC, highest ROI, and best conversion at every funnel stage
- **Least efficient channel:** Paid Social — highest traffic volume but highest CAC and weakest ROI of any paid channel
- **Standout campaigns:** LinkedIn ABM and Drip Nurture convert far better than their channel averages despite lower volume
- **Seasonality:** Q4 (Oct–Dec) is the strongest quarter for both traffic and closed customers

## 🎯 Top Recommendations

1. Reallocate budget from Paid Social toward Referral and Email programs
2. Fix the Visitor→Lead bottleneck first — highest-leverage single-stage improvement
3. Scale specific high-performing campaigns (LinkedIn ABM, Drip Nurture) rather than whole channels
4. Tighten or pause underperforming Paid Search segments (Generic/Competitor Keywords)
5. Formalize and expand the Customer Referral Program
6. Front-load budget and content ahead of the Q4 seasonal demand lift

## 🚀 Running the Dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

The app looks for `marketing_funnel.csv` in the same folder (already included). It opens at
`http://localhost:8501` with sidebar filters (date range, channel, campaign) and five tabs:
Funnel, Trend, Channel Performance, Campaigns, and Raw Data (with CSV export).

To deploy it publicly for free, push this repo to GitHub and deploy via
[Streamlit Community Cloud](https://share.streamlit.io) — point it at `dashboard/app.py`.

## 🛠️ Methodology & Tools

- **Data generation:** Python (numpy, pandas) — daily stochastic binomial simulation of
  each funnel stage per channel/campaign, with channel-specific base conversion rates,
  monthly seasonality, weekday effects, and a gradual within-year conversion improvement
  to reflect ongoing optimization work
- **Analysis & visualization:** Python (pandas, matplotlib for the static report; Plotly
  for the interactive dashboard)
- **Report:** Generated as a formatted Word document (docx)

To adapt this for a real company's data, replace `marketing_funnel.csv` with an actual
analytics/CRM export (e.g. GA4 + HubSpot/Salesforce, mapped to the same column structure)
— no other changes required.
