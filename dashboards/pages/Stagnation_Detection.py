import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Stagnation Detection",
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
.kpi-card.danger  { border-top-color: #c0392b; }
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
.kpi-card.danger  .kpi-value { color: #c0392b; }
.kpi-card.warning .kpi-value { color: #c24f00; }

.insight-box {
    background: #fdf3f2;
    border-left: 5px solid #c0392b;
    border-radius: 10px;
    padding: 16px 20px;
    color: #6b1a1a;
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

stagnation_days = df[df['Stagnation_Period'] >= 5]
total_stag      = len(stagnation_days)
max_stag        = int(df['Stagnation_Period'].max())
avg_stag        = round(df['Stagnation_Period'].mean(), 1)
avg_eff_stag    = round(stagnation_days['Transfer_Efficiency'].mean(), 3) if total_stag > 0 else 'N/A'
pct_stag        = round((total_stag / len(df)) * 100, 1)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Stagnation Detection")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Identifies periods where transfer efficiency remained consistently low for 5+ consecutive days.

**Sections:**
- Stagnation KPIs
- Trend with highlighted zones
- Detected periods table
- Key insight
""")
    st.markdown("---")
    st.markdown(f"**Stagnation Days:** {total_stag:,}")
    st.markdown(f"**% of Total Days:** {pct_stag}%")
    st.markdown(f"**Longest Streak:** {max_stag} days")
    st.markdown(f"**Avg Efficiency (stag.):** {avg_eff_stag}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #6b1a1a 0%, #c0392b 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Stagnation Detection
    </p>
    <p style="color:#f5c6c6; margin:10px 0 0; font-size:0.95rem;">
        Identifying prolonged low-efficiency periods that signal operational bottlenecks
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">📊 Stagnation Summary</p>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

cards = [
    (k1, "danger",  "Stagnation Days",  f"{total_stag:,}"),
    (k2, "warning", "% of All Days",     f"{pct_stag}%"),
    (k3, "danger",  "Longest Streak",    f"{max_stag} days"),
    (k4, "",        "Avg Stagnation",    f"{avg_stag}"),
    (k5, "success", "Normal Days",        f"{len(df) - total_stag:,}"),
]

for col, cls, label, value in cards:
    with col:
        st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:110px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
</div>""", unsafe_allow_html=True)

st.markdown("---")


# ── Stagnation trend with highlighted zones ───────────────────────────────────

st.markdown('<p class="section-title">📈 Stagnation Trend with Alert Zones</p>', unsafe_allow_html=True)

fig1 = go.Figure()

# Highlight stagnation threshold
fig1.add_hline(
    y=5, line_dash='dash', line_color='#c0392b',
    annotation_text='Stagnation threshold (5 days)',
    annotation_position='top left'
)

# Normal zone shading
fig1.add_hrect(
    y0=0, y1=5,
    fillcolor='rgba(26,122,74,0.06)', line_width=0,
    annotation_text='Normal', annotation_position='top left'
)

# Stagnation zone shading
fig1.add_hrect(
    y0=5, y1=df['Stagnation_Period'].max() + 1,
    fillcolor='rgba(192,57,43,0.06)', line_width=0,
    annotation_text='Stagnation zone', annotation_position='top right'
)

# Main line
fig1.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Stagnation_Period'],
    line=dict(color='#0B3C5D', width=2),
    name='Stagnation Period',
    hovertemplate='%{x|%b %d, %Y}<br>Stagnation: %{y} days<extra></extra>'
))

# Highlight stagnation points in red
fig1.add_trace(go.Scatter(
    x=stagnation_days['Date'],
    y=stagnation_days['Stagnation_Period'],
    mode='markers',
    marker=dict(color='#c0392b', size=5, opacity=0.7),
    name='Stagnation Detected',
    hovertemplate='%{x|%b %d, %Y}<br>Stagnation: %{y} days<extra></extra>'
))

fig1.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Stagnation Period (days)'),
    title='Stagnation Period Over Time',
    title_font=dict(size=15, color='#0B3C5D'),
    hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")


# ── Transfer efficiency during stagnation ─────────────────────────────────────

st.markdown('<p class="section-title">Transfer Efficiency: Normal vs Stagnation Days</p>', unsafe_allow_html=True)

df['Status'] = df['Stagnation_Period'].apply(lambda x: '🔴 Stagnation' if x >= 5 else '🟢 Normal')

fig2 = px.box(
    df, x='Status', y='Transfer_Efficiency',
    color='Status',
    color_discrete_map={'🟢 Normal': '#1a7a4a', '🔴 Stagnation': '#c0392b'},
    title='Transfer Efficiency Distribution by Status'
)
fig2.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(title=''),
    yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Transfer Efficiency'),
    title_font=dict(size=15, color='#0B3C5D'),
    showlegend=False
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# ── Detected stagnation table ─────────────────────────────────────────────────

st.markdown('<p class="section-title">Detected Stagnation Periods</p>', unsafe_allow_html=True)

display_df = stagnation_days[['Date', 'Transfer_Efficiency', 'Stagnation_Period']].copy()
display_df['Date'] = display_df['Date'].dt.strftime('%b %d, %Y')
display_df.columns = ['Date', 'Transfer Efficiency', 'Stagnation Days']
display_df = display_df.sort_values('Stagnation Days', ascending=False).reset_index(drop=True)
display_df.index += 1
st.dataframe(display_df, use_container_width=True, height=300)

st.markdown("---")


# ── Key insight ───────────────────────────────────────────────────────────────

st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
    <strong>{total_stag:,} stagnation days</strong> were detected ({pct_stag}% of the full observation period),
    with the longest streak reaching <strong>{max_stag} consecutive days</strong>.<br><br>
    Stagnation periods occur when transfer efficiency remains consistently low for 5+ days,
    indicating operational bottlenecks, resource constraints, or delays in moving children
    from CBP custody into HHS care.<br><br>
    Identifying and intervening during these periods can significantly improve reunification
    timelines and reduce system-wide care load.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Stagnation Detection | UAC Care Transition Analytics Project")