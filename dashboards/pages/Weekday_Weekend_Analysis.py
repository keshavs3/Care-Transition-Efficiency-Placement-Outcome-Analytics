import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Weekday vs Weekend Analysis",
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
.kpi-card.blue    { border-top-color: #1747A0; }
.kpi-card.purple  { border-top-color: #6a3fa8; }

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
.kpi-card.blue    .kpi-value { color: #1747A0; }
.kpi-card.purple  .kpi-value { color: #6a3fa8; }

.insight-box-warning {
    background: #fff8e1;
    border-left: 5px solid #f39c12;
    border-radius: 10px;
    padding: 16px 20px;
    color: #7d5a00;
    font-size: 0.95rem;
    line-height: 1.6;
}
.insight-box-success {
    background: #e8faf0;
    border-left: 5px solid #1a7a4a;
    border-radius: 10px;
    padding: 16px 20px;
    color: #0f3d22;
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
df['Day_Type'] = np.where(df['Date'].dt.dayofweek >= 5, 'Weekend', 'Weekday')
df['Day_Name'] = df['Date'].dt.day_name()

weekday_weekend = df.groupby('Day_Type')['Transfer_Efficiency'].mean().reset_index()
by_day = df.groupby('Day_Name')['Transfer_Efficiency'].mean().reset_index()

# Order days correctly
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
by_day['Day_Name'] = pd.Categorical(by_day['Day_Name'], categories=day_order, ordered=True)
by_day = by_day.sort_values('Day_Name')

weekday_eff = round(weekday_weekend[weekday_weekend['Day_Type']=='Weekday']['Transfer_Efficiency'].values[0], 3)
weekend_eff = round(weekday_weekend[weekday_weekend['Day_Type']=='Weekend']['Transfer_Efficiency'].values[0], 3)
diff        = round(abs(weekday_eff - weekend_eff), 3)
pct_diff    = round((abs(weekday_eff - weekend_eff) / weekday_eff) * 100, 1)
higher      = 'Weekday' if weekday_eff > weekend_eff else 'Weekend'


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Weekday vs Weekend Analysis")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Compares transfer efficiency across weekdays and weekends to detect operational consistency or staffing-related slowdowns.

**Charts included:**
- Weekday vs weekend comparison
- Day-of-week breakdown
- Efficiency distribution by day type
""")
    st.markdown("---")
    st.markdown(f"**Weekday Avg:** {weekday_eff}")
    st.markdown(f"**Weekend Avg:** {weekend_eff}")
    st.markdown(f"**Difference:** {diff} ({pct_diff}%)")
    st.markdown(f"**Higher efficiency:** {higher}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #2e7bcf 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Weekday vs Weekend Analysis
    </p>
    <p style="color:#c8dff5; margin:10px 0 0; font-size:0.95rem;">
        Detecting operational consistency and staffing-related patterns across the week
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Efficiency Summary</p>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

cards = [
    (k1, "blue",    "Weekday Avg",       f"{weekday_eff}"),
    (k2, "purple",  "Weekend Avg",       f"{weekend_eff}"),
    (k3, "warning", "Difference",        f"{diff}"),
    (k4, "success" if weekday_eff >= weekend_eff else "warning",
         "Higher Efficiency", higher),
]

for col, cls, label, value in cards:
    with col:
        st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:110px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
</div>""", unsafe_allow_html=True)

st.markdown("---")


# ── Weekday vs Weekend bar + box side by side ─────────────────────────────────

st.markdown('<p class="section-title">📊 Weekday vs Weekend Comparison</p>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    fig1 = px.bar(
        weekday_weekend,
        x='Day_Type', y='Transfer_Efficiency',
        title='Avg Transfer Efficiency by Day Type',
        color='Day_Type',
        color_discrete_map={'Weekday': '#1747A0', 'Weekend': '#6a3fa8'},
        text='Transfer_Efficiency'
    )
    fig1.update_traces(
        marker_line_width=0, opacity=0.85,
        texttemplate='%{text:.3f}', textposition='outside'
    )
    fig1.add_hline(
        y=df['Transfer_Efficiency'].mean(), line_dash='dash', line_color='#e05c00',
        annotation_text='Overall avg', annotation_position='top left'
    )
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Avg Transfer Efficiency'),
        title_font=dict(size=15, color='#0B3C5D'),
        showlegend=False
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_r:
    fig2 = px.box(
        df, x='Day_Type', y='Transfer_Efficiency',
        title='Efficiency Distribution by Day Type',
        color='Day_Type',
        color_discrete_map={'Weekday': '#1747A0', 'Weekend': '#6a3fa8'}
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Transfer Efficiency'),
        title_font=dict(size=15, color='#0B3C5D'),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# ── Day-of-week breakdown ─────────────────────────────────────────────────────

st.markdown('<p class="section-title">📅 Efficiency by Day of Week</p>', unsafe_allow_html=True)

colors = ['#1747A0','#1747A0','#1747A0','#1747A0','#1747A0','#6a3fa8','#6a3fa8']

fig3 = go.Figure(go.Bar(
    x=by_day['Day_Name'],
    y=by_day['Transfer_Efficiency'],
    marker_color=colors,
    marker_line_width=0,
    opacity=0.85,
    text=by_day['Transfer_Efficiency'].round(3),
    textposition='outside',
    hovertemplate='%{x}<br>Efficiency: %{y:.3f}<extra></extra>'
))
fig3.add_hline(
    y=df['Transfer_Efficiency'].mean(), line_dash='dash', line_color='#e05c00',
    annotation_text='Overall avg', annotation_position='top left'
)
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=50, b=10),
    xaxis=dict(showgrid=False, title='Day of Week'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Avg Transfer Efficiency'),
    title='Average Transfer Efficiency by Day of Week<br><sup style="color:#1747A0">■ Weekday</sup>  <sup style="color:#6a3fa8">■ Weekend</sup>',
    title_font=dict(size=15, color='#0B3C5D'),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

if weekday_eff > weekend_eff:
    st.markdown(f"""
<div class="insight-box-warning">
    ⚠️ Weekday transfer efficiency (<strong>{weekday_eff}</strong>) is <strong>{pct_diff}% higher</strong>
    than weekend efficiency (<strong>{weekend_eff}</strong>), a gap of <strong>{diff}</strong>.<br><br>
    This suggests that transitions from CBP custody to HHS care slow down during weekends,
    potentially due to reduced staffing, administrative constraints, or lower operational
    capacity. Targeted weekend interventions could help close this gap and improve
    overall reunification timelines.
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class="insight-box-success">
    Weekday (<strong>{weekday_eff}</strong>) and weekend (<strong>{weekend_eff}</strong>) transfer
    efficiency are comparable, with a difference of only <strong>{diff}</strong> ({pct_diff}%).<br><br>
    This indicates a stable and consistent care transition process throughout the week
    with no significant weekend-related operational slowdowns — a positive sign of
    operational resilience across all days.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Weekday vs Weekend Analysis | UAC Care Transition Analytics Project")