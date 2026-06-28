import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Discharge Analytics",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #F0F4F8;
}

[data-testid="stSidebar"] {
    background-color: #0B3C5D;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

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
    text-align: left;
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
    margin: 12px 0;
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

avg_discharge   = round(df['Discharge_Effectiveness'].mean(), 3)
max_discharge   = round(df['Discharge_Effectiveness'].max(), 3)
min_discharge   = round(df['Discharge_Effectiveness'].min(), 3)
total_discharged = f"{int(df['Children discharged from HHS Care'].sum()):,}"

monthly_discharge = (
    df.groupby('Month')['Children discharged from HHS Care']
    .sum()
    .reset_index()
)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Discharge Analytics")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Evaluates sponsor placement outcomes and discharge performance across the UAC care pipeline.

**Metrics tracked:**
- Discharge effectiveness trend
- Monthly discharge volume
- Discharge distribution
""")
    st.markdown("---")
    st.markdown("### 📅 Date Range")
    st.markdown(f"**From:** {df['Date'].min().strftime('%b %d, %Y')}")
    st.markdown(f"**To:** {df['Date'].max().strftime('%b %d, %Y')}")
    st.markdown(f"**Total Records:** {len(df):,}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1a7a4a 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
        Discharge Analytics
    </p>
    <p style="color:#c8f0d5; margin:10px 0 0; font-size:0.95rem;">
        Tracking sponsor placement outcomes and discharge effectiveness over time
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Discharge Summary</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:20px;">

  <div class="kpi-card success" style="flex:1;">
    <div class="kpi-label">Avg Effectiveness</div>
    <div class="kpi-value">{avg_discharge}</div>
  </div>

  <div class="kpi-card success" style="flex:1;">
    <div class="kpi-label">Peak Effectiveness</div>
    <div class="kpi-value">{max_discharge}</div>
  </div>

  <div class="kpi-card warning" style="flex:1;">
    <div class="kpi-label">Lowest Effectiveness</div>
    <div class="kpi-value">{min_discharge}</div>
  </div>

  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Total Discharged</div>
    <div class="kpi-value">{total_discharged}</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Discharge effectiveness trend ─────────────────────────────────────────────

st.markdown('<p class="section-title">📈 Discharge Effectiveness Trend</p>', unsafe_allow_html=True)

fig1 = px.line(df, x='Date', y='Discharge_Effectiveness',
               title='Discharge Effectiveness Over Time')
fig1.update_traces(line=dict(color='#1a7a4a', width=2.5))
fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', zeroline=False),
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified'
)
fig1.add_hrect(
    y0=avg_discharge * 0.95, y1=avg_discharge * 1.05,
    fillcolor='rgba(26,122,74,0.08)', line_width=0,
    annotation_text='Avg band', annotation_position='top left'
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# ── Monthly discharges + box plot side by side ────────────────────────────────

st.markdown('<p class="section-title">📅 Monthly & Distribution Breakdown</p>', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    fig2 = px.bar(
        monthly_discharge,
        x='Month',
        y='Children discharged from HHS Care',
        title='Monthly Discharges',
        color='Children discharged from HHS Care',
        color_continuous_scale=['#D6EAF8', '#1a7a4a', '#0B3C5D']
    )
    fig2.update_traces(marker_line_width=0)
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title='Month'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Children Discharged'),
        coloraxis_showscale=False,
        title_font=dict(size=15, color='#0B3C5D'),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_r:
    fig3 = px.box(
        df,
        y='Children discharged from HHS Care',
        title='Discharge Distribution',
        color_discrete_sequence=['#1a7a4a']
    )
    fig3.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
        title_font=dict(size=15, color='#0B3C5D'),
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
    <strong>Discharge Effectiveness</strong> averaged <strong>{avg_discharge}</strong> across the full period,
    ranging from <strong>{min_discharge}</strong> to a peak of <strong>{max_discharge}</strong>.<br><br>
    A total of <strong>{total_discharged}</strong> children were discharged from HHS care.
    Stable discharge rates suggest consistent reunification performance —
    any downward trend should be investigated for process bottlenecks or capacity constraints.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Discharge Analytics | UAC Care Transition Analytics Project")