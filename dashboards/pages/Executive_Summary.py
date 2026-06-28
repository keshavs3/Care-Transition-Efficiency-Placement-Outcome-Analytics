import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Executive Summary",
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

.objective-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    border-left: 4px solid #1a6fa8;
    margin-bottom: 10px;
    color: #0B3C5D;
    font-size: 0.95rem;
}

.finding-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    border-left: 4px solid #1a7a4a;
    margin-bottom: 10px;
    color: #1a3a2a;
    font-size: 0.93rem;
}

.rec-card {
    background: #f0faf4;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    border-left: 4px solid #f39c12;
    margin-bottom: 10px;
    color: #4a3800;
    font-size: 0.93rem;
}

.conclusion-box {
    background: linear-gradient(135deg, #e8f4fd 0%, #e8faf0 100%);
    border-radius: 14px;
    padding: 24px 28px;
    border: 1px solid #c8dff5;
    color: #0B3C5D;
    font-size: 0.97rem;
    line-height: 1.7;
}

</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "cleaned_uac.csv"

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year

total_discharged = f"{int(df['Children discharged from HHS Care'].sum()):,}"
avg_efficiency   = round(df['Transfer_Efficiency'].mean(), 2)
avg_discharge    = round(df['Discharge_Effectiveness'].mean(), 3)
warning_days     = len(df[df['Alert'] == 'Warning'])
avg_backlog      = round(df['Transfer_Backlog'].mean(), 1)

# YoY deltas: 2024 vs 2023, 2025 vs 2024
yoy = df.groupby('Year')[['Transfer_Efficiency','Discharge_Effectiveness',
                           'Transfer_Backlog']].mean()
warn_yr = df.groupby('Year')['Alert'].apply(lambda x: (x=='Warning').sum())

def delta_badge(new_v, old_v, invert=False):
    if old_v == 0: return ""
    pct = (new_v - old_v) / abs(old_v) * 100
    arrow = "▲" if pct > 0 else "▼"
    good = (pct > 0) != invert
    color = "#155c38" if good else "#c0392b"
    return f'<span style="font-size:0.68rem; font-weight:700; color:{color}; display:block; margin-top:3px;">{arrow} {abs(pct):.1f}% (\'24 vs \'23)</span>'

def delta_badge2(new_v, old_v, invert=False):
    if old_v == 0: return ""
    pct = (new_v - old_v) / abs(old_v) * 100
    arrow = "▲" if pct > 0 else "▼"
    good = (pct > 0) != invert
    color = "#155c38" if good else "#c0392b"
    return f'<span style="font-size:0.68rem; font-weight:700; color:{color}; display:block;">{arrow} {abs(pct):.1f}% (\'25 vs \'24)</span>'

d_eff_1  = delta_badge (yoy.loc[2024,'Transfer_Efficiency'],     yoy.loc[2023,'Transfer_Efficiency'],  True)
d_eff_2  = delta_badge2(yoy.loc[2025,'Transfer_Efficiency'],     yoy.loc[2024,'Transfer_Efficiency'],  True)
d_disc_1 = delta_badge (yoy.loc[2024,'Discharge_Effectiveness'], yoy.loc[2023,'Discharge_Effectiveness'], True)
d_disc_2 = delta_badge2(yoy.loc[2025,'Discharge_Effectiveness'], yoy.loc[2024,'Discharge_Effectiveness'], True)
d_warn_1 = delta_badge (warn_yr.get(2024,0), warn_yr.get(2023,0), False)
d_warn_2 = delta_badge2(warn_yr.get(2025,0), warn_yr.get(2024,0), False)
d_back_1 = delta_badge (yoy.loc[2024,'Transfer_Backlog'], yoy.loc[2023,'Transfer_Backlog'], False)
d_back_2 = delta_badge2(yoy.loc[2025,'Transfer_Backlog'], yoy.loc[2024,'Transfer_Backlog'], False)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Executive Summary")
    st.markdown("---")
    st.markdown("### 📌 Contents")
    st.markdown("""
- KPI Overview
- Project Objectives
- Key Findings
- Recommendations
- Conclusion
""")
    st.markdown("---")
    st.markdown("### 📅 Data Coverage")
    st.markdown(f"**From:** {df['Date'].min().strftime('%b %d, %Y')}")
    st.markdown(f"**To:** {df['Date'].max().strftime('%b %d, %Y')}")
    st.markdown(f"**Total Records:** {len(df):,}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1a5fa8 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Executive Summary
    </p>
    <p style="color:#c8dff5; margin:10px 0 0; font-size:0.95rem;">
        High-level overview of UAC care pipeline performance, findings, and recommendations
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Key Performance Indicators</p>', unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap;">

  <div class="kpi-card" style="flex:1; min-width:140px;">
    <div class="kpi-label">Total Discharges</div>
    <div class="kpi-value">{total_discharged}</div>
  </div>

  <div class="kpi-card success" style="flex:1; min-width:140px;">
    <div class="kpi-label">Avg Transfer Efficiency</div>
    <div class="kpi-value">{avg_efficiency}</div>
    {d_eff_1}{d_eff_2}
  </div>

  <div class="kpi-card success" style="flex:1; min-width:140px;">
    <div class="kpi-label">Avg Discharge Effectiveness</div>
    <div class="kpi-value">{avg_discharge}</div>
    {d_disc_1}{d_disc_2}
  </div>

  <div class="kpi-card warning" style="flex:1; min-width:140px;">
    <div class="kpi-label">Warning Days</div>
    <div class="kpi-value">{warning_days}</div>
    {d_warn_1}{d_warn_2}
  </div>

  <div class="kpi-card warning" style="flex:1; min-width:140px;">
    <div class="kpi-label">Avg Backlog</div>
    <div class="kpi-value">{avg_backlog}</div>
    {d_back_1}{d_back_2}
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ── Objectives + Findings side by side ───────────────────────────────────────

col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<p class="section-title">Project Objectives</p>', unsafe_allow_html=True)

    objectives = [
        ("1.", "Measure transfer efficiency from CBP to HHS custody."),
        ("2.", "Evaluate sponsor placement and discharge outcomes."),
        ("3.", "Identify operational bottlenecks and delay patterns."),
        ("4.", "Support data-driven policy-level decisions."),
        ("5.", "Improve reunification timelines for children."),
    ]
    for icon, text in objectives:
        st.markdown(f'<div class="objective-card">{icon} &nbsp; {text}</div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<p class="section-title">Key Findings</p>', unsafe_allow_html=True)

    findings = [
        ("1️.", "Transfer efficiency remained relatively stable across the observation period."),
        ("2️.", "Discharge performance showed limited variation, indicating consistent reunification."),
        ("3️.", f"A total of <strong>{warning_days}</strong> warning days flagged elevated operational pressure."),
        ("4️.", "Several backlog spikes were identified, particularly during peak intake periods."),
        ("5️.", "Outcome stability remained generally consistent despite occasional anomalies."),
    ]
    for icon, text in findings:
        st.markdown(f'<div class="finding-card">{icon} &nbsp; {text}</div>', unsafe_allow_html=True)

st.markdown("---")


# ── Recommendations ───────────────────────────────────────────────────────────

st.markdown('<p class="section-title">Recommendations</p>', unsafe_allow_html=True)

recs = [
    ("1.", "Monitor backlog growth regularly and set threshold-based alerts."),
    ("2.", "Reduce processing delays between CBP apprehension and HHS transfer."),
    ("3.", "Improve discharge throughput during high-intake periods."),
    ("4.", "Maintain placement outcome consistency through standardized workflows."),
    ("5.", "Use warning day alerts proactively to identify operational issues early."),
]

col1, col2 = st.columns(2)
for i, (icon, text) in enumerate(recs):
    with (col1 if i % 2 == 0 else col2):
        st.markdown(f'<div class="rec-card">{icon} &nbsp; {text}</div>', unsafe_allow_html=True)

st.markdown("---")


# ── Conclusion ────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">Overall Conclusion</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="conclusion-box">
    <strong>The UAC care pipeline demonstrated generally stable transfer and discharge performance</strong>
    over the observed period, with an average transfer efficiency of <strong>{avg_efficiency}</strong>
    and discharge effectiveness of <strong>{avg_discharge}</strong>.<br><br>
    However, <strong>{warning_days} warning days</strong> and recurring backlog spikes indicate
    clear opportunities for improving operational efficiency and reducing delays in the
    CBP → HHS → Sponsor placement pipeline.<br><br>
    Continued monitoring, proactive alerting, and targeted process improvements can support
    faster reunification outcomes for unaccompanied children.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Executive Summary | UAC Care Transition Analytics Project")


