"""
====================================================================
GOALKEEPER WORLD ANALYSIS — Streamlit Interactive Dashboard
====================================================================
Built with Streamlit — a Python library that turns scripts into
professional web applications instantly.

How to run:
  streamlit run dashboard/app.py

Sections:
  1. Home         — rankings overview
  2. Top 5        — detailed GK profiles with radar charts
  3. Compare      — pick any 2 GKs and compare metrics
  4. Competition  — UCL vs League performance heatmap
  5. Methodology  — full explanation for interviews
====================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Top 5 Goalkeeper World Analysis",
    page_icon="🧤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS: dark premium theme ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #111827 100%);
    border-right: 1px solid #1e3a5f;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d2137 0%, #0f2940 100%);
    border: 1px solid #1e4976;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 20px rgba(0, 120, 255, 0.1);
}

/* Headers */
h1, h2, h3 {
    color: #e8f4fd !important;
}

/* Gold badge */
.rank-badge-1 { color: #FFD700; font-size: 2.4rem; font-weight: 800; }
.rank-badge-2 { color: #C0C0C0; font-size: 2.4rem; font-weight: 800; }
.rank-badge-3 { color: #CD7F32; font-size: 2.4rem; font-weight: 800; }
.rank-badge-4 { color: #60a5fa; font-size: 2.4rem; font-weight: 800; }
.rank-badge-5 { color: #60a5fa; font-size: 2.4rem; font-weight: 800; }

/* GK card */
.gk-card {
    background: linear-gradient(135deg, #0d2137 0%, #0f2940 100%);
    border: 1px solid #1e4976;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0, 120, 255, 0.15);
    transition: transform 0.2s;
}

/* Score bar */
.score-bar {
    background: linear-gradient(90deg, #1e4976 0%, #2563eb 100%);
    height: 8px;
    border-radius: 4px;
}

/* Insight box */
.insight-box {
    background: rgba(37, 99, 235, 0.1);
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 12px;
    color: #bfdbfe;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* Table styling */
.styled-table th {
    background-color: #0d2137 !important;
    color: #60a5fa !important;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #1e3a5f;
    margin: 24px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent.parent / "data" / "processed"
    df = pd.read_csv(base / "gk_ranked.csv")
    return df

df = load_data()
top5 = df.head(5).reset_index(drop=True)

# ── Sidebar navigation ──────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center; padding: 20px 0 10px;">
    <div style="font-size: 3rem;">🧤</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: #60a5fa;">GK World Analysis</div>
    <div style="font-size: 0.75rem; color: #6b7280;">5 Seasons | 16 GKs | 7 Metrics</div>
</div>
<hr style="border-color: #1e3a5f; margin: 0 0 16px;">
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["🏆 World Rankings", "⭐ Top 5 Profiles", "⚖️ GK Comparison", "🌍 Competition Analysis", "📚 Methodology"],
    label_visibility="collapsed"
)

st.sidebar.markdown("""
<hr style="border-color: #1e3a5f; margin: 16px 0;">
<div style="font-size: 0.75rem; color: #6b7280; padding: 8px 0;">
    <b style="color: #60a5fa;">Data Sources</b><br>
    FBref.com · Transfermarkt<br>
    Seasons: 2019-20 → 2023-24<br>
    Leagues: PL · La Liga · Serie A<br>
    Bundesliga · Ligue 1 · UCL
</div>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────
NATION_FLAGS = {
    "BRA": "🇧🇷", "BEL": "🇧🇪", "SVN": "🇸🇮", "FRA": "🇫🇷",
    "GER": "🇩🇪", "ITA": "🇮🇹", "ESP": "🇪🇸", "CMR": "🇨🇲",
    "SUI": "🇨🇭", "POL": "🇵🇱",
}

RANK_COLORS = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32", 4: "#60a5fa", 5: "#60a5fa"}
RING_COLORS = ["#FFD700","#C0C0C0","#CD7F32","#60a5fa","#818cf8"]

RADAR_METRICS = ["save_pct","clean_sheet_pct","psxg_diff","ucl_save_pct","penalty_save_pct","pass_completion_pct"]
RADAR_LABELS  = ["Save %","CS Rate","PSxG Diff","UCL Save %","Pen Save %","Distribution"]

def radar_chart(players_df, title=""):
    """Build a beautiful radar chart for selected goalkeepers."""
    fig = go.Figure()

    # Normalize to 0-100 for display
    norm_df = players_df.copy()
    for col in RADAR_METRICS:
        mn, mx = df[col].min(), df[col].max()
        if mx > mn:
            norm_df[col] = (players_df[col] - mn) / (mx - mn) * 100
        else:
            norm_df[col] = 50

    # Map hex colors to rgba fill equivalents
    FILL_COLORS = [
        "rgba(255,215,0,0.15)",
        "rgba(192,192,192,0.15)",
        "rgba(205,127,50,0.15)",
        "rgba(96,165,250,0.15)",
        "rgba(129,140,248,0.15)",
    ]

    for i, (_, row) in enumerate(players_df.iterrows()):
        color     = RING_COLORS[i % len(RING_COLORS)]
        fillcolor = FILL_COLORS[i % len(FILL_COLORS)]
        vals  = [norm_df.loc[row.name, m] for m in RADAR_METRICS]
        vals.append(vals[0])  # close the polygon

        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=RADAR_LABELS + [RADAR_LABELS[0]],
            fill="toself",
            name=row["player"],
            line=dict(color=color, width=2),
            fillcolor=fillcolor,
            opacity=0.85,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(13,33,55,0.5)",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#6b7280", size=9), gridcolor="#1e3a5f"),
            angularaxis=dict(tickfont=dict(color="#9ca3af", size=11), gridcolor="#1e3a5f", linecolor="#1e3a5f"),
        ),
        showlegend=True,
        legend=dict(font=dict(color="#d1d5db"), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text=title, font=dict(color="#e8f4fd", size=14)),
        margin=dict(l=40, r=40, t=60, b=40),
        height=420,
    )
    return fig


# ══════════════════════════════════════════════════════════════════
# PAGE 1: WORLD RANKINGS
# ══════════════════════════════════════════════════════════════════
if page == "🏆 World Rankings":

    st.markdown("""
    <h1 style="text-align:center; font-size:2.4rem; background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom:4px;">
    🧤 Top 5 Goalkeepers in the World
    </h1>
    <p style="text-align:center; color:#6b7280; font-size:1rem; margin-bottom:32px;">
    Based on 5 seasons of data (2019–2024) · Big 5 Leagues + Champions League · 7 Advanced Metrics
    </p>
    """, unsafe_allow_html=True)

    # ── Top 5 podium cards ─────────────────────────────────────────
    cols = st.columns(5)
    for i, row in top5.iterrows():
        rank = i + 1
        color = RANK_COLORS[rank]
        flag  = NATION_FLAGS.get(row["nation"], "🏳️")
        score = row["composite_score"]
        bar_w = int(score)

        with cols[i]:
            st.markdown(f"""
            <div class="gk-card" style="border-color:{color}44; text-align:center;">
                <div style="font-size:2rem; font-weight:800; color:{color};">#{rank}</div>
                <div style="font-size:1.0rem; font-weight:700; color:#e8f4fd; margin:6px 0;">{row['player']}</div>
                <div style="font-size:0.8rem; color:#6b7280; margin-bottom:10px;">{flag} {row['squad']}</div>
                <div style="font-size:1.8rem; font-weight:800; color:{color};">{score:.1f}</div>
                <div style="font-size:0.72rem; color:#6b7280; margin-bottom:10px;">Composite Score</div>
                <div style="background:#0a1929; border-radius:4px; height:6px; margin-bottom:14px;">
                    <div style="background:{color}; width:{bar_w}%; height:100%; border-radius:4px;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.75rem;">
                    <span style="color:#9ca3af;">Save%<br><b style="color:#e8f4fd;">{row['save_pct']:.1f}%</b></span>
                    <span style="color:#9ca3af;">CS%<br><b style="color:#e8f4fd;">{row['clean_sheet_pct']:.1f}%</b></span>
                    <span style="color:#9ca3af;">PSxG<br><b style="color:#e8f4fd;">+{row['psxg_diff']:.1f}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Full rankings table ────────────────────────────────────────
    st.markdown("### 📊 Full Goalkeeper Rankings")

    display = df[["rank","player","squad","nation",
                  "composite_score","save_pct","clean_sheet_pct",
                  "goals_per_game","psxg_diff","ucl_save_pct","matches_played"]].copy()
    display.columns = ["Rank","Player","Club","Nation",
                       "Score","Save %","CS %","GA/Game","PSxG+/-","UCL Save %","Matches"]
    display["Nation"] = display["Nation"].map(lambda n: NATION_FLAGS.get(n,"") + " " + n)
    display["Score"]  = display["Score"].round(1)
    display["Save %"] = display["Save %"].round(1)
    display["CS %"]   = display["CS %"].round(1)
    display["GA/Game"]= display["GA/Game"].round(2)
    display["PSxG+/-"]= display["PSxG+/-"].round(2)
    display["UCL Save %"] = display["UCL Save %"].round(1)
    display = display.set_index("Rank")

    st.dataframe(
        display.style
            .background_gradient(subset=["Score"], cmap="Blues")
            .background_gradient(subset=["Save %"], cmap="Greens")
            .background_gradient(subset=["PSxG+/-"], cmap="Purples")
            .format({"GA/Game": "{:.2f}"}),
        use_container_width=True,
        height=480,
    )

    # ── Bar chart ──────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📈 Composite Score Comparison — All Goalkeepers")

    bar_df = df.sort_values("composite_score", ascending=True)
    colors_bar = ["#FFD700" if r == 1 else "#C0C0C0" if r == 2 else "#CD7F32" if r == 3 else "#2563eb" for r in bar_df["rank"]]

    fig_bar = go.Figure(go.Bar(
        x=bar_df["composite_score"],
        y=bar_df["player"],
        orientation="h",
        marker=dict(color=colors_bar, line=dict(color="rgba(0,0,0,0)", width=0)),
        text=bar_df["composite_score"].round(1),
        textposition="outside",
        textfont=dict(color="#d1d5db", size=11),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.5)",
        xaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#6b7280"), title=""),
        yaxis=dict(tickfont=dict(color="#e8f4fd", size=11)),
        margin=dict(l=10, r=80, t=20, b=20),
        height=520,
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 2: TOP 5 PROFILES
# ══════════════════════════════════════════════════════════════════
elif page == "⭐ Top 5 Profiles":

    st.markdown("""
    <h1 style="font-size:2rem; background: linear-gradient(90deg, #FFD700, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    ⭐ Top 5 Goalkeeper World Profiles
    </h1>
    <p style="color:#6b7280; margin-bottom:24px;">Deep-dive analysis into every elite goalkeeper's strengths, weaknesses, and big-match record.</p>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "Select Goalkeeper",
        top5["player"].tolist(),
        format_func=lambda n: f"#{top5[top5['player']==n].index[0]+1}  {n}"
    )

    row = top5[top5["player"] == selected].iloc[0]
    rank = int(row["rank"])
    color = RANK_COLORS[rank]
    flag  = NATION_FLAGS.get(row["nation"], "🏳️")

    # Header
    col_l, col_r = st.columns([1.2, 2])
    with col_l:
        st.markdown(f"""
        <div class="gk-card" style="border-color:{color}; text-align:center; padding:32px 24px;">
            <div style="font-size:3.5rem; font-weight:900; color:{color};">#{rank}</div>
            <div style="font-size:1.4rem; font-weight:700; color:#e8f4fd; margin:8px 0;">{row['player']}</div>
            <div style="font-size:1.0rem; color:#9ca3af;">{flag} {row['squad']}</div>
            <div style="margin:20px 0;">
                <div style="font-size:3rem; font-weight:800; color:{color};">{row['composite_score']:.1f}</div>
                <div style="font-size:0.8rem; color:#6b7280;">out of 100</div>
                <div style="background:#0a1929; border-radius:6px; height:10px; margin:12px 0;">
                    <div style="background:linear-gradient(90deg,{color},{color}88); width:{int(row['composite_score'])}%; height:100%; border-radius:6px;"></div>
                </div>
            </div>
            <div style="font-size:0.85rem; color:#9ca3af;">{int(row['matches_played'])} Matches · {int(row['seasons_played'])} Seasons</div>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics
        st.markdown("**Key Stats**")
        metrics_to_show = [
            ("Save %",      f"{row['save_pct']:.1f}%"),
            ("Clean Sheet %", f"{row['clean_sheet_pct']:.1f}%"),
            ("Goals/Game",  f"{row['goals_per_game']:.2f}"),
            ("PSxG Diff",   f"+{row['psxg_diff']:.2f}"),
            ("UCL Save %",  f"{row['ucl_save_pct']:.1f}%"),
            ("Pen Save %",  f"{row['penalty_save_pct']:.1f}%"),
            ("Distribution",f"{row['pass_completion_pct']:.1f}%"),
        ]
        for label, val in metrics_to_show:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:6px 0; 
                        border-bottom:1px solid #1e3a5f; font-size:0.85rem;">
                <span style="color:#9ca3af;">{label}</span>
                <span style="color:#e8f4fd; font-weight:600;">{val}</span>
            </div>""", unsafe_allow_html=True)

    with col_r:
        # Radar chart
        st.plotly_chart(
            radar_chart(top5[top5["player"] == selected].reset_index(), f"Performance Radar — {row['player']}"),
            use_container_width=True
        )

        # Insight box
        st.markdown(f"""
        <div class="insight-box">
            <b style="color:#60a5fa;">📊 Analyst Insight</b><br><br>
            {row['insight']}
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # All 5 radar overlay
    st.markdown("### 🕸️ All Top 5 — Radar Overlay")
    st.plotly_chart(radar_chart(top5.reset_index(), "Top 5 Goalkeepers — Profile Comparison"), use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 3: COMPARISON
# ══════════════════════════════════════════════════════════════════
elif page == "⚖️ GK Comparison":

    st.markdown("""
    <h1 style="font-size:2rem; color:#e8f4fd;">⚖️ Head-to-Head Goalkeeper Comparison</h1>
    <p style="color:#6b7280; margin-bottom:24px;">Compare any two goalkeepers across all 7 metrics side by side.</p>
    """, unsafe_allow_html=True)

    all_gks = df["player"].tolist()
    col1, col2 = st.columns(2)
    with col1:
        gk1 = st.selectbox("Goalkeeper A", all_gks, index=0, key="gk1")
    with col2:
        gk2 = st.selectbox("Goalkeeper B", all_gks, index=1, key="gk2")

    r1 = df[df["player"] == gk1].iloc[0]
    r2 = df[df["player"] == gk2].iloc[0]

    # Radar comparison
    compare_df = df[df["player"].isin([gk1, gk2])].reset_index()
    st.plotly_chart(radar_chart(compare_df, f"{gk1} vs {gk2}"), use_container_width=True)

    # Metric comparison table
    st.markdown("### 📋 Metric-by-Metric Breakdown")
    metrics = [
        ("Composite Score", "composite_score", False),
        ("Save %",          "save_pct",         False),
        ("Clean Sheet %",   "clean_sheet_pct",  False),
        ("Goals/Game",      "goals_per_game",   True),   # lower is better
        ("PSxG Diff",       "psxg_diff",        False),
        ("UCL Save %",      "ucl_save_pct",     False),
        ("Penalty Save %",  "penalty_save_pct", False),
        ("Distribution %",  "pass_completion_pct", False),
        ("UCL Matches",     "ucl_matches",      False),
        ("Total Matches",   "matches_played",   False),
    ]

    rows_html = ""
    for label, col, lower_better in metrics:
        v1 = r1[col]
        v2 = r2[col]
        if lower_better:
            w1 = "color:#4ade80; font-weight:700;" if v1 < v2 else ("color:#f87171;" if v1 > v2 else "")
            w2 = "color:#4ade80; font-weight:700;" if v2 < v1 else ("color:#f87171;" if v2 > v1 else "")
        else:
            w1 = "color:#4ade80; font-weight:700;" if v1 > v2 else ("color:#f87171;" if v1 < v2 else "")
            w2 = "color:#4ade80; font-weight:700;" if v2 > v1 else ("color:#f87171;" if v2 < v1 else "")
        rows_html += f"""
        <tr style="border-bottom:1px solid #1e3a5f;">
            <td style="{w1} padding:10px 16px; text-align:right;">{v1:.1f}</td>
            <td style="color:#6b7280; text-align:center; padding:10px 8px; font-size:0.85rem;">{label}</td>
            <td style="{w2} padding:10px 16px; text-align:left;">{v2:.1f}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; background:rgba(13,33,55,0.5); border-radius:12px; overflow:hidden;">
        <thead>
            <tr style="background:#0d2137;">
                <th style="color:#60a5fa; padding:14px 16px; text-align:right; font-size:1rem;">{gk1}</th>
                <th style="color:#6b7280; text-align:center; font-size:0.8rem;">METRIC</th>
                <th style="color:#60a5fa; padding:14px 16px; text-align:left; font-size:1rem;">{gk2}</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    <p style="color:#6b7280; font-size:0.75rem; margin-top:8px;">🟢 Green = better value on that metric</p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 4: COMPETITION ANALYSIS
# ══════════════════════════════════════════════════════════════════
elif page == "🌍 Competition Analysis":

    st.markdown("""
    <h1 style="font-size:2rem; color:#e8f4fd;">🌍 League vs Champions League Performance</h1>
    <p style="color:#6b7280; margin-bottom:24px;">Who performs in big matches? This compares domestic league Save% vs UCL Save%.</p>
    """, unsafe_allow_html=True)

    # Only GKs with UCL games
    ucl_df = df[df["ucl_matches"] > 5].copy()

    # Scatter: League Save% vs UCL Save%
    fig_scatter = px.scatter(
        ucl_df, x="save_pct", y="ucl_save_pct",
        size="ucl_matches", color="composite_score",
        hover_name="player", hover_data={"squad": True, "ucl_matches": True},
        text="player",
        color_continuous_scale="Blues",
        labels={"save_pct": "League Save %", "ucl_save_pct": "UCL Save %", "ucl_matches": "UCL Matches"},
    )
    fig_scatter.update_traces(textposition="top center", textfont=dict(color="#d1d5db", size=10))
    fig_scatter.add_shape(type="line", x0=60, y0=60, x1=82, y1=82, line=dict(color="#1e3a5f", dash="dot"))
    fig_scatter.add_annotation(x=72, y=70, text="Equal performance line", font=dict(color="#6b7280", size=10), showarrow=False)
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.5)",
        xaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#9ca3af")),
        yaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#9ca3af")),
        font=dict(color="#9ca3af"),
        height=480,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("💡 GKs above the dotted line perform BETTER in UCL than in their league — they rise to big occasions.")

    # Heatmap: all GKs × key metrics
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 🔥 Performance Heatmap — All Goalkeepers")

    hm_metrics = ["save_pct","clean_sheet_pct","psxg_diff","ucl_save_pct","penalty_save_pct","goals_per_game"]
    hm_labels  = ["Save %","CS %","PSxG Diff","UCL Save%","Pen Save%","GA/Game"]
    hm_df = df.set_index("player")[hm_metrics].copy()
    hm_df["goals_per_game"] = -hm_df["goals_per_game"]   # invert so higher = better

    # Normalise each column 0-1 for heatmap colouring
    hm_norm = (hm_df - hm_df.min()) / (hm_df.max() - hm_df.min())

    fig_hm = go.Figure(go.Heatmap(
        z=hm_norm.values,
        x=hm_labels,
        y=hm_norm.index.tolist(),
        colorscale="Blues",
        showscale=True,
        text=[[f"{v:.1f}" for v in row] for row in hm_df.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
    ))
    fig_hm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,33,55,0.5)",
        xaxis=dict(tickfont=dict(color="#9ca3af")),
        yaxis=dict(tickfont=dict(color="#e8f4fd"), autorange="reversed"),
        height=550,
        margin=dict(l=180, r=20, t=40, b=40),
    )
    st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE 5: METHODOLOGY
# ══════════════════════════════════════════════════════════════════
elif page == "📚 Methodology":

    st.markdown("""
    <h1 style="font-size:2rem; color:#e8f4fd;">📚 Full Methodology — For Analysts & Coaches</h1>
    <p style="color:#6b7280;">Everything you need to understand <i>how</i> we ranked the world's best goalkeepers.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    ## 🔬 Research Design

    This analysis covers **16 elite goalkeepers** from the **Big 5 European Leagues** over **5 seasons (2019–20 to 2023–24)**, 
    plus **Champions League** data. Only goalkeepers with **30+ total appearances** were included to ensure statistical reliability.

    ---

    ## 📐 Metrics Explained

    | Metric | Formula | Weight | Why It Matters |
    |--------|---------|--------|----------------|
    | **Save %** | Saves ÷ Shots on Target × 100 | **25%** | Core efficiency — how often the GK stops shots |
    | **PSxG Diff** | PSxG − Goals Against | **25%** | The gold standard — did the GK save harder shots than expected? |
    | **Clean Sheet %** | Clean Sheets ÷ Matches × 100 | **15%** | Consistency — how often the team keeps a zero |
    | **Goals/Game (inv.)** | Goals Against ÷ Matches | **15%** | Lower = better; inverted for scoring |
    | **UCL Save %** | UCL Saves ÷ UCL Shots × 100 | **10%** | Big match performance in elite competition |
    | **Penalty Save %** | Pen Saved ÷ Pen Faced × 100 | **5%** | Clutch moments that decide titles |
    | **Distribution %** | Pass Accuracy % | **5%** | Modern GKs build play from the back |

    ---

    ## ⚙️ Composite Score Formula

    Each metric is **normalised** to a 0–100 scale so they're comparable:

    ```
    Normalised Value = (Value − Min) / (Max − Min) × 100
    ```

    Then a **weighted average** is computed:

    ```
    Composite Score =
      (Save% × 0.25) +
      (PSxG Diff × 0.25) +
      (Clean Sheet% × 0.15) +
      (Goals/Game_inverted × 0.15) +
      (UCL Save% × 0.10) +
      (Pen Save% × 0.05) +
      (Distribution% × 0.05)
    ```

    ---

    ## 🛠️ Technology Stack

    | Layer | Tool | Purpose |
    |-------|------|---------|
    | Language | Python 3.11 | Core programming |
    | Data | pandas, numpy | Collection, cleaning, aggregation |
    | Scraping | requests, BeautifulSoup | FBref data extraction |
    | Visualisation | plotly, matplotlib | All charts |
    | Dashboard | Streamlit | Interactive web app |
    | Normalisation | scikit-learn MinMaxScaler | Metric scaling |
    | Hosting | Streamlit Cloud | Free public URL |

    ---

    ## ⚠️ Limitations & Caveats

    - **Team quality matters**: A GK on a top team (City, Real) faces fewer shots and may have an inflated Clean Sheet % — that's why we weight **PSxG Diff** as highly as Save%, because PSxG measures shot QUALITY not just quantity.
    - **Injury seasons**: GKs like Courtois (2022-23, season ending ACL) and ter Stegen are fairly assessed by weighting averages by matches played.
    - **Retired/transferred GKs**: De Gea retired from club football in 2023-24, Lloris left PL — their scores naturally drop.
    - **UCL access**: Not all teams qualify every year, so a GK with fewer UCL games isn't penalised unfairly (UCL weight = only 10%).
    """)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    <b style="color:#60a5fa;">🎤 Interview Talking Points</b><br><br>
    ✅ "We used a multi-metric composite scoring model with 7 KPIs, weighted by analytical importance."<br>
    ✅ "PSxG-GA separates goalkeepers who face difficult shots from those who face simple ones."<br>
    ✅ "We aggregated 5 seasons to smooth out single-season noise and variance."<br>
    ✅ "Data was collected from FBref, the industry-standard source used by Premier League clubs."<br>
    ✅ "The dashboard was built in Python with Streamlit and deployed to Streamlit Cloud for free."
    </div>
    """, unsafe_allow_html=True)
