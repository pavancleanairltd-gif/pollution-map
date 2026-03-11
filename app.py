import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ireland & UK Air Quality",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  NASA / Deep-Space theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ── Base reset ── */
html, body, * {
    font-family: 'Exo 2', sans-serif !important;
    box-sizing: border-box;
    color: #d0e8ff;
}
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}
section[data-testid="stSidebar"] { display: none !important; }
div[data-testid="stVerticalBlock"] > div { background: transparent !important; }
.stMarkdown { background: transparent !important; }

/* ── Deep-space background ── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
section.main, .stMain, .main {
    background: radial-gradient(ellipse at 50% 0%, #0d1b4b 0%, #05091a 55%, #000000 100%) !important;
    background-attachment: fixed !important;
}

/* ── Animated star field ── */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(1px 1px at  4%  8%, rgba(255,255,255,0.90) 0%, transparent 100%),
        radial-gradient(1px 1px at 12% 22%, rgba(255,255,255,0.80) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 20%  5%, rgba(200,220,255,0.85) 0%, transparent 100%),
        radial-gradient(1px 1px at 28% 38%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1px 1px at 35% 15%, rgba(255,255,255,0.90) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 42% 55%, rgba(200,220,255,0.75) 0%, transparent 100%),
        radial-gradient(1px 1px at 50% 28%, rgba(255,255,255,0.85) 0%, transparent 100%),
        radial-gradient(1px 1px at 57%  9%, rgba(255,255,255,0.75) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 63% 44%, rgba(200,220,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 18%, rgba(255,255,255,0.90) 0%, transparent 100%),
        radial-gradient(1px 1px at 76% 62%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 82%  3%, rgba(200,220,255,0.85) 0%, transparent 100%),
        radial-gradient(1px 1px at 88% 35%, rgba(255,255,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 93% 72%, rgba(255,255,255,0.75) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 97% 15%, rgba(200,220,255,0.90) 0%, transparent 100%),
        radial-gradient(1px 1px at  7% 50%, rgba(255,255,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 16% 78%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 24% 92%, rgba(200,220,255,0.75) 0%, transparent 100%),
        radial-gradient(1px 1px at 33% 67%, rgba(255,255,255,0.85) 0%, transparent 100%),
        radial-gradient(1px 1px at 45% 82%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 54% 95%, rgba(200,220,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 64% 88%, rgba(255,255,255,0.75) 0%, transparent 100%),
        radial-gradient(1px 1px at 73% 76%, rgba(255,255,255,0.85) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 85% 90%, rgba(200,220,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 91% 48%, rgba(255,255,255,0.90) 0%, transparent 100%);
    animation: starTwinkle 6s ease-in-out infinite alternate;
}
@keyframes starTwinkle {
    0%   { opacity: 0.55; }
    50%  { opacity: 1.00; }
    100% { opacity: 0.60; }
}

/* Second star layer — slower, offset positions */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(1px 1px at  9% 31%, rgba(255,255,255,0.75) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 18% 59%, rgba(200,220,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 27% 46%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1px 1px at 38%  2%, rgba(255,255,255,0.85) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 48% 71%, rgba(200,220,255,0.75) 0%, transparent 100%),
        radial-gradient(1px 1px at 59% 37%, rgba(255,255,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 67% 84%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 78% 53%, rgba(200,220,255,0.85) 0%, transparent 100%),
        radial-gradient(1px 1px at 86% 24%, rgba(255,255,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 95% 66%, rgba(255,255,255,0.75) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at  3% 87%, rgba(200,220,255,0.80) 0%, transparent 100%),
        radial-gradient(1px 1px at 14% 13%, rgba(255,255,255,0.70) 0%, transparent 100%),
        radial-gradient(1px 1px at 52%  6%, rgba(255,255,255,0.90) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 72% 98%, rgba(200,220,255,0.75) 0%, transparent 100%),
        radial-gradient(1px 1px at 89% 42%, rgba(255,255,255,0.85) 0%, transparent 100%);
    animation: starTwinkle2 9s ease-in-out infinite alternate;
}
@keyframes starTwinkle2 {
    0%   { opacity: 0.40; }
    50%  { opacity: 0.90; }
    100% { opacity: 0.50; }
}

/* ── Layout container ── */
[data-testid="block-container"],
.block-container,
.stMainBlockContainer {
    position: relative;
    z-index: 1;
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── HEADER BANNER ── */
.nasa-header {
    position: relative;
    z-index: 2;
    background: linear-gradient(90deg, #000510 0%, #050d2a 50%, #000510 100%);
    border-bottom: 1px solid rgba(80,160,255,0.30);
    padding: 0.95rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.6rem;
    box-shadow: 0 2px 30px rgba(40,100,255,0.15);
}
.nasa-header-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.nasa-header-icon { font-size: 1.8rem; line-height: 1; }
.nasa-header-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.04em;
    margin: 0;
    text-shadow: 0 0 20px rgba(80,160,255,0.70), 0 0 40px rgba(40,100,255,0.40);
}
.nasa-header-subtitle {
    font-size: 0.73rem;
    color: #6090c0;
    margin: 0.1rem 0 0 0;
    letter-spacing: 0.06em;
    font-family: 'Share Tech Mono', monospace !important;
}
.nasa-header-badge {
    background: rgba(40,100,255,0.12);
    border: 1px solid rgba(80,160,255,0.35);
    border-radius: 4px;
    padding: 0.3rem 0.85rem;
    font-size: 0.68rem;
    color: #80c0ff;
    letter-spacing: 0.08em;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase;
}

/* ── SIDEBAR PANEL ── */
.space-sidebar {
    background: rgba(3, 8, 25, 0.88);
    border-right: 1px solid rgba(40,100,255,0.20);
    backdrop-filter: blur(12px);
    min-height: 640px;
}
.sidebar-empty-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 500px;
    padding: 2rem;
    text-align: center;
}
.sidebar-empty-icon { font-size: 2.8rem; margin-bottom: 1rem; }
.sidebar-empty-title {
    font-size: 0.9rem;
    color: #4a7aaa;
    line-height: 1.6;
    font-weight: 500;
}
.sidebar-empty-sub {
    font-size: 0.72rem;
    color: #2a4a6a;
    margin-top: 0.6rem;
    letter-spacing: 0.04em;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── City header in sidebar ── */
.city-block {
    padding: 1.1rem 1.3rem 0.9rem 1.3rem;
    border-bottom: 1px solid rgba(40,100,255,0.15);
}
.city-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8f4ff;
    margin: 0 0 0.15rem 0;
    letter-spacing: 0.02em;
    text-shadow: 0 0 12px rgba(80,160,255,0.50);
}
.city-coords {
    font-size: 0.70rem;
    color: #3a6a9a;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.06em;
}

/* ── AQI display ── */
.aqi-block {
    padding: 1rem 1.3rem;
    border-bottom: 1px solid rgba(40,100,255,0.12);
}
.aqi-row {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.aqi-orb {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
    font-family: 'Share Tech Mono', monospace !important;
    position: relative;
}
.aqi-level { font-size: 1rem; font-weight: 600; color: #e8f4ff; margin: 0; }
.aqi-sublabel { font-size: 0.70rem; color: #4a7aaa; margin-top: 0.1rem; letter-spacing: 0.05em; font-family: 'Share Tech Mono', monospace !important; }

/* ── Trend pill ── */
.trend-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 3px;
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-top: 0.4rem;
    font-family: 'Share Tech Mono', monospace !important;
}
.trend-up     { background:rgba(255,60,60,0.15);   color:#ff6060; border:1px solid rgba(255,60,60,0.35); }
.trend-down   { background:rgba(0,255,140,0.12);   color:#00ff8c; border:1px solid rgba(0,255,140,0.35); }
.trend-stable { background:rgba(40,140,255,0.12);  color:#60b0ff; border:1px solid rgba(40,140,255,0.30); }

/* ── Metric cards ── */
.metrics-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.55rem;
    padding: 0.9rem 1.3rem;
    border-bottom: 1px solid rgba(40,100,255,0.12);
}
.metric-card {
    background: rgba(5,15,40,0.75);
    border: 1px solid rgba(40,120,255,0.22);
    border-radius: 6px;
    padding: 0.6rem 0.7rem;
    box-shadow: 0 0 12px rgba(40,100,255,0.08), inset 0 0 8px rgba(40,100,255,0.04);
}
.mc-label {
    font-size: 0.60rem;
    color: #2a6a9a;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    margin-bottom: 0.2rem;
    font-family: 'Share Tech Mono', monospace !important;
}
.mc-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #a0d0ff;
    font-family: 'Share Tech Mono', monospace !important;
    line-height: 1.1;
}
.mc-unit {
    font-size: 0.58rem;
    color: #2a5a7a;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── WHO panel ── */
.who-panel {
    padding: 0.85rem 1.3rem;
    border-bottom: 1px solid rgba(40,100,255,0.12);
}
.panel-title {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2a6a9a;
    margin-bottom: 0.6rem;
    font-family: 'Share Tech Mono', monospace !important;
}
.who-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    gap: 0.4rem;
}
.who-name  { font-size: 0.73rem; color: #70a0d0; font-weight: 500; min-width: 48px; }
.who-val   { font-size: 0.72rem; color: #90c0e8; font-family:'Share Tech Mono',monospace !important; flex:1; text-align:center; }
.who-good  { font-size: 0.65rem; font-weight: 700; color: #00ee88; background: rgba(0,200,100,0.12); border: 1px solid rgba(0,200,100,0.28); border-radius: 3px; padding: 1px 7px; white-space:nowrap; font-family:'Share Tech Mono',monospace !important; }
.who-bad   { font-size: 0.65rem; font-weight: 700; color: #ff5555; background: rgba(255,60,60,0.12);  border: 1px solid rgba(255,60,60,0.28);  border-radius: 3px; padding: 1px 7px; white-space:nowrap; font-family:'Share Tech Mono',monospace !important; }
.who-na    { font-size: 0.65rem; font-weight: 500; color: #3a5a7a; background: rgba(40,80,140,0.12);  border: 1px solid rgba(40,80,140,0.22);  border-radius: 3px; padding: 1px 7px; white-space:nowrap; font-family:'Share Tech Mono',monospace !important; }
.who-note  { font-size: 0.60rem; color: #2a4a6a; margin-top: -0.3rem; margin-bottom: 0.3rem; font-style: italic; padding-left: 0.1rem; }

/* ── Health advice panel ── */
.health-panel {
    padding: 0.85rem 1.3rem;
    border-bottom: 1px solid rgba(40,100,255,0.12);
}
.health-box {
    border-radius: 5px;
    padding: 0.7rem 0.9rem;
    font-size: 0.76rem;
    line-height: 1.6;
    color: #d0e8ff;
    border-left: 3px solid;
}

/* ── Chart section ── */
.chart-section { padding: 0.7rem 0.3rem 0.4rem 0.3rem; }
.chart-label {
    font-size: 0.63rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2a6a9a;
    padding: 0 0.6rem;
    margin-bottom: 0.3rem;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── AQI scale strip ── */
.scale-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    padding: 0.2rem 0.6rem 0.8rem 0.6rem;
}
.scale-label-head {
    font-size: 0.58rem;
    color: #2a5a7a;
    width: 100%;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.05rem;
    font-family: 'Share Tech Mono', monospace !important;
}
.scale-chip {
    font-size: 0.62rem;
    padding: 2px 7px;
    border-radius: 3px;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Map note ── */
.map-note {
    font-size: 0.70rem;
    color: #2a5a8a;
    text-align: center;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Disclaimer ── */
.disclaimer {
    background: rgba(2,6,20,0.82);
    border-top: 1px solid rgba(200,140,0,0.25);
    border-left: 3px solid #d09000;
    padding: 0.75rem 2rem;
    font-size: 0.72rem;
    color: #5a7a9a;
    line-height: 1.65;
    position: relative;
    z-index: 2;
}
.disclaimer strong { color: #8ab0d0; }

/* ── Footer ── */
.space-footer {
    background: linear-gradient(90deg, #000510 0%, #030a1e 100%);
    border-top: 1px solid rgba(40,100,255,0.18);
    text-align: center;
    padding: 1.1rem 1.5rem 1.2rem 1.5rem;
    position: relative;
    z-index: 2;
}
.footer-brand {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.06em;
    text-shadow: 0 0 14px rgba(80,160,255,0.50);
}
.footer-tagline {
    font-size: 0.73rem;
    color: #5a8aaa;
    margin-top: 0.2rem;
    letter-spacing: 0.03em;
}
.footer-link {
    font-size: 0.72rem;
    margin-top: 0.35rem;
}
.footer-link a {
    color: #60a8ff;
    text-decoration: underline;
    text-underline-offset: 2px;
    letter-spacing: 0.03em;
}
.footer-link a:hover { color: #90c8ff; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .nasa-header     { padding: 0.75rem 1rem; }
    .nasa-header-title { font-size: 0.95rem; }
    .metrics-row     { grid-template-columns: 1fr 1fr; }
    .disclaimer      { padding: 0.75rem 1rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  AQI SCALE & HELPERS
# ─────────────────────────────────────────────────────────────────────────────
AQI_SCALE = [
    (20,  "#009966", "Good"),
    (40,  "#5cb85c", "Fair"),
    (60,  "#f0c430", "Moderate"),
    (80,  "#e07020", "Poor"),
    (100, "#d03020", "Very Poor"),
    (999, "#7e1f8e", "Extremely Poor"),
]

# Glow colours per level (for marker box-shadow)
AQI_GLOW = [
    (20,  "rgba(0,200,120,0.70)"),
    (40,  "rgba(90,200,90,0.65)"),
    (60,  "rgba(240,200,40,0.70)"),
    (80,  "rgba(220,110,20,0.70)"),
    (100, "rgba(210,40,20,0.70)"),
    (999, "rgba(140,30,160,0.70)"),
]

HEALTH_ADVICE = [
    (20,  "#009966", "rgba(0,153,102,0.13)",
     "✅ Air quality is good. No precautions needed. Safe for all outdoor activities."),
    (40,  "#5cb85c", "rgba(92,184,92,0.13)",
     "🟢 Air quality is acceptable. Unusually sensitive individuals should consider limiting prolonged outdoor exertion."),
    (60,  "#f0c430", "rgba(240,196,48,0.13)",
     "⚠️ Sensitive groups (children, elderly, asthma sufferers) should reduce prolonged outdoor activity. Consider wearing a mask outdoors."),
    (80,  "#e07020", "rgba(224,112,32,0.13)",
     "🟠 Everyone should reduce outdoor exertion. Sensitive groups should avoid outdoor activity. Wear a mask outdoors. Keep windows closed."),
    (100, "#d03020", "rgba(208,48,32,0.13)",
     "🔴 Avoid outdoor activity where possible. Everyone should wear a mask outdoors. Keep windows closed. Use an air purifier indoors."),
    (999, "#7e1f8e", "rgba(126,31,142,0.13)",
     "🟣 Stay indoors. Do not open windows. Wear a mask if you must go outside. Use a high-quality air purifier indoors immediately."),
]

WHO_GUIDELINES = {
    "PM2.5": 15.0,
    "PM10":  45.0,
    "NO₂":   25.0,
}


def aqi_colour(v):
    try:
        v = float(v)
        if np.isnan(v): return "#334455"
    except (TypeError, ValueError):
        return "#334455"
    for thr, col, _ in AQI_SCALE:
        if v <= thr: return col
    return "#7e1f8e"


def aqi_glow(v):
    try:
        v = float(v)
        if np.isnan(v): return "rgba(40,80,140,0.40)"
    except (TypeError, ValueError):
        return "rgba(40,80,140,0.40)"
    for thr, glow in AQI_GLOW:
        if v <= thr: return glow
    return "rgba(140,30,160,0.70)"


def aqi_label(v):
    try:
        v = float(v)
        if np.isnan(v): return "N/A"
    except (TypeError, ValueError):
        return "N/A"
    for thr, _, lbl in AQI_SCALE:
        if v <= thr: return lbl
    return "Extremely Poor"


def fmt_val(v, dec=1):
    try:
        f = float(v)
        return "—" if np.isnan(f) else f"{f:.{dec}f}"
    except (TypeError, ValueError):
        return "—"


def get_health_advice(v):
    try:
        v = float(v)
        if np.isnan(v):
            return "#334455", "rgba(30,50,90,0.12)", "No AQI data available for this location."
    except (TypeError, ValueError):
        return "#334455", "rgba(30,50,90,0.12)", "No AQI data available for this location."
    for thr, border, bg, text in HEALTH_ADVICE:
        if v <= thr:
            return border, bg, text
    return "#7e1f8e", "rgba(126,31,142,0.13)", HEALTH_ADVICE[-1][3]


def compute_trend(df):
    aqi = df["european_aqi"].dropna()
    if len(aqi) < 12:
        return "stable", "Stable — No significant change expected"
    slope = np.polyfit(np.arange(len(aqi)), aqi, 1)[0]
    per_day = slope * 24
    if per_day > 2:
        return "up",   "Worsening ↑ — Pollution expected to increase"
    elif per_day < -2:
        return "down", "Improving ↓ — Pollution expected to decrease"
    return "stable", "Stable — No significant change expected"


# ─────────────────────────────────────────────────────────────────────────────
#  CITY DATA  (99 locations)
# ─────────────────────────────────────────────────────────────────────────────
CITIES = {
    "Dublin":         {"lat":53.3498,"lon":-6.2603, "country":"Ireland"},
    "Cork":           {"lat":51.8985,"lon":-8.4756, "country":"Ireland"},
    "Galway":         {"lat":53.2707,"lon":-9.0568, "country":"Ireland"},
    "Limerick":       {"lat":52.6638,"lon":-8.6267, "country":"Ireland"},
    "Waterford":      {"lat":52.2593,"lon":-7.1101, "country":"Ireland"},
    "Kilkenny":       {"lat":52.6541,"lon":-7.2448, "country":"Ireland"},
    "Drogheda":       {"lat":53.7189,"lon":-6.3478, "country":"Ireland"},
    "Dundalk":        {"lat":54.0035,"lon":-6.4110, "country":"Ireland"},
    "Sligo":          {"lat":54.2697,"lon":-8.4694, "country":"Ireland"},
    "Athlone":        {"lat":53.4239,"lon":-7.9407, "country":"Ireland"},
    "Tralee":         {"lat":52.2675,"lon":-9.7022, "country":"Ireland"},
    "Ennis":          {"lat":52.8459,"lon":-8.9863, "country":"Ireland"},
    "Wexford":        {"lat":52.3369,"lon":-6.4633, "country":"Ireland"},
    "Mullingar":      {"lat":53.5252,"lon":-7.3389, "country":"Ireland"},
    "Navan":          {"lat":53.6527,"lon":-6.6819, "country":"Ireland"},
    "Letterkenny":    {"lat":54.9533,"lon":-7.7333, "country":"Ireland"},
    "Carlow":         {"lat":52.8408,"lon":-6.9261, "country":"Ireland"},
    "Tullamore":      {"lat":53.2756,"lon":-7.4878, "country":"Ireland"},
    "Bray":           {"lat":53.2008,"lon":-6.0986, "country":"Ireland"},
    "Wicklow":        {"lat":52.9800,"lon":-6.0444, "country":"Ireland"},
    "Castlebar":      {"lat":53.8594,"lon":-9.2986, "country":"Ireland"},
    "Roscommon":      {"lat":53.6311,"lon":-8.1892, "country":"Ireland"},
    "Killarney":      {"lat":52.0599,"lon":-9.5044, "country":"Ireland"},
    "Clonmel":        {"lat":52.3548,"lon":-7.7030, "country":"Ireland"},
    "Portlaoise":     {"lat":53.0341,"lon":-7.2993, "country":"Ireland"},
    "Cavan":          {"lat":53.9908,"lon":-7.3600, "country":"Ireland"},
    "Monaghan":       {"lat":54.2492,"lon":-6.9685, "country":"Ireland"},
    "Longford":       {"lat":53.7276,"lon":-7.7971, "country":"Ireland"},
    "Westport":       {"lat":53.7997,"lon":-9.5175, "country":"Ireland"},
    "Belfast":        {"lat":54.5973,"lon":-5.9301, "country":"Northern Ireland"},
    "Derry":          {"lat":54.9966,"lon":-7.3086, "country":"Northern Ireland"},
    "Lisburn":        {"lat":54.5162,"lon":-6.0586, "country":"Northern Ireland"},
    "Newry":          {"lat":54.1751,"lon":-6.3400, "country":"Northern Ireland"},
    "Armagh":         {"lat":54.3503,"lon":-6.6528, "country":"Northern Ireland"},
    "Omagh":          {"lat":54.5978,"lon":-7.2989, "country":"Northern Ireland"},
    "Enniskillen":    {"lat":54.3447,"lon":-7.6328, "country":"Northern Ireland"},
    "Ballymena":      {"lat":54.8639,"lon":-6.2789, "country":"Northern Ireland"},
    "Coleraine":      {"lat":55.1322,"lon":-6.6683, "country":"Northern Ireland"},
    "Bangor NI":      {"lat":54.6536,"lon":-5.6679, "country":"Northern Ireland"},
    "London":         {"lat":51.5074,"lon":-0.1278, "country":"England"},
    "Manchester":     {"lat":53.4808,"lon":-2.2426, "country":"England"},
    "Birmingham":     {"lat":52.4862,"lon":-1.8904, "country":"England"},
    "Leeds":          {"lat":53.8008,"lon":-1.5491, "country":"England"},
    "Bristol":        {"lat":51.4545,"lon":-2.5879, "country":"England"},
    "Liverpool":      {"lat":53.4084,"lon":-2.9916, "country":"England"},
    "Newcastle":      {"lat":54.9783,"lon":-1.6178, "country":"England"},
    "Sheffield":      {"lat":53.3811,"lon":-1.4701, "country":"England"},
    "Nottingham":     {"lat":52.9548,"lon":-1.1581, "country":"England"},
    "Leicester":      {"lat":52.6369,"lon":-1.1398, "country":"England"},
    "Coventry":       {"lat":52.4081,"lon":-1.5106, "country":"England"},
    "Bradford":       {"lat":53.7960,"lon":-1.7594, "country":"England"},
    "Stoke-on-Trent": {"lat":53.0027,"lon":-2.1794, "country":"England"},
    "Derby":          {"lat":52.9225,"lon":-1.4746, "country":"England"},
    "Southampton":    {"lat":50.9097,"lon":-1.4044, "country":"England"},
    "Portsmouth":     {"lat":50.8198,"lon":-1.0880, "country":"England"},
    "Brighton":       {"lat":50.8225,"lon":-0.1372, "country":"England"},
    "Hull":           {"lat":53.7676,"lon":-0.3274, "country":"England"},
    "Middlesbrough":  {"lat":54.5742,"lon":-1.2350, "country":"England"},
    "Sunderland":     {"lat":54.9069,"lon":-1.3838, "country":"England"},
    "Oxford":         {"lat":51.7520,"lon":-1.2577, "country":"England"},
    "Cambridge":      {"lat":52.2053,"lon": 0.1218, "country":"England"},
    "Exeter":         {"lat":50.7184,"lon":-3.5339, "country":"England"},
    "Plymouth":       {"lat":50.3755,"lon":-4.1427, "country":"England"},
    "Norwich":        {"lat":52.6309,"lon": 1.2974, "country":"England"},
    "Ipswich":        {"lat":52.0567,"lon": 1.1482, "country":"England"},
    "Peterborough":   {"lat":52.5695,"lon":-0.2405, "country":"England"},
    "Milton Keynes":  {"lat":52.0406,"lon":-0.7594, "country":"England"},
    "Wolverhampton":  {"lat":52.5860,"lon":-2.1288, "country":"England"},
    "Carlisle":       {"lat":54.8951,"lon":-2.9382, "country":"England"},
    "York":           {"lat":53.9590,"lon":-1.0815, "country":"England"},
    "Lancaster":      {"lat":54.0466,"lon":-2.7998, "country":"England"},
    "Blackpool":      {"lat":53.8142,"lon":-3.0503, "country":"England"},
    "Reading":        {"lat":51.4543,"lon":-0.9781, "country":"England"},
    "Luton":          {"lat":51.8787,"lon":-0.4200, "country":"England"},
    "Northampton":    {"lat":52.2405,"lon":-0.9027, "country":"England"},
    "Gloucester":     {"lat":51.8642,"lon":-2.2380, "country":"England"},
    "Truro":          {"lat":50.2632,"lon":-5.0510, "country":"England"},
    "Lincoln":        {"lat":53.2307,"lon":-0.5406, "country":"England"},
    "Edinburgh":      {"lat":55.9533,"lon":-3.1883, "country":"Scotland"},
    "Glasgow":        {"lat":55.8642,"lon":-4.2518, "country":"Scotland"},
    "Aberdeen":       {"lat":57.1497,"lon":-2.0943, "country":"Scotland"},
    "Dundee":         {"lat":56.4620,"lon":-2.9707, "country":"Scotland"},
    "Inverness":      {"lat":57.4778,"lon":-4.2247, "country":"Scotland"},
    "Stirling":       {"lat":56.1165,"lon":-3.9369, "country":"Scotland"},
    "Perth":          {"lat":56.3950,"lon":-3.4310, "country":"Scotland"},
    "Paisley":        {"lat":55.8456,"lon":-4.4230, "country":"Scotland"},
    "Ayr":            {"lat":55.4628,"lon":-4.6293, "country":"Scotland"},
    "Dumfries":       {"lat":55.0704,"lon":-3.6052, "country":"Scotland"},
    "Fort William":   {"lat":56.8198,"lon":-5.1052, "country":"Scotland"},
    "Kirkcaldy":      {"lat":56.1107,"lon":-3.1615, "country":"Scotland"},
    "Cardiff":        {"lat":51.4816,"lon":-3.1791, "country":"Wales"},
    "Swansea":        {"lat":51.6214,"lon":-3.9436, "country":"Wales"},
    "Newport":        {"lat":51.5842,"lon":-2.9977, "country":"Wales"},
    "Wrexham":        {"lat":53.0461,"lon":-2.9925, "country":"Wales"},
    "Bangor":         {"lat":53.2274,"lon":-4.1293, "country":"Wales"},
    "Aberystwyth":    {"lat":52.4153,"lon":-4.0829, "country":"Wales"},
    "Llanelli":       {"lat":51.6842,"lon":-4.1625, "country":"Wales"},
    "Merthyr Tydfil": {"lat":51.7459,"lon":-3.3785, "country":"Wales"},
    "Rhyl":           {"lat":53.3196,"lon":-3.4909, "country":"Wales"},
    "Caernarfon":     {"lat":53.1393,"lon":-4.2758, "country":"Wales"},
}


# ─────────────────────────────────────────────────────────────────────────────
#  DATA FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_air_quality(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm2_5,pm10,nitrogen_dioxide"
        "&forecast_days=7&timezone=Europe%2FLondon"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    d = r.json()["hourly"]
    return pd.DataFrame({
        "time":             pd.to_datetime(d["time"]),
        "european_aqi":     d.get("european_aqi"),
        "pm2_5":            d.get("pm2_5"),
        "pm10":             d.get("pm10"),
        "nitrogen_dioxide": d.get("nitrogen_dioxide"),
    })


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_current_aqi(lat, lon):
    try:
        df = fetch_air_quality(lat, lon)
        valid = df.dropna(subset=["european_aqi"])
        if not valid.empty:
            return float(valid.iloc[0]["european_aqi"])
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  FOLIUM MAP
# ─────────────────────────────────────────────────────────────────────────────
def build_map(selected_city=None, aqi_cache=None):
    m = folium.Map(
        location=[54.2, -4.0],
        zoom_start=6,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # AQI legend overlay
    ranges_str = ["0–20", "21–40", "41–60", "61–80", "81–100", "100+"]
    legend_html = """
    <div style="position:absolute;top:12px;right:12px;z-index:9999;
        background:rgba(2,5,20,0.92);border:1px solid rgba(40,120,255,0.28);
        border-radius:6px;padding:10px 13px;font-family:'Exo 2',sans-serif;
        box-shadow:0 0 18px rgba(20,80,200,0.20);">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.12em;color:#2a6aaa;margin-bottom:7px;
                  font-family:'Share Tech Mono',monospace;">EU AQI SCALE</div>
    """
    for i, (thr, col, lbl) in enumerate(AQI_SCALE):
        legend_html += (
            f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">'
            f'<span style="width:11px;height:11px;border-radius:50%;background:{col};'
            f'display:inline-block;flex-shrink:0;'
            f'box-shadow:0 0 6px {col};"></span>'
            f'<span style="font-size:10.5px;color:#90b8d8;font-family:\'Share Tech Mono\',monospace;">'
            f'{ranges_str[i]} {lbl}</span></div>'
        )
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    aqi_cache = aqi_cache or {}
    for city, info in CITIES.items():
        is_sel   = city == selected_city
        aqi_val  = aqi_cache.get(city)
        col      = aqi_colour(aqi_val) if aqi_val is not None else "#334455"
        glow     = aqi_glow(aqi_val)   if aqi_val is not None else "rgba(40,80,140,0.40)"
        aqi_disp = f"{int(round(aqi_val))}" if aqi_val is not None else "?"
        aqi_lbl  = aqi_label(aqi_val)  if aqi_val is not None else "click to load"

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=11 if is_sel else 7,
            color="#ffffff"  if is_sel else col,
            weight=3 if is_sel else 1.5,
            fill=True,
            fill_color=col,
            fill_opacity=1.0 if is_sel else 0.88,
            tooltip=folium.Tooltip(
                f"<span style='font-family:\"Exo 2\",sans-serif;font-size:12px;"
                f"font-weight:700;color:#e8f4ff;'>{city}</span>"
                f"<br><span style='font-size:10px;color:#6090c0;"
                f"font-family:\"Share Tech Mono\",monospace;'>"
                f"{info['country']} · AQI {aqi_disp} · {aqi_lbl}</span>",
                sticky=False,
            ),
            popup=folium.Popup(city, parse_html=False),
        ).add_to(m)

        if is_sel:
            folium.Marker(
                location=[info["lat"] + 0.18, info["lon"]],
                icon=folium.DivIcon(
                    html=(
                        f"<div style='font-family:\"Exo 2\",sans-serif;font-size:11px;"
                        f"font-weight:700;color:#ffffff;white-space:nowrap;"
                        f"text-shadow:0 0 8px {col},0 1px 4px #000;'>{city}</div>"
                    ),
                    icon_size=(150, 20),
                    icon_anchor=(75, 0),
                ),
            ).add_to(m)

    return m


# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY CHART  —  BUG FIX: mode="lines" only, NO fill, NO fillcolor
# ─────────────────────────────────────────────────────────────────────────────
def build_chart(df):
    has_no2 = df["nitrogen_dioxide"].notna().any()
    rows    = 4 if has_no2 else 3
    titles  = ["European AQI", "PM2.5 (µg/m³)", "PM10 (µg/m³)"]
    if has_no2:
        titles.append("NO₂ (µg/m³)")

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=titles,
    )

    COLOURS = {
        "aqi":  "#4090ff",
        "pm25": "#ff6040",
        "pm10": "#c070ff",
        "no2":  "#00e890",
    }

    # ── Lines only — no fill or fillcolor anywhere ──
    def add_trace(col_name, label, colour, row, fmt):
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[col_name],
                mode="lines",
                name=label,
                line=dict(color=colour, width=2.0),
                hovertemplate=f"%{{y:{fmt}}}<extra>{label}</extra>",
            ),
            row=row, col=1,
        )

    add_trace("european_aqi",    "AQI",   COLOURS["aqi"],  1, ".0f")
    add_trace("pm2_5",           "PM2.5", COLOURS["pm25"], 2, ".1f")
    add_trace("pm10",            "PM10",  COLOURS["pm10"], 3, ".1f")
    if has_no2:
        add_trace("nitrogen_dioxide", "NO₂", COLOURS["no2"], 4, ".1f")

    GRID_COL = "rgba(30,70,160,0.18)"
    BG_COL   = "rgba(3,8,25,0.70)"

    fig.update_layout(
        height=520 if has_no2 else 390,
        margin=dict(l=4, r=4, t=26, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG_COL,
        font=dict(family="Exo 2, sans-serif", size=10, color="#3a6a9a"),
        showlegend=False,
        hovermode="x unified",
    )
    for i in range(1, rows + 1):
        fig.update_xaxes(
            showgrid=True, gridcolor=GRID_COL, zeroline=False,
            tickformat="%a %d",
            tickfont=dict(size=9, color="#2a5a8a", family="Share Tech Mono, monospace"),
            linecolor="rgba(30,70,160,0.22)",
            row=i, col=1,
        )
        fig.update_yaxes(
            showgrid=True, gridcolor=GRID_COL, zeroline=False,
            tickfont=dict(size=9, color="#2a5a8a", family="Share Tech Mono, monospace"),
            linecolor="rgba(30,70,160,0.22)",
            row=i, col=1,
        )
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=10, color="#2a6aaa", family="Share Tech Mono, monospace")
        ann["x"] = 0

    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  WHO PANEL  —  built as a single HTML string, rendered with unsafe_allow_html
# ─────────────────────────────────────────────────────────────────────────────
def render_who_panel(pm25_str, pm10_str, no2_str):
    def status_badge(val_str, limit):
        if val_str == "—":
            return '<span class="who-na">NO DATA</span>'
        try:
            v = float(val_str)
        except ValueError:
            return '<span class="who-na">NO DATA</span>'
        if v <= limit:
            return '<span class="who-good">✓ WITHIN</span>'
        return '<span class="who-bad">✗ ABOVE</span>'

    rows = [
        ("PM2.5", pm25_str, WHO_GUIDELINES["PM2.5"], "WHO 24-hr: 15 µg/m³"),
        ("PM10",  pm10_str, WHO_GUIDELINES["PM10"],  "WHO 24-hr: 45 µg/m³"),
        ("NO₂",   no2_str,  WHO_GUIDELINES["NO₂"],   "WHO 24-hr: 25 µg/m³"),
    ]

    html = '<div class="who-panel"><div class="panel-title">🔬 WHO Air Quality Targets</div>'
    for name, val_str, limit, note in rows:
        badge = status_badge(val_str, limit)
        unit  = " µg/m³" if val_str != "—" else ""
        html += (
            f'<div class="who-row">'
            f'<span class="who-name">{name}</span>'
            f'<span class="who-val">{val_str}{unit}</span>'
            f'{badge}'
            f'</div>'
            f'<div class="who-note">{note}</div>'
        )
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HEALTH ADVICE PANEL
# ─────────────────────────────────────────────────────────────────────────────
def render_health_panel(aqi_v):
    border, bg, text = get_health_advice(aqi_v)
    html = (
        f'<div class="health-panel">'
        f'<div class="panel-title">💊 Health Recommendations</div>'
        f'<div class="health-box" style="background:{bg};border-left-color:{border};">'
        f'{text}'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nasa-header">
  <div class="nasa-header-left">
    <span class="nasa-header-icon">🛰️</span>
    <div>
      <p class="nasa-header-title">Ireland &amp; UK Air Quality Forecast</p>
      <p class="nasa-header-subtitle">LIVE 7-DAY POLLUTION FORECAST · POWERED BY OPEN-METEO</p>
    </div>
  </div>
  <span class="nasa-header-badge">99 LOCATIONS · FREE · NO LOGIN</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "selected_city" not in st.session_state:
    st.session_state["selected_city"] = None
if "aqi_cache" not in st.session_state:
    st.session_state["aqi_cache"] = {}

active_city = st.session_state["selected_city"]
aqi_cache   = st.session_state["aqi_cache"]

# Pre-cache AQI for selected city
if active_city and active_city not in aqi_cache:
    _info = CITIES[active_city]
    aqi_cache[active_city] = fetch_current_aqi(_info["lat"], _info["lon"])
    st.session_state["aqi_cache"] = aqi_cache


# ─────────────────────────────────────────────────────────────────────────────
#  TWO-COLUMN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
col_side, col_map = st.columns([0.37, 0.63], gap="small")


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with col_side:
    if not active_city:
        st.markdown("""
        <div class="space-sidebar">
          <div class="sidebar-empty-wrap">
            <div class="sidebar-empty-icon">🛰️</div>
            <div class="sidebar-empty-title">
              Select a location on the map to load its 7-day air quality forecast.
            </div>
            <div class="sidebar-empty-sub">
              99 LOCATIONS · IE · NI · ENG · SCO · WAL
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        info = CITIES[active_city]
        with st.spinner(f"Loading {active_city}…"):
            try:
                df = fetch_air_quality(info["lat"], info["lon"])
            except Exception as e:
                st.error(f"Data unavailable: {e}")
                st.stop()

        valid = df.dropna(subset=["european_aqi"])
        now   = valid.iloc[0] if not valid.empty else None

        aqi_v  = float(now["european_aqi"]) if now is not None else None
        pm25_v = now["pm2_5"]               if now is not None else None
        pm10_v = now["pm10"]                if now is not None else None
        no2_v  = now["nitrogen_dioxide"]    if now is not None else None

        aqi_cache[active_city] = aqi_v
        st.session_state["aqi_cache"] = aqi_cache

        col        = aqi_colour(aqi_v)
        glow       = aqi_glow(aqi_v)
        lbl        = aqi_label(aqi_v)
        aqi_disp   = fmt_val(aqi_v, 0)
        pm25_str   = fmt_val(pm25_v)
        pm10_str   = fmt_val(pm10_v)
        no2_str    = fmt_val(no2_v)

        trend_dir, trend_label = compute_trend(df)
        t_cls  = {"up": "trend-up", "down": "trend-down", "stable": "trend-stable"}[trend_dir]
        lon_dir = "W" if info["lon"] < 0 else "E"

        # ── City + AQI block ──
        no2_card_html = ""
        if no2_str != "—":
            no2_card_html = (
                f'<div class="metric-card">'
                f'<div class="mc-label">NO₂</div>'
                f'<div class="mc-value">{no2_str}</div>'
                f'<div class="mc-unit">µg/m³</div>'
                f'</div>'
            )

        st.markdown(f"""
        <div class="space-sidebar">
          <div class="city-block">
            <div class="city-name">{active_city}</div>
            <div class="city-coords">
              {info['country'].upper()} &nbsp;·&nbsp;
              {info['lat']:.4f}°N &nbsp; {abs(info['lon']):.4f}°{lon_dir}
            </div>
          </div>
          <div class="aqi-block">
            <div class="aqi-row">
              <div class="aqi-orb"
                   style="background:{col};
                          box-shadow:0 0 18px {glow}, 0 0 36px {glow}, inset 0 0 10px rgba(255,255,255,0.15);">
                {aqi_disp}
              </div>
              <div>
                <div class="aqi-level">{lbl}</div>
                <div class="aqi-sublabel">EUROPEAN AQI · CURRENT</div>
                <span class="trend-pill {t_cls}">{trend_label}</span>
              </div>
            </div>
          </div>
          <div class="metrics-row">
            <div class="metric-card">
              <div class="mc-label">PM2.5</div>
              <div class="mc-value">{pm25_str}</div>
              <div class="mc-unit">µg/m³</div>
            </div>
            <div class="metric-card">
              <div class="mc-label">PM10</div>
              <div class="mc-value">{pm10_str}</div>
              <div class="mc-unit">µg/m³</div>
            </div>
            {no2_card_html}
          </div>
        """, unsafe_allow_html=True)

        # ── WHO panel  (separate st.markdown call — fully rendered HTML) ──
        render_who_panel(pm25_str, pm10_str, no2_str)

        # ── Health advice ──
        render_health_panel(aqi_v)

        # ── Chart ──
        st.markdown(
            '<div class="chart-section">'
            '<div class="chart-label">📡 7-Day Hourly Forecast</div>',
            unsafe_allow_html=True,
        )
        fig = build_chart(df)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── AQI scale chips + close outer div ──
        ranges_str = ["0–20", "21–40", "41–60", "61–80", "81–100", "100+"]
        chips = "".join(
            f'<span class="scale-chip" style="background:rgba(0,0,0,0.30);'
            f'color:{c};border:1px solid {c}44;">{lbl_s}</span>'
            for _, c, lbl_s in AQI_SCALE
        )
        st.markdown(
            f'<div class="scale-strip">'
            f'<span class="scale-label-head">EU AQI SCALE</span>'
            f'{chips}'
            f'</div>'
            f'</div>',   # closes space-sidebar
            unsafe_allow_html=True,
        )


# ── MAP COLUMN ───────────────────────────────────────────────────────────────
with col_map:
    m = build_map(selected_city=active_city, aqi_cache=aqi_cache)

    map_data = st_folium(
        m,
        width=None,
        height=640,
        returned_objects=["last_object_clicked_popup"],
        key="main_map",
    )

    if map_data and map_data.get("last_object_clicked_popup"):
        clicked = map_data["last_object_clicked_popup"]
        if isinstance(clicked, str) and clicked in CITIES:
            if clicked != st.session_state.get("selected_city"):
                st.session_state["selected_city"] = clicked
                st.rerun()

    st.markdown(
        '<div class="map-note">'
        '[ CLICK A MARKER TO LOAD ITS FORECAST ] &nbsp;·&nbsp; '
        '[ COLOUR = CURRENT EU AQI LEVEL ]'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  DISCLAIMER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
  <strong>⚠️ DISCLAIMER:</strong>&nbsp; This tool is for indicative purposes only.
  Pollution forecasts are predictions based on available data and may not be fully accurate,
  as levels can be influenced by weather conditions, local events, and other external factors.
  This tool has been developed to help people identify general air quality trends in advance.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="space-footer">
  <div class="footer-brand">Pavan Clean Air</div>
  <div class="footer-tagline">
    Get in touch today to get your tailored air purifier ready for hybrid, indoor and outdoor spaces.
  </div>
  <div class="footer-link">
    <a href="https://www.pavancleanair.com" target="_blank" rel="noopener noreferrer">
      Visit us at www.pavancleanair.com
    </a>
  </div>
</div>
""", unsafe_allow_html=True)
