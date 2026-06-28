import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Bottleneck Analysis",
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

.kpi-card.warning { border-top-color: #e05c00; }
.kpi-card.danger  { border-top-color: #c0392b; }

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

.kpi-card.warning .kpi-value { color: #c24f00; }
.kpi-card.danger  .kpi-value { color: #c0392b; }

.insight-box {
    background: #fff8e1;
    border-left: 5px solid #f39c12;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #7d5a00;
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


# ── Data ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "cleaned_uac.csv"

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])

top_backlog   = df.sort_values('Transfer_Backlog', ascending=False).head(10)
warning_days  = len(df[df['Alert'] == 'Warning'])
max_backlog   = int(df['Transfer_Backlog'].max())
avg_backlog   = round(df['Transfer_Backlog'].mean(), 1)
peak_date     = df.loc[df['Transfer_Backlog'].idxmax(), 'Date'].strftime('%b %d, %Y')


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Bottleneck Analysis")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Identifies periods where UAC transfers could not keep pace with incoming cases.

**Metrics tracked:**
- Transfer backlog trend
- Peak backlog periods
- Warning day count
""")
    st.markdown("---")
    st.markdown("### 📅 Date Range")
    st.markdown(f"**From:** {df['Date'].min().strftime('%b %d, %Y')}")
    st.markdown(f"**To:** {df['Date'].max().strftime('%b %d, %Y')}")
    st.markdown(f"**Total Records:** {len(df):,}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1a6fa8 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Bottleneck Analysis
    </p>
    <p style="color:#c8dff5; margin:10px 0 0; font-size:0.95rem;">
        Identifying transfer delays and backlog accumulation in the UAC care pipeline
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Backlog Summary</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:20px;">

  <div class="kpi-card warning" style="flex:1;">
    <div class="kpi-label">Warning Days</div>
    <div class="kpi-value">{warning_days}</div>
  </div>

  <div class="kpi-card danger" style="flex:1;">
    <div class="kpi-label">Peak Backlog</div>
    <div class="kpi-value">{max_backlog:,}</div>
  </div>

  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Avg Backlog</div>
    <div class="kpi-value">{avg_backlog}</div>
  </div>

  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Peak Date</div>
    <div class="kpi-value" style="font-size:1.1rem;">{peak_date}</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Backlog trend ─────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📈 Transfer Backlog Trend</p>', unsafe_allow_html=True)

fig1 = px.area(
    df, x='Date', y='Transfer_Backlog',
    title='Transfer Backlog Over Time'
)
fig1.update_traces(line=dict(color='#1a6fa8', width=2), fillcolor='rgba(26,111,168,0.12)')
fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# ── Top 10 bar chart + table side by side ─────────────────────────────────────

st.markdown('<p class="section-title">Top 10 Highest Backlog Periods</p>', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    fig2 = px.bar(
        top_backlog.sort_values('Transfer_Backlog'),
        x='Transfer_Backlog',
        y=top_backlog.sort_values('Transfer_Backlog')['Date'].dt.strftime('%b %d, %Y'),
        orientation='h',
        title='Top 10 Backlog Days',
        color='Transfer_Backlog',
        color_continuous_scale=['#D6EAF8', '#1a6fa8', '#0B3C5D']
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis_title='', xaxis_title='Backlog Count',
        coloraxis_showscale=False,
        title_font=dict(size=15, color='#0B3C5D'),
    )
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

with col_r:
    st.markdown("**📋 Backlog Records**")
    display_df = top_backlog[['Date', 'Transfer_Backlog']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%b %d, %Y')
    display_df.columns = ['Date', 'Backlog']
    display_df = display_df.sort_values('Backlog', ascending=False).reset_index(drop=True)
    display_df.index += 1
    st.dataframe(display_df, use_container_width=True, height=360)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
    ⚠️ <strong>{warning_days} warning days</strong> were detected across the dataset, with a peak backlog
    of <strong>{max_backlog:,}</strong> on <strong>{peak_date}</strong>.<br><br>
    Periods of increasing backlog indicate that transfers are not keeping pace with incoming cases.
    These periods should be monitored closely and may signal a need for additional resources or
    process improvements in the CBP → HHS transfer pipeline.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Bottleneck Analysis | UAC Care Transition Analytics Project")