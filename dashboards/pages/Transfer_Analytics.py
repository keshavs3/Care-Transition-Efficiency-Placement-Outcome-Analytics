import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Transfer Analytics",
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

/* ── Tab styling ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0px;
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 20px;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 8px 22px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #6b7280;
    background: transparent;
    border: none;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: #1747A0 !important;
    color: #ffffff !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #1747A0;
    background: #EAF2FD;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "cleaned_uac.csv"

df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').astype(str)

monthly_transfer = df.groupby('Month')['Transfer_Efficiency'].mean().reset_index()
monthly_transfer.columns = ['Month', 'Avg_Efficiency']

avg_transfer  = round(df['Transfer_Efficiency'].mean(), 2)
max_transfer  = round(df['Transfer_Efficiency'].max(), 2)
min_transfer  = round(df['Transfer_Efficiency'].min(), 2)
std_transfer  = round(df['Transfer_Efficiency'].std(), 3)
best_month    = monthly_transfer.loc[monthly_transfer['Avg_Efficiency'].idxmax(), 'Month']

ratio_clean  = df['Transfer_to_Discharge_Ratio'].dropna()
median_ratio = round(ratio_clean.median(), 2)
mean_ratio   = round(ratio_clean.mean(), 2)
above_1_pct  = round((ratio_clean > 1).mean() * 100, 1)

roll_mean = df['Rolling_Transfer_Efficiency'].mean()
roll_std  = df['Rolling_Transfer_Efficiency'].std()
roll_max  = round(df['Rolling_Transfer_Efficiency'].max(), 3)
roll_min  = round(df['Rolling_Transfer_Efficiency'].min(), 3)

stability = "low" if std_transfer < 0.1 else "moderate" if std_transfer < 0.3 else "high"


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Transfer Analytics")
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown("""
Measures how effectively children move from CBP custody into HHS care over time.

**Tabs:**
- 📈 Trend — Efficiency over time
- 📅 Monthly — Monthly breakdown
- 🔁 Ratio — Transfer-to-Discharge
- 〰️ Rolling — Smoothed trend
""")
    st.markdown("---")
    st.markdown(f"**Avg Efficiency:** {avg_transfer}")
    st.markdown(f"**Peak:** {max_transfer}")
    st.markdown(f"**Lowest:** {min_transfer}")
    st.markdown(f"**Best Month:** {best_month}")
    st.markdown(f"**Variability:** {stability}")


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background: linear-gradient(90deg, #0B3C5D 0%, #1747A0 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <p style="color:#ffffff; margin:0; font-size:1.7rem; font-weight:800; line-height:1.2;">
    Transfer Analytics
    </p>
    <p style="color:#c8d8f5; margin:10px 0 0; font-size:0.95rem;">
        Evaluating how efficiently children transition from CBP custody into HHS care
    </p>
</div>
""", unsafe_allow_html=True)


# ── KPI row (always visible above tabs) ──────────────────────────────────────

st.markdown('<p class="section-title">📊 Transfer Efficiency Summary</p>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
cards = [
    (k1, "blue",    "Avg Efficiency",  f"{avg_transfer}"),
    (k2, "success", "Peak Efficiency", f"{max_transfer}"),
    (k3, "warning", "Lowest",          f"{min_transfer}"),
    (k4, "blue",    "Std Deviation",   f"{std_transfer}"),
    (k5, "success", "Best Month",      best_month),
]
for col, cls, label, value in cards:
    with col:
        st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:110px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="font-size:{'1.1rem' if len(str(value)) > 6 else '1.75rem'};">{value}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "Trend",
    "Monthly",
    "Transfer-to-Discharge Ratio",
    "Rolling Efficiency",
])


# ── Tab 1: Trend ──────────────────────────────────────────────────────────────

with tab1:
    st.markdown('<p class="section-title">📈 Transfer Efficiency Trend</p>', unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_hrect(
        y0=avg_transfer * 0.95, y1=avg_transfer * 1.05,
        fillcolor='rgba(23,71,160,0.07)', line_width=0,
        annotation_text='Avg band', annotation_position='top left'
    )
    fig1.add_hline(
        y=avg_transfer, line_dash='dash', line_color='#e05c00',
        annotation_text=f'Mean: {avg_transfer}', annotation_position='bottom right'
    )
    fig1.add_trace(go.Scatter(
        x=df['Date'], y=df['Transfer_Efficiency'],
        line=dict(color='#1747A0', width=2),
        name='Transfer Efficiency',
        hovertemplate='%{x|%b %d, %Y}<br>Efficiency: %{y:.3f}<extra></extra>'
    ))
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Transfer Efficiency'),
        title='Transfer Efficiency Over Time',
        title_font=dict(size=15, color='#0B3C5D'),
        hovermode='x unified', showlegend=False
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown('<p class="section-title">📊 Frequency Distribution</p>', unsafe_allow_html=True)
    fig_hist = px.histogram(
        df, x='Transfer_Efficiency', nbins=20,
        title='Transfer Efficiency Frequency Distribution',
        color_discrete_sequence=['#1747A0']
    )
    fig_hist.update_traces(marker_line_color='#66B8F3', marker_line_width=1.5, opacity=0.75)
    fig_hist.add_vline(
        x=avg_transfer, line_dash='dash', line_color='#e05c00',
        annotation_text=f'Mean: {avg_transfer}', annotation_position='top right'
    )
    fig_hist.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title='Transfer Efficiency'),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Count'),
        title_font=dict(size=15, color='#0B3C5D'),
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    
    # ── Key insight ───────────────────────────────────────────────────────────────

    st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

    st.write("""
<div class="insight-box">
    Transfer Efficiency declined from 0.83 (2023) to 0.46 (2025).2023 recorded the strongest transition performance across the study period.<br>
    A moderate decline was observed in 2024, followed by a significant deterioration in 2025.<br><br>
    Reduced transfer efficiency may indicate operational bottlenecks between CBP and HHS.<br>
    Lower efficiency increases the risk of backlog accumulation and delayed care transitions.<br>
    Process optimization and improved coordination are recommended to restore transition speed.<br><br>
    The histogram shows how frequently different transfer efficiency levels occurred throughout the study period.

</div>
""", unsafe_allow_html=True)

# ── Tab 2: Monthly ────────────────────────────────────────────────────────────

with tab2:
    st.markdown('<p class="section-title">📅 Monthly Breakdown & Distribution</p>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        fig2 = px.bar(
            monthly_transfer, x='Month', y='Avg_Efficiency',
            title='Monthly Avg Transfer Efficiency',
            color='Avg_Efficiency',
            color_continuous_scale=['#D6EAF8', '#1747A0', '#0B3C5D']
        )
        fig2.add_hline(
            y=avg_transfer, line_dash='dash', line_color='#e05c00',
            annotation_text='Overall avg', annotation_position='top left'
        )
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=60),
            xaxis=dict(showgrid=False, tickangle=-45, title='Month'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Avg Efficiency'),
            coloraxis_showscale=False,
            title_font=dict(size=15, color='#0B3C5D'),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        fig3 = px.box(
            df, y='Transfer_Efficiency',
            title='Efficiency Spread & Outliers',
            color_discrete_sequence=['#1747A0']
        )
        fig3.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Transfer Efficiency'),
            title_font=dict(size=15, color='#0B3C5D'),
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    
    st.markdown("---")
    
    # ── Key insight ───────────────────────────────────────────────────────────────

    st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)

    st.write("""
<div class="insight-box">
    Median Transfer Efficiency was 0.70, indicating that half of the months performed above this level.<br><br>
    The highest monthly Transfer Efficiency reached 2.30, representing exceptionally fast transitions during peak-performing periods.<br>
    The lowest monthly Transfer Efficiency was 0.00, indicating months where transfers were severely delayed or absent.<br><br>
    50% of monthly observations fell between 0.50 and 0.85, showing the typical operating range of the system.<br><br>
    Transfer Efficiency varied considerably across months, indicating fluctuations in the speed of CBP-to-HHS transitions.
    The distribution pattern helps identify whether efficiency issues were isolated events or part of a recurring trend.<br><br>
    The box plot highlights the median efficiency level and identifies potential outlier months.
    Outlier months may represent unusual operational conditions, sudden surges in intake volume, or exceptional transfer performance.
</div>
""", unsafe_allow_html=True)


# ── Tab 3: Transfer-to-Discharge Ratio ───────────────────────────────────────

with tab3:
    st.markdown('<p class="section-title">🔁 Transfer-to-Discharge Ratio</p>', unsafe_allow_html=True)

    tr1, tr2, tr3 = st.columns(3)
    for col, label, val, cls in [
        (tr1, "Median Ratio",        f"{median_ratio}", "blue"),
        (tr2, "Mean Ratio",           f"{mean_ratio}",   "blue"),
        (tr3, "Days Ratio > 1.0",    f"{above_1_pct}%", "warning"),
    ]:
        with col:
            st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:90px; margin-bottom:16px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
</div>""", unsafe_allow_html=True)

    col_r1, col_r2 = st.columns([3, 2])

    with col_r1:
        fig5 = go.Figure()
        fig5.add_hline(
            y=1.0, line_dash='dash', line_color='#1a7a4a',
            annotation_text='Balanced (1.0)', annotation_position='top left'
        )
        fig5.add_trace(go.Scatter(
            x=df['Date'], y=df['Transfer_to_Discharge_Ratio'],
            line=dict(color='#1747A0', width=1.5),
            name='Transfer-to-Discharge Ratio',
            hovertemplate='%{x|%b %d, %Y}<br>Ratio: %{y:.2f}<extra></extra>'
        ))
        fig5.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0',
                       title='Transfers ÷ Discharges',
                       range=[0, ratio_clean.quantile(0.98)]),
            title='Transfer-to-Discharge Ratio Over Time',
            title_font=dict(size=15, color='#0B3C5D'),
            hovermode='x unified', showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_r2:
        fig6 = px.box(
            ratio_clean.to_frame(), y='Transfer_to_Discharge_Ratio',
            title='Ratio Spread & Outliers',
            color_discrete_sequence=['#1747A0']
        )
        fig6.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Ratio',
                       range=[0, ratio_clean.quantile(0.98)]),
            title_font=dict(size=15, color='#0B3C5D'),
        )
        st.plotly_chart(fig6, use_container_width=True)
        
    st.markdown("---")
    
    # ── Key insight ───────────────────────────────────────────────────────────────

    st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)


    st.markdown(f"""
<div class="insight-box">
    The Transfer-to-Discharge Ratio compares how many children are transferred into HHS care
    against how many are discharged on the same day. The median ratio was <strong>{median_ratio}</strong>
    (mean: <strong>{mean_ratio}</strong>, skewed by occasional spikes), and transfers exceeded
    discharges on <strong>{above_1_pct}%</strong> of days.<br><br>
    A ratio above 1.0 means more children entered HHS care than left it that day — sustained periods
    above 1.0 contribute directly to backlog growth, while a ratio near or below 1.0 indicates the
    system is keeping pace with incoming transfers.
</div>
""", unsafe_allow_html=True)


# ── Tab 4: Rolling ────────────────────────────────────────────────────────────

with tab4:
    st.markdown('<p class="section-title">〰️ Rolling Transfer Efficiency & Stability Band</p>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    for col, label, val, cls in [
        (r1, "Rolling Mean",   f"{roll_mean:.3f}", "blue"),
        (r2, "Rolling Std Dev", f"{roll_std:.3f}",  "blue"),
        (r3, "🔺 Rolling Peak",    f"{roll_max}",      "success"),
        (r4, "🔻 Rolling Low",     f"{roll_min}",      "warning"),
    ]:
        with col:
            st.markdown(f"""
<div class="kpi-card {cls}" style="min-height:90px; margin-bottom:16px;">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
</div>""", unsafe_allow_html=True)

    col_roll1, col_roll2 = st.columns([3, 2])

    with col_roll1:
        fig_r1 = go.Figure()
        band_x = pd.concat([df['Date'], df['Date'][::-1]])
        band_y = pd.concat([
            pd.Series([roll_mean + roll_std] * len(df)),
            pd.Series([roll_mean - roll_std] * len(df[::-1]))
        ])
        fig_r1.add_trace(go.Scatter(
            x=band_x, y=band_y,
            fill='toself', fillcolor='rgba(23,71,160,0.08)',
            line=dict(color='rgba(0,0,0,0)'),
            name='±1 SD Band', hoverinfo='skip'
        ))
        fig_r1.add_hline(
            y=roll_mean, line_dash='dash', line_color='#e05c00',
            annotation_text=f'Rolling Mean: {roll_mean:.3f}',
            annotation_position='top left'
        )
        fig_r1.add_trace(go.Scatter(
            x=df['Date'], y=df['Rolling_Transfer_Efficiency'],
            line=dict(color='#1747A0', width=2),
            name='Rolling Transfer Efficiency',
            hovertemplate='%{x|%b %d, %Y}<br>Value: %{y:.3f}<extra></extra>'
        ))
        fig_r1.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Rolling Transfer Efficiency'),
            title='Rolling Transfer Efficiency with Stability Band',
            title_font=dict(size=14, color='#0B3C5D'),
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=0.97, xanchor='right', x=0.92)
        )
        st.plotly_chart(fig_r1, use_container_width=True)

    with col_roll2:
        fig_r2 = go.Figure()
        fig_r2.add_trace(go.Scatter(
            x=df['Date'], y=df['Transfer_Efficiency'],
            line=dict(color='#D6EAF8', width=1),
            name='Raw Efficiency', opacity=0.6,
            hovertemplate='Raw: %{y:.3f}<extra></extra>'
        ))
        fig_r2.add_trace(go.Scatter(
            x=df['Date'], y=df['Rolling_Transfer_Efficiency'],
            line=dict(color='#1747A0', width=2),
            name='Rolling Efficiency',
            hovertemplate='Rolling: %{y:.3f}<extra></extra>'
        ))
        fig_r2.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0', title='Transfer Efficiency'),
            title='Raw vs Rolling Transfer Efficiency',
            title_font=dict(size=14, color='#0B3C5D'),
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=0.97, xanchor='right', x=0.92)
        )
        st.plotly_chart(fig_r2, use_container_width=True)
        
    st.markdown("---")
    
    # ── Key insight ───────────────────────────────────────────────────────────────

    st.markdown('<p class="section-title">💡 Key Insight</p>', unsafe_allow_html=True)


    st.markdown(f"""
<div class="insight-box">
    Transfer Efficiency averaged <strong>{avg_transfer}</strong> across the full period,
    ranging from <strong>{min_transfer}</strong> to <strong>{max_transfer}</strong>
    (std dev: <strong>{std_transfer}</strong> — <strong>{stability} variability</strong>),
    with the best performing month being <strong>{best_month}</strong>.<br><br>
    The Rolling Transfer Efficiency (smoothed trend) ranged from <strong>{roll_min}</strong>
    to <strong>{roll_max}</strong> with a mean of <strong>{roll_mean:.3f}</strong>.
    The shaded ±1 SD stability band highlights periods where the smoothed signal deviated
    from its long-run average — sustained periods below the band are early indicators of
    systemic CBP → HHS transfer slowdowns, distinct from day-level noise in the raw series.
</div>
""", unsafe_allow_html=True)


st.markdown("---")
st.caption("Transfer Analytics | UAC Care Transition Analytics Project")