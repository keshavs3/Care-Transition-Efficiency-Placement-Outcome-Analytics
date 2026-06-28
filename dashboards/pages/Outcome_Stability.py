import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Outcome Stability Analysis",
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
.kpi-card.purple  .kpi-value { color: #6a3fa8; }

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

std_dev   = round(df['Discharge_Effectiveness'].std(), 4)
avg_eff   = round(df['Discharge_Effectiveness'].mean(), 3)
max_roll  = round(df['Rolling_Discharge_Effectiveness'].max(), 3)
min_roll  = round(df['Rolling_Discharge_Effectiveness'].min(), 3)
roll_std  = round(df['Rolling_Discharge_Effectiveness'].std(), 4)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Outcome Stability")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Measures the consistency and volatility of discharge effectiveness over time.

**Charts included:**
- Rolling effectiveness trend
- Discharge distribution
- Stability band analysis
""")
    st.markdown("---")
    st.markdown(f"**Std Dev (raw):** {std_dev}")
    st.markdown(f"**Std Dev (rolling):** {roll_std}")
    st.markdown(f"**Rolling range:** {min_roll} – {max_roll}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1E33BC 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Outcome Stability Analysis
    </p>
    <p style="color:#c8d5f5; margin:10px 0 0; font-size:0.95rem;">
        Measuring consistency and volatility of discharge effectiveness across the UAC pipeline
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">Stability Metrics</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">

  <div class="kpi-card success" style="flex:1; min-width:130px;">
    <div class="kpi-label">Avg Effectiveness</div>
    <div class="kpi-value">{avg_eff}</div>
  </div>

  <div class="kpi-card purple" style="flex:1; min-width:130px;">
    <div class="kpi-label">Std Deviation</div>
    <div class="kpi-value">{std_dev}</div>
  </div>

  <div class="kpi-card success" style="flex:1; min-width:130px;">
    <div class="kpi-label">Rolling Peak</div>
    <div class="kpi-value">{max_roll}</div>
  </div>

  <div class="kpi-card warning" style="flex:1; min-width:130px;">
    <div class="kpi-label">Rolling Low</div>
    <div class="kpi-value">{min_roll}</div>
  </div>

  <div class="kpi-card purple" style="flex:1; min-width:130px;">
    <div class="kpi-label">Rolling Std Dev</div>
    <div class="kpi-value">{roll_std}</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Rolling trend with stability band ────────────────────────────────────────

st.markdown('<p class="section-title">📈 Rolling Discharge Effectiveness Trend</p>', unsafe_allow_html=True)

roll_mean = df['Rolling_Discharge_Effectiveness'].mean()
roll_sd   = df['Rolling_Discharge_Effectiveness'].std()

fig1 = go.Figure()

# Stability band (±1 std dev)
fig1.add_trace(go.Scatter(
    x=pd.concat([df['Date'], df['Date'][::-1]]),
    y=pd.concat([
        pd.Series([roll_mean + roll_sd] * len(df)),
        pd.Series([roll_mean - roll_sd] * len(df[::-1]))
    ]),
    fill='toself',
    fillcolor='rgba(30,51,188,0.08)',
    line=dict(color='rgba(0,0,0,0)'),
    name='±1 Std Dev Band',
    hoverinfo='skip'
))

# Mean line
fig1.add_hline(
    y=roll_mean, line_dash='dash', line_color='#e05c00',
    annotation_text='Rolling Mean', annotation_position='top left'
)

# Main line
fig1.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Rolling_Discharge_Effectiveness'],
    line=dict(color='#1E33BC', width=2.5),
    name='Rolling Effectiveness',
    hovertemplate='%{x|%b %d, %Y}<br>Value: %{y:.4f}<extra></extra>'
))

fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Rolling Discharge Effectiveness'),
    title='Rolling Discharge Effectiveness with Stability Band',
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# ── Histogram + box plot side by side ────────────────────────────────────────

st.markdown('<p class="section-title">📉 Discharge Effectiveness Distribution</p>', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    fig2 = px.histogram(
        df, x='Discharge_Effectiveness',
        title='Discharge Effectiveness Distribution',
        nbins=30,
        color_discrete_sequence=['#1E33BC']
    )
    fig2.update_traces(
        marker_line_color='#39D5F5',
        marker_line_width=1.5,
        opacity=0.75
    )
    fig2.add_vline(
        x=avg_eff, line_dash='dash', line_color='#e05c00',
        annotation_text=f'Mean: {avg_eff}', annotation_position='top right'
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title='Discharge Effectiveness'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Count'),
        title_font=dict(size=15, color='#0B3C5D'),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_r:
    fig3 = px.box(
        df, y='Discharge_Effectiveness',
        title='Spread & Outliers',
        color_discrete_sequence=['#1E33BC']
    )
    fig3.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Discharge Effectiveness'),
        title_font=dict(size=15, color='#0B3C5D'),
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

stability = "low" if std_dev < 0.01 else "moderate" if std_dev < 0.05 else "high"

st.markdown(f"""
<div class="insight-box">
    Discharge effectiveness averaged <strong>{avg_eff}</strong> with a standard deviation
    of <strong>{std_dev}</strong>, indicating <strong>{stability} volatility</strong> in outcomes.<br><br>
    The rolling effectiveness ranged from <strong>{min_roll}</strong> to <strong>{max_roll}</strong>.
    The shaded stability band (±1 std dev) on the trend chart highlights periods where performance
    deviated from the norm — sustained periods outside the band may signal operational instability
    and warrant closer investigation.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Outcome Stability Analysis | UAC Care Transition Analytics Project")