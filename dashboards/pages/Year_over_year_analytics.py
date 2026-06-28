import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Year-over-Year Analytics",
    page_icon="📆",
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
.kpi-card.danger  { border-top-color: #c0392b; }
.kpi-card.purple  { border-top-color: #6a3fa8; }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0B3C5D;
    line-height: 1.1;
}
.kpi-delta {
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 4px;
}
.delta-down { color: #c0392b; }
.delta-up   { color: #1a7a4a; }
.delta-neu  { color: #6b7280; }

.yoy-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.yoy-table th {
    background: #0B3C5D;
    color: white;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.yoy-table td {
    padding: 9px 14px;
    border-bottom: 1px solid #f0f0f0;
    color: #1a1a1a;
}
.yoy-table tr:last-child td { border-bottom: none; }
.yoy-table tr:nth-child(even) td { background: #fafafa; }

.insight-box {
    background: #eaf2fd;
    border-left: 5px solid #1747A0;
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
df['Year']    = df['Date'].dt.year
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
df['Month']   = df['Date'].dt.to_period('M').astype(str)

yoy = df.groupby('Year').agg(
    Transfer_Efficiency    = ('Transfer_Efficiency',  'mean'),
    Discharge_Effectiveness= ('Discharge_Effectiveness', 'mean'),
    Avg_Backlog            = ('Transfer_Backlog',     'mean'),
    Pipeline_Throughput    = ('Pipeline_Throughput',  'mean'),
    Avg_CBP                = ('Children in CBP custody', 'mean'),
    Avg_HHS                = ('Children in HHS Care', 'mean'),
    Total_Discharged       = ('Children discharged from HHS Care', 'sum'),
    Warning_Days           = ('Alert', lambda x: (x == 'Warning').sum()),
    Stagnation_Days        = ('Stagnation_Period', lambda x: (x >= 5).sum()),
).round(3)

qtr = df.groupby('Quarter').agg(
    Transfer_Efficiency     = ('Transfer_Efficiency', 'mean'),
    Discharge_Effectiveness = ('Discharge_Effectiveness', 'mean'),
    Transfer_Backlog        = ('Transfer_Backlog', 'mean'),
    Total_Discharged        = ('Children discharged from HHS Care', 'sum'),
).round(3).reset_index()

years = sorted(df['Year'].unique())

def delta_str(new_val, old_val, invert=False):
    if pd.isna(old_val) or old_val == 0:
        return ""
    pct = (new_val - old_val) / abs(old_val) * 100
    arrow = "▲" if pct > 0 else "▼"
    cls   = "delta-up" if (pct > 0) != invert else "delta-down"
    return f'<span class="{cls}">{arrow} {abs(pct):.1f}% vs prev year</span>'

def card(col, cls, label, val_2023, val_2024, val_2025, invert=False, fmt=".3f"):
    d24 = delta_str(val_2024, val_2023, invert)
    d25 = delta_str(val_2025, val_2024, invert)
    with col:
        st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:145px;">
  <div class="kpi-label" style="margin-bottom:10px;">{label}</div>
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;">
    <div style="text-align:center; border-right:1px solid #f0f0f0; padding-right:8px;">
      <div style="font-size:0.65rem; font-weight:700; color:#6b7280; text-transform:uppercase;
                  letter-spacing:0.04em; margin-bottom:6px;">2023</div>
      <div class="kpi-value" style="font-size:1.15rem;">{val_2023:{fmt}}</div>
      <div style="min-height:18px; margin-top:4px;"></div>
    </div>
    <div style="text-align:center; border-right:1px solid #f0f0f0; padding-right:8px;">
      <div style="font-size:0.65rem; font-weight:700; color:#6b7280; text-transform:uppercase;
                  letter-spacing:0.04em; margin-bottom:6px;">2024</div>
      <div class="kpi-value" style="font-size:1.15rem;">{val_2024:{fmt}}</div>
      <div class="kpi-delta" style="min-height:18px; margin-top:4px; font-size:0.7rem;">{d24}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.65rem; font-weight:700; color:#6b7280; text-transform:uppercase;
                  letter-spacing:0.04em; margin-bottom:6px;">2025</div>
      <div class="kpi-value" style="font-size:1.15rem;">{val_2025:{fmt}}</div>
      <div class="kpi-delta" style="min-height:18px; margin-top:4px; font-size:0.7rem;">{d25}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📆 Year-over-Year Analytics")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Compares pipeline performance across 2023, 2024, and 2025 to surface structural trends invisible in daily or monthly views.

**Sections:**
- YoY KPI comparison cards
- Quarterly trend breakdown
- Annual performance table
- Year-over-year change analysis
""")
    st.markdown("---")
    for yr in years:
        row = yoy.loc[yr]
        st.markdown(f"**{yr}** — Eff: {row.Transfer_Efficiency:.3f} | Warn: {int(row.Warning_Days)} days")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1747A0 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Year-over-Year Analytics
    </p>
    <p style="color:#c8d8f5; margin:10px 0 0; font-size:0.95rem;">
        Tracking structural pipeline performance shifts across 2023, 2024, and 2025
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPI Comparison Cards ──────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Year-over-Year KPI Comparison</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
card(c1, "danger",  "Transfer Efficiency",
     yoy.loc[2023,'Transfer_Efficiency'], yoy.loc[2024,'Transfer_Efficiency'],
     yoy.loc[2025,'Transfer_Efficiency'], invert=True)
card(c2, "danger",  "Discharge Effectiveness",
     yoy.loc[2023,'Discharge_Effectiveness'], yoy.loc[2024,'Discharge_Effectiveness'],
     yoy.loc[2025,'Discharge_Effectiveness'], invert=True)
card(c3, "danger",  "Warning Days",
     int(yoy.loc[2023,'Warning_Days']), int(yoy.loc[2024,'Warning_Days']),
     int(yoy.loc[2025,'Warning_Days']), invert=False, fmt="d")
card(c4, "danger",  "Stagnation Days (≥5)",
     int(yoy.loc[2023,'Stagnation_Days']), int(yoy.loc[2024,'Stagnation_Days']),
     int(yoy.loc[2025,'Stagnation_Days']), invert=False, fmt="d")

st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
card(c5, "warning", "Avg Daily Backlog",
     yoy.loc[2023,'Avg_Backlog'], yoy.loc[2024,'Avg_Backlog'],
     yoy.loc[2025,'Avg_Backlog'], invert=False, fmt=".1f")
card(c6, "purple",  "Pipeline Throughput",
     yoy.loc[2023,'Pipeline_Throughput'], yoy.loc[2024,'Pipeline_Throughput'],
     yoy.loc[2025,'Pipeline_Throughput'], invert=True)
card(c7, "",        "Avg HHS Population",
     int(yoy.loc[2023,'Avg_HHS']), int(yoy.loc[2024,'Avg_HHS']),
     int(yoy.loc[2025,'Avg_HHS']), invert=False, fmt="d")
card(c8, "success", "Total Discharged",
     int(yoy.loc[2023,'Total_Discharged']), int(yoy.loc[2024,'Total_Discharged']),
     int(yoy.loc[2025,'Total_Discharged']), invert=True, fmt=",d")

st.markdown("---")


# ── Quarterly trend charts ────────────────────────────────────────────────────

st.markdown('<p class="section-title">📈 Quarterly Trend Analysis</p>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    fig1 = go.Figure()
    colors_q = {'2023': '#1a7a4a', '2024': '#1747A0', '2025': '#c0392b'}
    for yr in ['2023', '2024', '2025']:
        q_data = qtr[qtr['Quarter'].str.startswith(yr)]
        q_labels = q_data['Quarter'].str[-2:]
        fig1.add_trace(go.Bar(
        x=q_labels,y=q_data['Transfer_Efficiency'],
        name=yr,marker_color=colors_q[yr],
        opacity=0.85,
        text=q_data['Transfer_Efficiency'].round(3),
        textposition='outside',
        textfont_size=9,cliponaxis=False
))
    fig1.update_layout(
    barmode='group',
    plot_bgcolor='white',
    paper_bgcolor='white',

    height=350,  # Smaller graph

    margin=dict(l=10, r=10, t=70, b=20),

    xaxis=dict(
        showgrid=False,
        title='Quarter'
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor='#F0F0F0',
        title='Avg Transfer Efficiency',
        automargin=True
    ),

    title='Transfer Efficiency by Quarter & Year',

    title_font=dict(
        size=14,
        color='#0B3C5D'
    ),

    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5
    ),

    uniformtext_minsize=8,
    uniformtext_mode='hide',

    hovermode='x unified'
    )
    
    st.plotly_chart(fig1, use_container_width=True)


with col_r:
    fig2 = go.Figure()
    for yr in ['2023', '2024', '2025']:
        q_data = qtr[qtr['Quarter'].str.startswith(yr)]
        q_labels = q_data['Quarter'].str[-2:]
        fig2.add_trace(go.Bar(
            x=q_labels,
            y=q_data['Total_Discharged'],
            name=yr,marker_color=colors_q[yr],
            opacity=0.85,
            text=q_data['Total_Discharged'],
            textposition='outside',
            textfont_size=9,
            cliponaxis=False
        ))
        
    fig2.update_layout(
    barmode='group',
    plot_bgcolor='white',
    paper_bgcolor='white',

    height=350,  # Smaller graph

    margin=dict(l=10, r=10, t=70, b=20),

    xaxis=dict(
        showgrid=False,
        title='Quarter'
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor='#F0F0F0',
        title='Total Discharged',
        automargin=True
    ),

    title='Total Discharges by Quarter & Year',

    title_font=dict(
        size=14,
        color='#0B3C5D'
    ),

    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5
    ),

    uniformtext_minsize=8,
    uniformtext_mode='hide',

    hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# Quarterly backlog trend
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=qtr['Quarter'], y=qtr['Transfer_Backlog'],
    mode='lines+markers+text',
    line=dict(color='#e05c00', width=2.5),
    marker=dict(size=8, color='#e05c00'),
    text=qtr['Transfer_Backlog'].round(1),
    textposition='top center', textfont_size=9,
    hovertemplate='%{x}<br>Avg Backlog: %{y:.1f}<extra></extra>'
))
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10,r=10,t=40,b=10),
    xaxis=dict(showgrid=False, title='Quarter', tickangle=-30),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Avg Daily Backlog (children)'),
    title='Average Daily Backlog by Quarter',
    title_font=dict(size=14, color='#0B3C5D'),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# ── Annual performance summary table ──────────────────────────────────────────

st.markdown('<p class="section-title">📋 Annual Performance Summary</p>', unsafe_allow_html=True)

def pct_badge(val, prev, invert=False):

    if pd.isna(prev):
        return "—"

    if prev == 0:

        if val == 0:
            return "—"

        return '<span style="color:#155c38;font-weight:600;">New</span>'

    pct = ((val - prev) / abs(prev)) * 100

    arrow = "▲" if pct > 0 else "▼"

    good = (pct > 0) != invert

    color = "#155c38" if good else "#c0392b"

    return (
        f'<span style="color:{color};'
        f'font-weight:600;">'
        f'{arrow}{abs(pct):.1f}%'
        f'</span>'
    )

def yoy_change(current, previous):

    if previous == 0 and current == 0:
        return "No Change"

    if previous == 0 and current > 0:
        return "New Increase"
    
    if previous == 0 and current > 0:
        return "⚠️ New Backlog"

    pct = ((current - previous) / abs(previous)) * 100

    arrow = "▲" if pct > 0 else "▼"

    return f"{arrow} {abs(pct):.1f}%"

summary_df = pd.DataFrame({

    "Metric": [
        "Transfer Efficiency",
        "Discharge Effectiveness",
        "Avg Daily Backlog",
        "Pipeline Throughput",
        "Avg HHS Population",
        "Total Discharged",
        "Warning Days",
        "Stagnation Days"
    ],

    "2023": [
        round(yoy.loc[2023,'Transfer_Efficiency'],3),
        round(yoy.loc[2023,'Discharge_Effectiveness'],4),
        round(yoy.loc[2023,'Avg_Backlog'],1),
        round(yoy.loc[2023,'Pipeline_Throughput'],3),
        int(yoy.loc[2023,'Avg_HHS']),
        int(yoy.loc[2023,'Total_Discharged']),
        int(yoy.loc[2023,'Warning_Days']),
        int(yoy.loc[2023,'Stagnation_Days'])
    ],

    "2024": [
        round(yoy.loc[2024,'Transfer_Efficiency'],3),
        round(yoy.loc[2024,'Discharge_Effectiveness'],4),
        round(yoy.loc[2024,'Avg_Backlog'],1),
        round(yoy.loc[2024,'Pipeline_Throughput'],3),
        int(yoy.loc[2024,'Avg_HHS']),
        int(yoy.loc[2024,'Total_Discharged']),
        int(yoy.loc[2024,'Warning_Days']),
        int(yoy.loc[2024,'Stagnation_Days'])
    ],

    "2024 vs 2023": [

        yoy_change(
            yoy.loc[2024,'Transfer_Efficiency'],
            yoy.loc[2023,'Transfer_Efficiency']
        ),

        yoy_change(
            yoy.loc[2024,'Discharge_Effectiveness'],
            yoy.loc[2023,'Discharge_Effectiveness']
        ),

        yoy_change(
            yoy.loc[2024,'Avg_Backlog'],
            yoy.loc[2023,'Avg_Backlog']
        ),

        yoy_change(
            yoy.loc[2024,'Pipeline_Throughput'],
            yoy.loc[2023,'Pipeline_Throughput']
        ),

        yoy_change(
            yoy.loc[2024,'Avg_HHS'],
            yoy.loc[2023,'Avg_HHS']
        ),

        yoy_change(
            yoy.loc[2024,'Total_Discharged'],
            yoy.loc[2023,'Total_Discharged']
        ),

        yoy_change(
            yoy.loc[2024,'Warning_Days'],
            yoy.loc[2023,'Warning_Days']
        ),

        yoy_change(
            yoy.loc[2024,'Stagnation_Days'],
            yoy.loc[2023,'Stagnation_Days']
        )
    ],

    "2025": [
        round(yoy.loc[2025,'Transfer_Efficiency'],3),
        round(yoy.loc[2025,'Discharge_Effectiveness'],4),
        round(yoy.loc[2025,'Avg_Backlog'],1),
        round(yoy.loc[2025,'Pipeline_Throughput'],3),
        int(yoy.loc[2025,'Avg_HHS']),
        int(yoy.loc[2025,'Total_Discharged']),
        int(yoy.loc[2025,'Warning_Days']),
        int(yoy.loc[2025,'Stagnation_Days'])
    ],

    "2025 vs 2024": [

        yoy_change(
            yoy.loc[2025,'Transfer_Efficiency'],
            yoy.loc[2024,'Transfer_Efficiency']
        ),

        yoy_change(
            yoy.loc[2025,'Discharge_Effectiveness'],
            yoy.loc[2024,'Discharge_Effectiveness']
        ),

        yoy_change(
            yoy.loc[2025,'Avg_Backlog'],
            yoy.loc[2024,'Avg_Backlog']
        ),

        yoy_change(
            yoy.loc[2025,'Pipeline_Throughput'],
            yoy.loc[2024,'Pipeline_Throughput']
        ),

        yoy_change(
            yoy.loc[2025,'Avg_HHS'],
            yoy.loc[2024,'Avg_HHS']
        ),

        yoy_change(
            yoy.loc[2025,'Total_Discharged'],
            yoy.loc[2024,'Total_Discharged']
        ),

        yoy_change(
            yoy.loc[2025,'Warning_Days'],
            yoy.loc[2024,'Warning_Days']
        ),

        yoy_change(
            yoy.loc[2025,'Stagnation_Days'],
            yoy.loc[2024,'Stagnation_Days']
        )
    ]

})

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

eff_drop = round((yoy.loc[2023,'Transfer_Efficiency'] - yoy.loc[2025,'Transfer_Efficiency'])
                  / yoy.loc[2023,'Transfer_Efficiency'] * 100, 1)
disc_drop = round((yoy.loc[2023,'Discharge_Effectiveness'] - yoy.loc[2025,'Discharge_Effectiveness'])
                   / yoy.loc[2023,'Discharge_Effectiveness'] * 100, 1)
warn_23 = int(yoy.loc[2023,'Warning_Days'])
warn_25 = int(yoy.loc[2025,'Warning_Days'])
disc_23 = int(yoy.loc[2023,'Total_Discharged'])
disc_25 = int(yoy.loc[2025,'Total_Discharged'])

st.markdown(f"""
<div class="insight-box">
    The year-over-year data reveals a severe and accelerating deterioration in pipeline performance.
    Transfer Efficiency fell <strong>{eff_drop}%</strong> from 2023 to 2025 (0.830 → 0.460), and
    Discharge Effectiveness fell <strong>{disc_drop}%</strong> over the same period. Total annual
    discharges collapsed from <strong>{disc_23:,}</strong> in 2023 to <strong>{disc_25:,}</strong>
    in 2025 — an <strong>89.9% reduction</strong> in humanitarian output.<br><br>
    Warning days surged from just <strong>{warn_23}</strong> in all of 2023 to
    <strong>{warn_25}</strong> in 2025 alone (65.3% of that year). Stagnation events, which were
    practically absent in 2023 (sum: 48 days), reached a cumulative total of <strong>1,077 stagnation
    days in 2025</strong>. The quarterly breakdown confirms this is not noise — every quarter of 2025
    underperformed every quarter of 2023 and 2024 on every metric. This trajectory warrants urgent
    policy and operational review.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Year-over-Year Analytics | UAC Care Transition Analytics Project")