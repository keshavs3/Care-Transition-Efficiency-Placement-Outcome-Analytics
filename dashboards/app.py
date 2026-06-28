import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
 
st.set_page_config(
    page_title="Care Transition Analytics",
    page_icon="🏥",
    layout="wide"
)
 
st.markdown("""
<style>
 
[data-testid="stAppViewContainer"] {
    background-color: #F0F4F8;
}
 
[data-testid="stSidebar"] {
    background-color: #003366;
}
 
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #003366 !important;
    background-color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton > button {
    border: 1px solid #c8dff5 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 4px 0 !important;
    width: 100% !important;
}

[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button:hover p,
[data-testid="stSidebar"] .stButton > button:hover span {
    background-color: #e8f0fe !important;
    color: #003366 !important;
    border-color: #1a5fa8 !important;
}
 
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button p,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button span,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button div {
    color: #003366 !important;
    background-color: #ffffff !important;
}
 
[data-testid="stDateInput"] input {
    color: #003366 !important;
    background-color: #ffffff !important;
}
 
[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 16px;
}
 
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #003366;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid #d0e4f7;
}
 
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 4px solid #003366;
    text-align: left;
}

 .kpi-card{
    min-height:120px;
}
 
.kpi-card.success { border-top-color: #1a7a4a; }
.kpi-card.warning { border-top-color: #e05c00; }
 
.kpi-label {
    font-size: 0.70rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
    line-height: 1.2;
}
 
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #003366;
    line-height: 1.1;
}
 
.kpi-card.warning .kpi-value { color: #c24f00; }
.kpi-card.success .kpi-value { color: #155c38; }
 
</style>
""", unsafe_allow_html=True)
 
 
# ── Sidebar ──────────────────────────────────────────────────────────────────
 
with st.sidebar:
    st.markdown("## 🏥 Care Transition Analytics")
    st.markdown("---")
    st.markdown("### 📅 Date Filter")
 
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "cleaned_uac.csv"

    df_raw = pd.read_csv(DATA_PATH)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'])
    
    st.markdown("**Quick select year:**")
    col_y1, col_y2, col_y3, col_y4 = st.columns(4)
    with col_y1:
        if st.button("2023", use_container_width=True):
            st.session_state['start_date'] = pd.Timestamp("2023-01-01")
            st.session_state['end_date']   = pd.Timestamp("2023-12-31")
    with col_y2:
        if st.button("2024", use_container_width=True):
            st.session_state['start_date'] = pd.Timestamp("2024-01-01")
            st.session_state['end_date']   = pd.Timestamp("2024-12-31")
    with col_y3:
        if st.button("2025", use_container_width=True):
            st.session_state['start_date'] = pd.Timestamp("2025-01-01")
            st.session_state['end_date']   = pd.Timestamp("2025-12-31")
    with col_y4:
        if st.button("All", use_container_width=True):
            st.session_state['start_date'] = df_raw['Date'].min()
            st.session_state['end_date']   = df_raw['Date'].max()
 
    default_start = st.session_state.get('start_date', df_raw['Date'].min())
    default_end   = st.session_state.get('end_date',   df_raw['Date'].max())
 
    start_date = st.date_input("Start Date", default_start)
    end_date   = st.date_input("End Date",   default_end)
 
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
This dashboard tracks the UAC care pipeline from CBP custody through HHS placement.
 
**Key metrics:**
- Transfer efficiency
- Discharge effectiveness
- Backlog trends
- Warning alerts
""")
    st.markdown("---")
 
 
# ── Filter data ───────────────────────────────────────────────────────────────
 
df = df_raw.copy()
filtered_df = df[
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
]
 
 
# ── Header ────────────────────────────────────────────────────────────────────
 
st.markdown("""
<div style="background: linear-gradient(90deg, #003366 0%, #1a5fa8 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
        🏥 Care Transition Efficiency &amp; Placement Outcome Analytics
    </p>
    <p style="color:#c8dff5; margin:10px 0 0; font-size:0.95rem;">
        Monitoring the UAC care pipeline · CBP → HHS → Sponsor Placement
    </p>
</div>
""", unsafe_allow_html=True)
 
 
# ── Project overview ──────────────────────────────────────────────────────────
 
with st.expander("📋 Project Overview", expanded=False):
    st.markdown("""
This dashboard analyzes the efficiency of the Unaccompanied Alien Children (UAC) care pipeline
from CBP custody through HHS care and sponsor placement.
 
**Objectives:**
- Evaluate CBP → HHS transfer efficiency
- Monitor placement and discharge outcomes
- Detect backlog accumulation and process bottlenecks
- Track outcome stability over time
 
The findings support policy improvements and faster family reunification.
""")
 
 
# ── KPI Cards ─────────────────────────────────────────────────────────────────
 
st.markdown('<p class="section-title">📊 Key Performance Indicators</p>', unsafe_allow_html=True)
 
warning_days = len(filtered_df[filtered_df['Alert'] == 'Warning'])
 
transfer_eff  = round(filtered_df['Transfer_Efficiency'].mean(), 2)
discharge_eff = round(filtered_df['Discharge_Effectiveness'].mean(), 3)
total_disc    = f"{int(filtered_df['Children discharged from HHS Care'].sum()):,}"
avg_backlog   = f"{round(filtered_df['Transfer_Backlog'].mean(), 0):,.0f}"
pipeline_tp = round(filtered_df['Pipeline_Throughput'].mean(), 2)
 
# ── YoY delta: compare filtered period to same period one year prior ──────────
def yoy_delta(series_now, series_prev):
    if len(series_prev) == 0 or series_prev.mean() == 0:
        return ""
    pct = (series_now.mean() - series_prev.mean()) / abs(series_prev.mean()) * 100
    arrow = "▲" if pct > 0 else "▼"
    color = "#155c38" if pct > 0 else "#c0392b"
    return f'<span style="font-size:0.72rem; font-weight:600; color:{color};">{arrow} {abs(pct):.1f}% YoY</span>'
 
start_dt = pd.to_datetime(start_date)
end_dt   = pd.to_datetime(end_date)
prev_start = start_dt - pd.DateOffset(years=1)
prev_end   = end_dt   - pd.DateOffset(years=1)
prev_df    = df[(df['Date'] >= prev_start) & (df['Date'] <= prev_end)]
 
delta_eff  = yoy_delta(filtered_df['Transfer_Efficiency'], prev_df['Transfer_Efficiency'])
delta_disc = yoy_delta(filtered_df['Discharge_Effectiveness'], prev_df['Discharge_Effectiveness'])
delta_back = yoy_delta(-filtered_df['Transfer_Backlog'], -prev_df['Transfer_Backlog'])  # invert: lower is better
delta_pipe = yoy_delta(
    filtered_df['Pipeline_Throughput'],
    prev_df['Pipeline_Throughput']
)
delta_warn_raw = len(prev_df[prev_df['Alert']=='Warning'])
if delta_warn_raw > 0:
    warn_pct = (warning_days - delta_warn_raw) / delta_warn_raw * 100
    w_arrow = "▲" if warn_pct > 0 else "▼"
    w_color = "#c0392b" if warn_pct > 0 else "#155c38"
    delta_warn = f'<span style="font-size:0.72rem; font-weight:600; color:{w_color};">{w_arrow} {abs(warn_pct):.1f}% YoY</span>'
else:
    delta_warn = ""
 
st.markdown(f"""
<div style="display:grid;
            grid-template-columns:repeat(6,1fr);
            gap:16px;
            margin-bottom:16px;">
 
  <div class="kpi-card success" style="flex:1;">
    <div class="kpi-label">Transfer Efficiency</div>
    <div class="kpi-value">{transfer_eff}</div>
    <div style="margin-top:4px;">{delta_eff}</div>
  </div>
 
  <div class="kpi-card success" style="flex:1;">
    <div class="kpi-label">Discharge Effectiveness</div>
    <div class="kpi-value">{discharge_eff}</div>
    <div style="margin-top:4px;">{delta_disc}</div>
  </div>
 
  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Total Discharges</div>
    <div class="kpi-value">{total_disc}</div>
  </div>
 
  <div class="kpi-card warning" style="flex:1;">
    <div class="kpi-label">Avg Backlog</div>
    <div class="kpi-value">{avg_backlog}</div>
    <div style="margin-top:4px;">{delta_back}</div>
  </div>
 
 <div class="kpi-card success" style="flex:1;">
    <div class="kpi-label">Pipeline Throughput</div>
    <div class="kpi-value">{pipeline_tp}</div>
    <div style="margin-top:4px;">{delta_pipe}</div>
</div>
 
  <div class="kpi-card warning" style="flex:1;">
    <div class="kpi-label">Warning Days</div>
    <div class="kpi-value">{warning_days}</div>
    <div style="margin-top:4px;">{delta_warn}</div>
  </div>
 
</div>
""", unsafe_allow_html=True)
 
if warning_days > 0:
    st.warning(f"⚠️ {warning_days} warning days detected in the selected period. Review backlog trends below.")
 
st.markdown("---")
 
 
 
# ── Chart helpers ─────────────────────────────────────────────────────────────
 
def style_fig(fig, color):
    fig.update_traces(line=dict(color=color, width=2.5))
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', zeroline=False),
        font=dict(family='sans-serif', size=12),
        title_font=dict(size=15, color='#003366'),
        hovermode='x unified'
    )
    return fig
 
 
# ── Charts row 1 ─────────────────────────────────────────────────────────────
 
st.markdown('<p class="section-title">📈 Trend Analysis</p>', unsafe_allow_html=True)
 
col_l, col_r = st.columns(2)
 
with col_l:
    fig1 = px.line(filtered_df, x='Date', y='Transfer_Efficiency',
                   title='Transfer Efficiency Trend')
    fig1 = style_fig(fig1, '#1a5fa8')
    fig1.add_hrect(y0=0.8, y1=1.0, fillcolor='rgba(26,122,74,0.07)',
                   line_width=0, annotation_text='Good zone', annotation_position='top left')
    st.plotly_chart(fig1, use_container_width=True)
 
with col_r:
    fig2 = px.line(filtered_df, x='Date', y='Discharge_Effectiveness',
                   title='Discharge Effectiveness Trend')
    fig2 = style_fig(fig2, '#1a7a4a')
    st.plotly_chart(fig2, use_container_width=True)
 
 
# ── Backlog chart ─────────────────────────────────────────────────────────────
 
fig3 = px.area(filtered_df, x='Date', y='Transfer_Backlog',
               title='Transfer Backlog Over Time')
fig3.update_traces(line=dict(color='#e05c00', width=2),
                   fillcolor='rgba(224,92,0,0.12)')
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
    title_font=dict(size=15, color='#003366'),
    hovermode='x unified'
)
st.plotly_chart(fig3, use_container_width=True)
 
st.markdown("---")
 
 
# ── Alert breakdown donut ─────────────────────────────────────────────────────
 
st.markdown('<p class="section-title">Alert Status Breakdown</p>', unsafe_allow_html=True)
 
alert_counts = filtered_df['Alert'].value_counts().reset_index()
alert_counts.columns = ['Alert', 'Count']
 
col_d1, col_d2 = st.columns([2, 3])
 
with col_d1:
    fig_donut = px.pie(
        alert_counts, names='Alert', values='Count',
        hole=0.55,
        color='Alert',
        color_discrete_map={'Normal': '#1a7a4a', 'Warning': '#e05c00'},
        title='Normal vs Warning Days'
    )
    fig_donut.update_traces(
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    fig_donut.update_layout(
        paper_bgcolor='white',
        height=260,
        margin=dict(l=40, r=40, t=50, b=40),
        title_font=dict(size=15, color='#003366'),
        showlegend=False,
        annotations=[dict(
            text=f"{len(filtered_df):,}<br>days",
            x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#003366'
        )]
    )
    st.plotly_chart(fig_donut, use_container_width=True)
 
with col_d2:
    normal_count = int(alert_counts.loc[alert_counts['Alert'] == 'Normal', 'Count'].sum()) if 'Normal' in alert_counts['Alert'].values else 0
    warning_count = int(alert_counts.loc[alert_counts['Alert'] == 'Warning', 'Count'].sum()) if 'Warning' in alert_counts['Alert'].values else 0
    warning_pct = round((warning_count / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0
 
    st.markdown(f"""
<div class="kpi-card" style="height:260px; display:flex; flex-direction:column; box-sizing:border-box;">
  <div class="kpi-label">📊 Period Summary</div>
  <div style="font-size:0.95rem; color:#374151; line-height:1.8; margin-top:8px;">
    Out of <strong>{len(filtered_df):,}</strong> days in the selected range,
    <strong style="color:#155c38;">{normal_count:,} were Normal</strong> and
    <strong style="color:#c24f00;">{warning_count:,} were Warning days</strong>
    (<strong>{warning_pct}%</strong> of the period).<br><br>
    A rising share of Warning days alongside the backlog trend above is a leading
    indicator of operational strain in the CBP → HHS transfer pipeline.
  </div>
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
 
 
# ── Dataset overview ──────────────────────────────────────────────────────────
 
st.markdown('<p class="section-title">🗂️ Dataset Overview</p>', unsafe_allow_html=True)
 
st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:16px;">
  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Total Rows</div>
    <div class="kpi-value">{len(df):,}</div>
  </div>
  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Columns</div>
    <div class="kpi-value">{len(df.columns)}</div>
  </div>
  <div class="kpi-card" style="flex:1;">
    <div class="kpi-label">Filtered Rows</div>
    <div class="kpi-value">{len(filtered_df):,}</div>
  </div>
</div>
""", unsafe_allow_html=True)
 
with st.expander("🔍 Preview Data", expanded=False):
    st.dataframe(filtered_df.head(10), use_container_width=True)
 
st.markdown("---")
csv = df_raw.to_csv(index=False)
st.download_button("📥 Download Dataset", csv, "cleaned_uac.csv", "text/csv")

st.caption("Care Transition Efficiency & Placement Outcome Analytics | Healthcare Analytics Project")

st.markdown(f"""
<div style="text-align:center; font-size:0.75rem; color:#888; margin-top:8px;">
  Data coverage: {df_raw['Date'].min().strftime('%b %d, %Y')} – {df_raw['Date'].max().strftime('%b %d, %Y')}
  &nbsp;·&nbsp; {len(df_raw):,} records
</div>
""", unsafe_allow_html=True)

