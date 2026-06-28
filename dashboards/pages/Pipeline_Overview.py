import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Care Pipeline Overview",
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

.pipeline-step {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    text-align: center;
    flex: 1;
    min-width: 120px;
}
.pipeline-icon { font-size: 2rem; margin-bottom: 6px; }
.pipeline-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #0B3C5D;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.pipeline-sub {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 4px;
}
.pipeline-arrow {
    font-size: 1.4rem;
    color: #328CC1;
    display: flex;
    align-items: center;
    padding: 0 4px;
}

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

avg_cbp       = int(round(df['Children in CBP custody'].mean()))
avg_hhs       = int(round(df['Children in HHS Care'].mean()))
avg_discharge = int(round(df['Children discharged from HHS Care'].mean()))
total_disc    = f"{int(df['Children discharged from HHS Care'].sum()):,}"
avg_transfer  = round(df['Transfer_Efficiency'].mean(), 2)

transfer_rate = round((avg_discharge / avg_hhs) * 100, 1) if avg_hhs > 0 else 0


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Care Pipeline Overview")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Visualizes how children move through the UAC care pipeline from CBP custody through HHS care to sponsor placement.

**Sections:**
- Pipeline flow diagram
- Stage-level statistics
- Sankey flow chart
- Trend comparison
""")
    st.markdown("---")
    st.markdown(f"**Avg CBP Custody:** {avg_cbp:,}")
    st.markdown(f"**Avg HHS Care:** {avg_hhs:,}")
    st.markdown(f"**Avg Daily Discharges:** {avg_discharge:,}")
    st.markdown(f"**Daily Discharge Rate:** {transfer_rate}%")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #328CC1 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Care Pipeline Overview
    </p>
    <p style="color:#c8eaf5; margin:10px 0 0; font-size:0.95rem;">
        Tracking the flow of children through CBP custody → HHS care → sponsor placement
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Pipeline Statistics</p>', unsafe_allow_html=True)

avg_throughput_kpi = round(df['Pipeline_Throughput'].mean(), 2)

p1, p2, p3, p4, p5, p6 = st.columns(6)

pipeline_cards = [
    (p1, "warning", "Avg CBP Custody",        f"{avg_cbp:,}"),
    (p2, "",        "Avg HHS Care",            f"{avg_hhs:,}"),
    (p3, "success", "Avg Daily Discharges",    f"{avg_discharge:,}"),
    (p4, "success", "Total Discharged",        total_disc),
    (p5, "purple",  "Avg Transfer Efficiency", f"{avg_transfer}"),
    (p6, "purple",  "Avg Throughput",          f"{avg_throughput_kpi}"),
]

for col, cls, label, value in pipeline_cards:
    with col:
        st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:110px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="font-size:1.4rem;">{value}</div>
</div>""", unsafe_allow_html=True)


st.markdown("---")


# ── Visual pipeline flow ──────────────────────────────────────────────────────

st.markdown('<p class="section-title">Care Transition Pipeline</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; align-items:center; gap:4px; margin-bottom:20px; flex-wrap:wrap;">

  <div class="pipeline-step">
    <div class="pipeline-icon">🏛️</div>
    <div class="pipeline-label">CBP Custody</div>
    <div class="pipeline-sub">Avg {avg_cbp:,} children</div>
  </div>

  <div class="pipeline-arrow">➜</div>

  <div class="pipeline-step">
    <div class="pipeline-icon">🚌</div>
    <div class="pipeline-label">Transfer</div>
    <div class="pipeline-sub">Efficiency: {avg_transfer}</div>
  </div>

  <div class="pipeline-arrow">➜</div>

  <div class="pipeline-step">
    <div class="pipeline-icon">🏥</div>
    <div class="pipeline-label">HHS Care</div>
    <div class="pipeline-sub">Avg {avg_hhs:,} children</div>
  </div>

  <div class="pipeline-arrow">➜</div>

  <div class="pipeline-step">
    <div class="pipeline-icon">📤</div>
    <div class="pipeline-label">Discharge</div>
    <div class="pipeline-sub">Avg {avg_discharge:,}/day</div>
  </div>

  <div class="pipeline-arrow">➜</div>

  <div class="pipeline-step">
    <div class="pipeline-icon">🏠</div>
    <div class="pipeline-label">Sponsor Placement</div>
    <div class="pipeline-sub">Final outcome</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Sankey chart ──────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">Pipeline Flow (Sankey)</p>', unsafe_allow_html=True)

sankey_cbp  = avg_cbp
sankey_hhs  = avg_hhs
sankey_disc = avg_discharge
sankey_rem  = max(sankey_hhs - sankey_disc, 0)

fig_sankey = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node=dict(
        label=["CBP Custody", "Transferred to HHS", "HHS Care", "Discharged", "Still in HHS Care"],
        color=["#e05c00", "#328CC1", "#0B3C5D", "#1a7a4a", "#6a3fa8"],
        pad=20,
        thickness=24,
    ),
    link=dict(
        source=[0, 1, 2, 2],
        target=[1, 2, 3, 4],
        value=[sankey_cbp, sankey_hhs, sankey_disc, sankey_rem],
        color=["rgba(50,140,193,0.3)", "rgba(11,60,93,0.3)",
               "rgba(26,122,74,0.3)", "rgba(106,63,168,0.3)"]
    )
)])

fig_sankey.update_layout(
    title='Average Daily Child Flow Through the UAC Pipeline',
    title_font=dict(size=15, color='#0B3C5D'),
    paper_bgcolor='white',
    margin=dict(l=10, r=10, t=50, b=10),
    height=350
)
st.plotly_chart(fig_sankey, use_container_width=True)

st.markdown("---")


# ── CBP vs HHS trend ──────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📈 CBP vs HHS Population Over Time</p>', unsafe_allow_html=True)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=df['Date'], y=df['Children in CBP custody'],
    name='CBP Custody', line=dict(color='#e05c00', width=2),
    hovertemplate='%{x|%b %d, %Y}<br>CBP: %{y:,}<extra></extra>'
))
fig_trend.add_trace(go.Scatter(
    x=df['Date'], y=df['Children in HHS Care'],
    name='HHS Care', line=dict(color='#0B3C5D', width=2),
    hovertemplate='%{x|%b %d, %Y}<br>HHS: %{y:,}<extra></extra>'
))
fig_trend.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Children'),
    title='Children in CBP Custody vs HHS Care',
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")


# ── Pipeline Throughput & HHS Care Load Ratio ─────────────────────────────────

st.markdown('<p class="section-title">Pipeline Throughput & Care Load Ratio</p>', unsafe_allow_html=True)

avg_throughput = round(df['Pipeline_Throughput'].mean(), 2)
avg_load_ratio = round(df['HHS_Care_Load_Ratio'].mean(), 3)

col_t1, col_t2 = st.columns(2)

with col_t1:
    fig_throughput = go.Figure()
    fig_throughput.add_hline(
        y=1.0, line_dash='dash', line_color='#1a7a4a',
        annotation_text='Balanced (1.0)', annotation_position='top left'
    )
    fig_throughput.add_trace(go.Scatter(
        x=df['Date'], y=df['Pipeline_Throughput'],
        line=dict(color='#328CC1', width=1.5),
        name='Pipeline Throughput',
        hovertemplate='%{x|%b %d, %Y}<br>Throughput: %{y:.2f}<extra></extra>'
    ))
    fig_throughput.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Throughput (Exits ÷ Entries)'),
        title=f'Pipeline Throughput Rate (Avg: {avg_throughput})',
        title_font=dict(size=15, color='#0B3C5D'),
        hovermode='x unified', showlegend=False
    )
    st.plotly_chart(fig_throughput, use_container_width=True)

with col_t2:
    fig_load = go.Figure()
    fig_load.add_trace(go.Scatter(
        x=df['Date'], y=df['HHS_Care_Load_Ratio'],
        line=dict(color='#6a3fa8', width=1.5),
        fill='tozeroy', fillcolor='rgba(106,63,168,0.08)',
        name='HHS Care Load Ratio',
        hovertemplate='%{x|%b %d, %Y}<br>Load Ratio: %{y:.3f}<extra></extra>'
    ))
    fig_load.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='HHS Care Load Ratio'),
        title=f'HHS Care Load Ratio (Avg: {avg_load_ratio})',
        title_font=dict(size=15, color='#0B3C5D'),
        hovermode='x unified', showlegend=False
    )
    st.plotly_chart(fig_load, use_container_width=True)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
    On average, <strong>{avg_cbp:,}</strong> children are held in CBP custody before transfer,
    while <strong>{avg_hhs:,}</strong> are in HHS care at any given time.
    Daily discharges average <strong>{avg_discharge:,}</strong> children — a daily discharge rate
    of approximately <strong>{transfer_rate}%</strong> of the HHS population.<br><br>
    Delays at any stage of the pipeline — CBP transfer, HHS intake, or sponsor placement —
    compound across the system and increase care load. Monitoring the gap between CBP and HHS
    populations helps identify upstream pressure before it becomes a downstream bottleneck.<br><br>
    Pipeline Throughput (total exits ÷ total entries) averaged <strong>{avg_throughput}</strong> —
    values above 1.0 indicate the system is discharging children faster than new cases are entering,
    while values below 1.0 signal a growing system-wide backlog.<br><br>
    The HHS Care Load Ratio averaged <strong>{avg_load_ratio}</strong>, reflecting how much of the
    HHS care population remains active relative to total throughput. Sustained low throughput
    combined with a high care load ratio is an early warning sign of systemic strain.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Care Pipeline Overview | UAC Care Transition Analytics Project")