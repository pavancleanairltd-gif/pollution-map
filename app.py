import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ireland & UK Air Quality",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, * { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
#MainMenu, header, footer, [data-testid="stToolbar"],
[data-testid="collapsedControl"] { display: none !important; visibility: hidden !important; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
section.main, .stMain, .main {
    background: linear-gradient(160deg, #0a1628 0%, #0d1f3c 40%, #112240 100%) !important;
}

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: -50%; bottom: 0; width: 250%;
    z-index: 0; pointer-events: none;
    background-image:
        radial-gradient(ellipse 300px 90px  at  8% 15%, rgba(30,80,160,0.20) 55%, transparent 100%),
        radial-gradient(ellipse 380px 100px at 32%  8%, rgba(30,80,160,0.18) 55%, transparent 100%),
        radial-gradient(ellipse 280px 85px  at 60% 22%, rgba(30,80,160,0.17) 55%, transparent 100%),
        radial-gradient(ellipse 260px 80px  at 85% 10%, rgba(30,80,160,0.18) 55%, transparent 100%),
        radial-gradient(ellipse 220px 68px  at 20% 50%, rgba(25,70,145,0.13) 55%, transparent 100%),
        radial-gradient(ellipse 260px 78px  at 70% 55%, rgba(25,70,145,0.12) 55%, transparent 100%);
    background-size: 100% 100%;
    animation: dc1 80s linear infinite;
}
@keyframes dc1 { from{transform:translateX(0)} to{transform:translateX(40%)} }

[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top: 0; left: -60%; bottom: 0; width: 260%;
    z-index: 0; pointer-events: none;
    background-image:
        radial-gradient(ellipse 220px 65px at 18% 65%, rgba(25,70,145,0.11) 55%, transparent 100%),
        radial-gradient(ellipse 300px 85px at 48% 75%, rgba(25,70,145,0.11) 55%, transparent 100%),
        radial-gradient(ellipse 240px 72px at  2% 82%, rgba(25,70,145,0.11) 55%, transparent 100%);
    background-size: 100% 100%;
    animation: dc2 110s linear infinite reverse;
}
@keyframes dc2 { from{transform:translateX(0)} to{transform:translateX(38%)} }

[data-testid="block-container"], .block-container {
    position: relative; z-index: 1;
    padding: 0 !important; max-width: 100% !important;
}
.stMainBlockContainer { padding: 0 !important; }

/* Header */
.header-banner {
    background: linear-gradient(90deg, #060e1f 0%, #0a1628 60%, #0d1f3c 100%);
    border-bottom: 1px solid rgba(56,139,253,0.22);
    padding: 1rem 2rem 0.9rem 2rem;
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
}
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.header-icon { font-size: 1.6rem; line-height: 1; }
.header-title {
    font-size: 1.2rem; font-weight: 700; color: #e8f4ff;
    letter-spacing: -0.02em; margin: 0; line-height: 1.2;
}
.header-subtitle { font-size: 0.74rem; color: #6b9fd4; margin: 0.1rem 0 0 0; font-weight: 400; }
.header-badge {
    background: rgba(56,139,253,0.12); border: 1px solid rgba(56,139,253,0.28);
    border-radius: 999px; padding: 0.25rem 0.75rem;
    font-size: 0.70rem; color: #88b8f0; font-weight: 500; white-space: nowrap;
}

/* Sidebar panel */
.sidebar-panel {
    background: rgba(8,18,36,0.92);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(56,139,253,0.13);
    border-radius: 0 0 0 0;
}
.sidebar-empty {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 400px; padding: 2rem; text-align: center;
}
.sidebar-empty-icon { font-size: 2.4rem; margin-bottom: 1rem; }
.sidebar-empty-text { font-size: 0.84rem; line-height: 1.6; color: #4a6a8a; }
.sidebar-empty-sub  { font-size: 0.74rem; color: #2d4a6a; margin-top: 0.5rem; }

/* City header */
.city-header {
    padding: 1.1rem 1.3rem 0.9rem 1.3rem;
    border-bottom: 1px solid rgba(56,139,253,0.10);
}
.city-header-name { font-size: 1.25rem; font-weight: 700; color: #e8f4ff; margin: 0 0 0.1rem 0; }
.city-header-meta { font-size: 0.72rem; color: #4a7aaa; font-family:'JetBrains Mono',monospace !important; }

/* AQI display */
.aqi-display { padding: 0.95rem 1.3rem; border-bottom: 1px solid rgba(56,139,253,0.08); }
.aqi-main-row { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 0.7rem; }
.aqi-circle {
    width: 60px; height: 60px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 700; color: #fff; flex-shrink: 0;
    box-shadow: 0 0 18px rgba(0,0,0,0.45);
    font-family: 'JetBrains Mono', monospace !important;
}
.aqi-level-text { font-size: 0.95rem; font-weight: 600; color: #e8f4ff; margin: 0; }
.aqi-level-sub  { font-size: 0.72rem; color: #5a8ab8; margin-top: 0.12rem; }

/* Trend pill */
.trend-pill {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.26rem 0.7rem; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600; letter-spacing: 0.02em; margin-top: 0.35rem;
}
.trend-up     { background:rgba(220,50,50,0.17);  color:#ff7070; border:1px solid rgba(220,50,50,0.28); }
.trend-down   { background:rgba(30,180,100,0.17); color:#5ee8a0; border:1px solid rgba(30,180,100,0.28); }
.trend-stable { background:rgba(80,130,200,0.14); color:#88b8f0; border:1px solid rgba(80,130,200,0.24); }

/* Metrics */
.metrics-grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 0.5rem; padding: 0.9rem 1.3rem;
    border-bottom: 1px solid rgba(56,139,253,0.08);
}
.metric-card {
    background: rgba(16,32,64,0.68); border: 1px solid rgba(56,139,253,0.11);
    border-radius: 8px; padding: 0.55rem 0.65rem;
}
.metric-card-label {
    font-size: 0.63rem; color: #4a7aaa; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.18rem;
}
.metric-card-value {
    font-size: 1.05rem; font-weight: 600; color: #c8e0f8;
    font-family: 'JetBrains Mono', monospace !important; line-height: 1.1;
}
.metric-card-unit { font-size: 0.60rem; color: #3a5a7a; font-family:'JetBrains Mono',monospace !important; }

.chart-section { padding: 0.8rem 0.4rem 0.5rem 0.4rem; }
.chart-section-label {
    font-size: 0.67rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.1em; color: #3a6a9a; padding: 0 0.6rem; margin-bottom: 0.35rem;
}

/* Map instruction */
.map-note {
    font-size: 0.73rem; color: #3a6a9a; text-align: center;
    margin-top: 0.45rem; padding: 0 0.5rem;
}

/* Disclaimer */
.disclaimer-box {
    background: rgba(8,18,36,0.78); border-top: 1px solid rgba(240,165,0,0.22);
    border-left: 3px solid #f0a500; padding: 0.75rem 2rem;
    font-size: 0.75rem; color: #6a8aaa; line-height: 1.6;
}
.disclaimer-box strong { color: #a0c0d8; }

/* Footer */
.footer-bar {
    background: linear-gradient(90deg, #060e1f 0%, #0a1628 100%);
    border-top: 1px solid rgba(56,139,253,0.13);
    text-align: center; padding: 1rem 1.5rem;
}
.footer-brand { font-size: 0.95rem; font-weight: 700; color: #e8f4ff; letter-spacing: 0.01em; }
.footer-tagline { font-size: 0.74rem; color: #4a7aaa; margin-top: 0.12rem; }

/* Responsive */
@media (max-width: 768px) {
    .header-banner { padding: 0.75rem 1rem; }
    .header-title  { font-size: 0.95rem; }
    .disclaimer-box { padding: 0.75rem 1rem; }
    .metrics-grid   { grid-template-columns: 1fr 1fr; }
}

div[data-testid="stVerticalBlock"] > div { background: transparent !important; }
.stMarkdown { background: transparent !important; }
section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── AQI scale ─────────────────────────────────────────────────────────────────
AQI_SCALE = [
    (20,  "#009966", "Good"),
    (40,  "#5cb85c", "Fair"),
    (60,  "#f0c430", "Moderate"),
    (80,  "#e07020", "Poor"),
    (100, "#d03020", "Very Poor"),
    (999, "#7e1f8e", "Extremely Poor"),
]

def aqi_colour(v):
    try:
        v = float(v)
        if np.isnan(v): return "#445566"
    except (TypeError, ValueError):
        return "#445566"
    for thr, col, _ in AQI_SCALE:
        if v <= thr: return col
    return "#7e1f8e"

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

# ── Cities ────────────────────────────────────────────────────────────────────
CITIES = {
    "Dublin":{"lat":53.3498,"lon":-6.2603,"country":"Ireland"},
    "Cork":{"lat":51.8985,"lon":-8.4756,"country":"Ireland"},
    "Galway":{"lat":53.2707,"lon":-9.0568,"country":"Ireland"},
    "Limerick":{"lat":52.6638,"lon":-8.6267,"country":"Ireland"},
    "Waterford":{"lat":52.2593,"lon":-7.1101,"country":"Ireland"},
    "Kilkenny":{"lat":52.6541,"lon":-7.2448,"country":"Ireland"},
    "Drogheda":{"lat":53.7189,"lon":-6.3478,"country":"Ireland"},
    "Dundalk":{"lat":54.0035,"lon":-6.4110,"country":"Ireland"},
    "Sligo":{"lat":54.2697,"lon":-8.4694,"country":"Ireland"},
    "Athlone":{"lat":53.4239,"lon":-7.9407,"country":"Ireland"},
    "Tralee":{"lat":52.2675,"lon":-9.7022,"country":"Ireland"},
    "Ennis":{"lat":52.8459,"lon":-8.9863,"country":"Ireland"},
    "Wexford":{"lat":52.3369,"lon":-6.4633,"country":"Ireland"},
    "Mullingar":{"lat":53.5252,"lon":-7.3389,"country":"Ireland"},
    "Navan":{"lat":53.6527,"lon":-6.6819,"country":"Ireland"},
    "Letterkenny":{"lat":54.9533,"lon":-7.7333,"country":"Ireland"},
    "Carlow":{"lat":52.8408,"lon":-6.9261,"country":"Ireland"},
    "Tullamore":{"lat":53.2756,"lon":-7.4878,"country":"Ireland"},
    "Bray":{"lat":53.2008,"lon":-6.0986,"country":"Ireland"},
    "Wicklow":{"lat":52.9800,"lon":-6.0444,"country":"Ireland"},
    "Castlebar":{"lat":53.8594,"lon":-9.2986,"country":"Ireland"},
    "Roscommon":{"lat":53.6311,"lon":-8.1892,"country":"Ireland"},
    "Killarney":{"lat":52.0599,"lon":-9.5044,"country":"Ireland"},
    "Clonmel":{"lat":52.3548,"lon":-7.7030,"country":"Ireland"},
    "Portlaoise":{"lat":53.0341,"lon":-7.2993,"country":"Ireland"},
    "Cavan":{"lat":53.9908,"lon":-7.3600,"country":"Ireland"},
    "Monaghan":{"lat":54.2492,"lon":-6.9685,"country":"Ireland"},
    "Longford":{"lat":53.7276,"lon":-7.7971,"country":"Ireland"},
    "Westport":{"lat":53.7997,"lon":-9.5175,"country":"Ireland"},
    "Belfast":{"lat":54.5973,"lon":-5.9301,"country":"Northern Ireland"},
    "Derry":{"lat":54.9966,"lon":-7.3086,"country":"Northern Ireland"},
    "Lisburn":{"lat":54.5162,"lon":-6.0586,"country":"Northern Ireland"},
    "Newry":{"lat":54.1751,"lon":-6.3400,"country":"Northern Ireland"},
    "Armagh":{"lat":54.3503,"lon":-6.6528,"country":"Northern Ireland"},
    "Omagh":{"lat":54.5978,"lon":-7.2989,"country":"Northern Ireland"},
    "Enniskillen":{"lat":54.3447,"lon":-7.6328,"country":"Northern Ireland"},
    "Ballymena":{"lat":54.8639,"lon":-6.2789,"country":"Northern Ireland"},
    "Coleraine":{"lat":55.1322,"lon":-6.6683,"country":"Northern Ireland"},
    "Bangor NI":{"lat":54.6536,"lon":-5.6679,"country":"Northern Ireland"},
    "London":{"lat":51.5074,"lon":-0.1278,"country":"England"},
    "Manchester":{"lat":53.4808,"lon":-2.2426,"country":"England"},
    "Birmingham":{"lat":52.4862,"lon":-1.8904,"country":"England"},
    "Leeds":{"lat":53.8008,"lon":-1.5491,"country":"England"},
    "Bristol":{"lat":51.4545,"lon":-2.5879,"country":"England"},
    "Liverpool":{"lat":53.4084,"lon":-2.9916,"country":"England"},
    "Newcastle":{"lat":54.9783,"lon":-1.6178,"country":"England"},
    "Sheffield":{"lat":53.3811,"lon":-1.4701,"country":"England"},
    "Nottingham":{"lat":52.9548,"lon":-1.1581,"country":"England"},
    "Leicester":{"lat":52.6369,"lon":-1.1398,"country":"England"},
    "Coventry":{"lat":52.4081,"lon":-1.5106,"country":"England"},
    "Bradford":{"lat":53.7960,"lon":-1.7594,"country":"England"},
    "Stoke-on-Trent":{"lat":53.0027,"lon":-2.1794,"country":"England"},
    "Derby":{"lat":52.9225,"lon":-1.4746,"country":"England"},
    "Southampton":{"lat":50.9097,"lon":-1.4044,"country":"England"},
    "Portsmouth":{"lat":50.8198,"lon":-1.0880,"country":"England"},
    "Brighton":{"lat":50.8225,"lon":-0.1372,"country":"England"},
    "Hull":{"lat":53.7676,"lon":-0.3274,"country":"England"},
    "Middlesbrough":{"lat":54.5742,"lon":-1.2350,"country":"England"},
    "Sunderland":{"lat":54.9069,"lon":-1.3838,"country":"England"},
    "Oxford":{"lat":51.7520,"lon":-1.2577,"country":"England"},
    "Cambridge":{"lat":52.2053,"lon":0.1218,"country":"England"},
    "Exeter":{"lat":50.7184,"lon":-3.5339,"country":"England"},
    "Plymouth":{"lat":50.3755,"lon":-4.1427,"country":"England"},
    "Norwich":{"lat":52.6309,"lon":1.2974,"country":"England"},
    "Ipswich":{"lat":52.0567,"lon":1.1482,"country":"England"},
    "Peterborough":{"lat":52.5695,"lon":-0.2405,"country":"England"},
    "Milton Keynes":{"lat":52.0406,"lon":-0.7594,"country":"England"},
    "Wolverhampton":{"lat":52.5860,"lon":-2.1288,"country":"England"},
    "Carlisle":{"lat":54.8951,"lon":-2.9382,"country":"England"},
    "York":{"lat":53.9590,"lon":-1.0815,"country":"England"},
    "Lancaster":{"lat":54.0466,"lon":-2.7998,"country":"England"},
    "Blackpool":{"lat":53.8142,"lon":-3.0503,"country":"England"},
    "Reading":{"lat":51.4543,"lon":-0.9781,"country":"England"},
    "Luton":{"lat":51.8787,"lon":-0.4200,"country":"England"},
    "Northampton":{"lat":52.2405,"lon":-0.9027,"country":"England"},
    "Gloucester":{"lat":51.8642,"lon":-2.2380,"country":"England"},
    "Truro":{"lat":50.2632,"lon":-5.0510,"country":"England"},
    "Lincoln":{"lat":53.2307,"lon":-0.5406,"country":"England"},
    "Edinburgh":{"lat":55.9533,"lon":-3.1883,"country":"Scotland"},
    "Glasgow":{"lat":55.8642,"lon":-4.2518,"country":"Scotland"},
    "Aberdeen":{"lat":57.1497,"lon":-2.0943,"country":"Scotland"},
    "Dundee":{"lat":56.4620,"lon":-2.9707,"country":"Scotland"},
    "Inverness":{"lat":57.4778,"lon":-4.2247,"country":"Scotland"},
    "Stirling":{"lat":56.1165,"lon":-3.9369,"country":"Scotland"},
    "Perth":{"lat":56.3950,"lon":-3.4310,"country":"Scotland"},
    "Paisley":{"lat":55.8456,"lon":-4.4230,"country":"Scotland"},
    "Ayr":{"lat":55.4628,"lon":-4.6293,"country":"Scotland"},
    "Dumfries":{"lat":55.0704,"lon":-3.6052,"country":"Scotland"},
    "Fort William":{"lat":56.8198,"lon":-5.1052,"country":"Scotland"},
    "Kirkcaldy":{"lat":56.1107,"lon":-3.1615,"country":"Scotland"},
    "Cardiff":{"lat":51.4816,"lon":-3.1791,"country":"Wales"},
    "Swansea":{"lat":51.6214,"lon":-3.9436,"country":"Wales"},
    "Newport":{"lat":51.5842,"lon":-2.9977,"country":"Wales"},
    "Wrexham":{"lat":53.0461,"lon":-2.9925,"country":"Wales"},
    "Bangor":{"lat":53.2274,"lon":-4.1293,"country":"Wales"},
    "Aberystwyth":{"lat":52.4153,"lon":-4.0829,"country":"Wales"},
    "Llanelli":{"lat":51.6842,"lon":-4.1625,"country":"Wales"},
    "Merthyr Tydfil":{"lat":51.7459,"lon":-3.3785,"country":"Wales"},
    "Rhyl":{"lat":53.3196,"lon":-3.4909,"country":"Wales"},
    "Caernarfon":{"lat":53.1393,"lon":-4.2758,"country":"Wales"},
}

# ── Data fetch ────────────────────────────────────────────────────────────────
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
        "time": pd.to_datetime(d["time"]),
        "european_aqi": d.get("european_aqi"),
        "pm2_5": d.get("pm2_5"),
        "pm10": d.get("pm10"),
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

def compute_trend(df):
    aqi = df["european_aqi"].dropna()
    if len(aqi) < 12:
        return "stable", "Stable →"
    slope = np.polyfit(np.arange(len(aqi)), aqi, 1)[0]
    per_day = slope * 24
    if per_day > 2:   return "up",   "Worsening ↑"
    elif per_day < -2: return "down", "Improving ↓"
    return "stable", "Stable →"

# ── Map builder ───────────────────────────────────────────────────────────────
def build_map(selected_city=None, aqi_cache=None):
    m = folium.Map(location=[54.2, -4.0], zoom_start=6,
                   tiles="CartoDB dark_matter", prefer_canvas=True)

    # Legend
    legend = """
    <div style="position:absolute;top:12px;right:12px;z-index:9999;
        background:rgba(8,18,36,0.88);border:1px solid rgba(56,139,253,0.20);
        border-radius:8px;padding:10px 13px;font-family:Inter,sans-serif;">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.1em;color:#4a7aaa;margin-bottom:7px;">EU AQI Scale</div>
    """
    ranges = ["0–20","21–40","41–60","61–80","81–100","100+"]
    for i, (thr, col, lbl) in enumerate(AQI_SCALE):
        legend += f"""<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
          <span style="width:11px;height:11px;border-radius:50%;background:{col};
                       display:inline-block;border:1.5px solid rgba(255,255,255,0.15);flex-shrink:0;"></span>
          <span style="font-size:10.5px;color:#a0c0e0;">{ranges[i]} {lbl}</span></div>"""
    legend += "</div>"
    m.get_root().html.add_child(folium.Element(legend))

    aqi_cache = aqi_cache or {}
    for city, info in CITIES.items():
        is_sel  = city == selected_city
        aqi_val = aqi_cache.get(city)
        colour  = aqi_colour(aqi_val) if aqi_val is not None else "#445566"
        aqi_disp = f"{int(round(aqi_val))}" if aqi_val is not None else "?"
        aqi_lbl  = aqi_label(aqi_val) if aqi_val is not None else "click to load"

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=11 if is_sel else 7,
            color="#ffffff" if is_sel else colour,
            weight=3 if is_sel else 1.5,
            fill=True, fill_color=colour,
            fill_opacity=1.0 if is_sel else 0.82,
            tooltip=folium.Tooltip(
                f"<span style='font-family:Inter,sans-serif;font-size:12px;"
                f"font-weight:600;color:#e8f4ff;'>{city}</span>"
                f"<br><span style='font-size:10px;color:#6a9ac8;'>"
                f"{info['country']} · AQI {aqi_disp} · {aqi_lbl}</span>",
                sticky=False,
            ),
            popup=folium.Popup(city, parse_html=False),
        ).add_to(m)

        if is_sel:
            folium.Marker(
                location=[info["lat"] + 0.18, info["lon"]],
                icon=folium.DivIcon(
                    html=f"<div style='font-family:Inter,sans-serif;font-size:11px;"
                         f"font-weight:700;color:#fff;white-space:nowrap;"
                         f"text-shadow:0 1px 4px #000;'>{city}</div>",
                    icon_size=(140, 20), icon_anchor=(70, 0),
                ),
            ).add_to(m)
    return m

# ── Chart ─────────────────────────────────────────────────────────────────────
def build_chart(df):
    has_no2 = df["nitrogen_dioxide"].notna().any()
    rows    = 4 if has_no2 else 3
    titles  = ["European AQI", "PM2.5 (µg/m³)", "PM10 (µg/m³)"]
    if has_no2: titles.append("NO₂ (µg/m³)")

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, subplot_titles=titles)

    C = {"aqi":"#388bfd","pm25":"#ff7c4c","pm10":"#b07af5","no2":"#3ecf8e"}

    def add_tr(col, name, colour, row, fmt):
        fig.add_trace(go.Scatter(
            x=df["time"], y=df[col], mode="lines", name=name,
            line=dict(color=colour, width=1.8),
            fill="tozeroy", fillcolor=colour+"22",
            hovertemplate=f"%{{y:{fmt}}}<extra>{name}</extra>",
        ), row=row, col=1)

    add_tr("european_aqi","AQI",C["aqi"],1,".0f")
    add_tr("pm2_5","PM2.5",C["pm25"],2,".1f")
    add_tr("pm10","PM10",C["pm10"],3,".1f")
    if has_no2: add_tr("nitrogen_dioxide","NO₂",C["no2"],4,".1f")

    GRID = "rgba(56,90,140,0.16)"
    fig.update_layout(
        height=510 if has_no2 else 385,
        margin=dict(l=4,r=4,t=26,b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,24,46,0.68)",
        font=dict(family="Inter, sans-serif", size=10, color="#4a7aaa"),
        showlegend=False, hovermode="x unified",
    )
    for i in range(1, rows+1):
        fig.update_xaxes(showgrid=True,gridcolor=GRID,zeroline=False,
                         tickformat="%a %d",tickfont=dict(size=9,color="#3a6a9a"),
                         row=i,col=1,linecolor="rgba(56,90,140,0.18)")
        fig.update_yaxes(showgrid=True,gridcolor=GRID,zeroline=False,
                         tickfont=dict(size=9,color="#3a6a9a"),
                         row=i,col=1,linecolor="rgba(56,90,140,0.18)")
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=10,color="#4a7aaa",family="Inter, sans-serif")
        ann["x"] = 0
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-banner">
  <div class="header-left">
    <span class="header-icon">🌍</span>
    <div>
      <p class="header-title">Ireland &amp; UK Air Quality Forecast</p>
      <p class="header-subtitle">Live 7-day pollution forecast powered by Open-Meteo</p>
    </div>
  </div>
  <span class="header-badge">99 locations · Free &amp; no login required</span>
</div>
""", unsafe_allow_html=True)

# Init state
if "selected_city" not in st.session_state:
    st.session_state["selected_city"] = None
if "aqi_cache" not in st.session_state:
    st.session_state["aqi_cache"] = {}

active_city = st.session_state["selected_city"]
aqi_cache   = st.session_state["aqi_cache"]

# Ensure selected city AQI cached
if active_city and active_city not in aqi_cache:
    info = CITIES[active_city]
    aqi_cache[active_city] = fetch_current_aqi(info["lat"], info["lon"])
    st.session_state["aqi_cache"] = aqi_cache

col_sidebar, col_map = st.columns([0.37, 0.63], gap="small")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with col_sidebar:
    if not active_city:
        st.markdown("""
        <div class="sidebar-panel">
          <div class="sidebar-empty">
            <div class="sidebar-empty-icon">🗺️</div>
            <div class="sidebar-empty-text">
              Click any marker on the map to load its 7-day air quality forecast.
            </div>
            <div class="sidebar-empty-sub">
              99 locations across Ireland, Northern Ireland,<br>England, Scotland &amp; Wales
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

        colour   = aqi_colour(aqi_v)
        lbl      = aqi_label(aqi_v)
        aqi_disp = fmt_val(aqi_v, 0)
        trend_dir, trend_label = compute_trend(df)
        badge_cls = {"up":"trend-up","down":"trend-down","stable":"trend-stable"}[trend_dir]
        lon_dir   = "W" if info["lon"] < 0 else "E"

        no2_card = ""
        if fmt_val(no2_v) != "—":
            no2_card = (
                f'<div class="metric-card">'
                f'<div class="metric-card-label">NO₂</div>'
                f'<div class="metric-card-value">{fmt_val(no2_v)}</div>'
                f'<div class="metric-card-unit">µg/m³</div></div>'
            )

        st.markdown(f"""
        <div class="sidebar-panel">
          <div class="city-header">
            <div class="city-header-name">{active_city}</div>
            <div class="city-header-meta">
              {info['country']} &nbsp;·&nbsp; {info['lat']:.4f}°N {abs(info['lon']):.4f}°{lon_dir}
            </div>
          </div>
          <div class="aqi-display">
            <div class="aqi-main-row">
              <div class="aqi-circle" style="background:{colour};">{aqi_disp}</div>
              <div>
                <div class="aqi-level-text">{lbl}</div>
                <div class="aqi-level-sub">European AQI (current)</div>
                <span class="trend-pill {badge_cls}">{trend_label}</span>
              </div>
            </div>
          </div>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-card-label">PM2.5</div>
              <div class="metric-card-value">{fmt_val(pm25_v)}</div>
              <div class="metric-card-unit">µg/m³</div>
            </div>
            <div class="metric-card">
              <div class="metric-card-label">PM10</div>
              <div class="metric-card-value">{fmt_val(pm10_v)}</div>
              <div class="metric-card-unit">µg/m³</div>
            </div>
            {no2_card}
          </div>
          <div class="chart-section">
            <div class="chart-section-label">7-day hourly forecast</div>
        """, unsafe_allow_html=True)

        fig = build_chart(df)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # AQI key
        scale_html = '<div style="padding:0.15rem 0.6rem 0.8rem 0.6rem;display:flex;flex-wrap:wrap;gap:0.28rem;">'
        scale_html += '<span style="font-size:0.63rem;color:#3a6a9a;width:100%;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.1rem;">EU AQI Scale</span>'
        ranges = ["0–20","21–40","41–60","61–80","81–100","100+"]
        for i, (thr, col, lbl_s) in enumerate(AQI_SCALE):
            scale_html += (
                f'<span style="font-size:0.66rem;background:rgba(0,0,0,0.28);'
                f'color:{col};padding:2px 7px;border-radius:999px;border:1px solid {col}44;">'
                f'{lbl_s}</span>'
            )
        scale_html += "</div></div></div>"
        st.markdown(scale_html, unsafe_allow_html=True)

# ── MAP ───────────────────────────────────────────────────────────────────────
with col_map:
    m = build_map(selected_city=active_city, aqi_cache=aqi_cache)

    map_data = st_folium(
        m, width=None, height=630,
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
        '<div class="map-note">Click any circle to see its 7-day forecast &nbsp;·&nbsp; '
        'Circle colour = current EU AQI level</div>',
        unsafe_allow_html=True,
    )

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-box">
  <strong>⚠️ Disclaimer:</strong>&nbsp; This tool is for indicative purposes only.
  Pollution forecasts are predictions based on available data and may not be fully accurate,
  as levels can be influenced by weather conditions, local events, and other external factors.
  This tool has been developed to help people identify general air quality trends in advance.
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
  <div class="footer-brand">Pavan Clean Air</div>
  <div class="footer-tagline">
    Get in touch today to get your tailored air purifier ready for hybrid, indoor and outdoor spaces.
  </div>
</div>
""", unsafe_allow_html=True)
