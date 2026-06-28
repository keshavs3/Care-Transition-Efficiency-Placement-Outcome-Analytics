import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Monthly Placement Trends",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stAppViewContainer"] { background-color: #F0F4F8; }

[data-testid="stSidebar"] { background-color: #0B3C5D; }
[data-testid="stSidebar"] * { color: #ffffff !important; }

.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0B3C5D;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid #D6EAF8;
}

.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 4px solid #0B3C5D;
}
.kpi-card.success { border-top-color: #1a7a4a; }
.kpi-card.warning { border-top-color: #e05c00; }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0B3C5D;
    line-height: 1.1;
}
.kpi-card.success .kpi-value { color: #155c38; }
.kpi-card.warning .kpi-value { color: #c24f00; }

.insight-box {
    background: #e8f4fd;
    border-left: 5px solid #1a6fa8;
    border-radius: 10px;
    padding: 16px 20px;
    color: #0B3C5D;
    font-size: 0.95rem;
    line-height: 1.6;
}

[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 16px;
}

</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "cleaned_uac.csv"

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').astype(str)

monthly = df.groupby('Month')['Children discharged from HHS Care'].sum().reset_index()
monthly.columns = ['Month', 'Discharges']

peak_month    = monthly.loc[monthly['Discharges'].idxmax(), 'Month']
peak_val      = f"{int(monthly['Discharges'].max()):,}"
lowest_month  = monthly.loc[monthly['Discharges'].idxmin(), 'Month']
lowest_val    = f"{int(monthly['Discharges'].min()):,}"
avg_monthly   = f"{int(monthly['Discharges'].mean()):,}"
total         = f"{int(monthly['Discharges'].sum()):,}"


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📅 Monthly Placement Trends")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Tracks monthly discharge volumes to identify seasonal patterns and long-term changes in placement outcomes.

**Charts included:**
- Monthly trend line
- Monthly bar breakdown
- Peak vs lowest comparison
""")
    st.markdown("---")
    st.markdown(f"**Months tracked:** {len(monthly)}")
    st.markdown(f"**Peak month:** {peak_month}")
    st.markdown(f"**Lowest month:** {lowest_month}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #6a3fa8 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Monthly Placement Trends
    </p>
    <p style="color:#ddd5f5; margin:10px 0 0; font-size:0.95rem;">
        Seasonal patterns and long-term changes in UAC discharge and placement outcomes
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Monthly Discharge Summary</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">

  <div class="kpi-card" style="flex:1; min-width:130px;">
    <div class="kpi-label">Total Discharged</div>
    <div class="kpi-value">{total}</div>
  </div>

  <div class="kpi-card" style="flex:1; min-width:130px;">
    <div class="kpi-label">Avg per Month</div>
    <div class="kpi-value">{avg_monthly}</div>
  </div>

  <div class="kpi-card success" style="flex:1; min-width:130px;">
    <div class="kpi-label">Peak Month</div>
    <div class="kpi-value" style="font-size:1.1rem;">{peak_month}</div>
    <div style="font-size:0.85rem; color:#155c38; margin-top:4px;">{peak_val} discharges</div>
  </div>

  <div class="kpi-card warning" style="flex:1; min-width:130px;">
    <div class="kpi-label">Lowest Month</div>
    <div class="kpi-value" style="font-size:1.1rem;">{lowest_month}</div>
    <div style="font-size:0.85rem; color:#c24f00; margin-top:4px;">{lowest_val} discharges</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Trend line ────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📈 Monthly Discharge Trend</p>', unsafe_allow_html=True)

fig1 = px.line(
    monthly, x='Month', y='Discharges',
    title='Monthly Placement Trend',
    markers=True
)
fig1.update_traces(
    line=dict(color='#6a3fa8', width=2.5),
    marker=dict(size=6, color='#6a3fa8')
)
fig1.add_hline(
    y=monthly['Discharges'].mean(),
    line_dash='dash', line_color='#e05c00',
    annotation_text='Monthly Average',
    annotation_position='top left'
)
fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=60),
    xaxis=dict(showgrid=False, tickangle=-45, title='Month'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Children Discharged'),
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# ── Bar chart ─────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Monthly Discharge Breakdown</p>', unsafe_allow_html=True)

fig2 = px.bar(
    monthly, x='Month', y='Discharges',
    title='Monthly Discharges by Period',
    color='Discharges',
    color_continuous_scale=['#D6EAF8', '#6a3fa8', '#0B3C5D']
)
fig2.update_traces(marker_line_width=0)
fig2.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=60),
    xaxis=dict(showgrid=False, tickangle=-45, title='Month'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Children Discharged'),
    coloraxis_showscale=False,
    title_font=dict(size=15, color='#0B3C5D'),
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
    Across <strong>{len(monthly)} months</strong> of data, monthly discharges averaged
    <strong>{avg_monthly}</strong> children, peaking at <strong>{peak_val}</strong> in
    <strong>{peak_month}</strong> and dropping to a low of <strong>{lowest_val}</strong>
    in <strong>{lowest_month}</strong>.<br><br>
    Monthly discharge trends help identify seasonal patterns and long-term shifts in placement
    outcomes. Periods of sustained decline should be investigated for capacity constraints,
    policy changes, or processing bottlenecks in the CBP → HHS pipeline.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Monthly Placement Trends | UAC Care Transition Analytics Project")