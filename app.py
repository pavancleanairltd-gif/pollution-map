import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK & Ireland Air Quality",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS: animated cloud sky + layout ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ─── Sky gradient background ─── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
section.main, .stMain, .main {
    background: linear-gradient(180deg, #b8ddf0 0%, #d8eef8 50%, #eaf5fb 100%) !important;
    background-attachment: fixed !important;
}

/* ─── Cloud layer 1 (slow) ─── */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: -50%; right: 0; bottom: 0;
    width: 250%;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(ellipse 260px 85px  at  8% 12%, rgba(255,255,255,0.90) 55%, transparent 100%),
        radial-gradient(ellipse 180px 60px  at  8% 17%, rgba(255,255,255,0.72) 55%, transparent 100%),
        radial-gradient(ellipse 320px 95px  at 30% 8%,  rgba(255,255,255,0.88) 55%, transparent 100%),
        radial-gradient(ellipse 210px 65px  at 30% 13%, rgba(255,255,255,0.68) 55%, transparent 100%),
        radial-gradient(ellipse 280px 80px  at 55% 20%, rgba(255,255,255,0.85) 55%, transparent 100%),
        radial-gradient(ellipse 160px 50px  at 55% 25%, rgba(255,255,255,0.65) 55%, transparent 100%),
        radial-gradient(ellipse 230px 75px  at 78% 6%,  rgba(255,255,255,0.88) 55%, transparent 100%),
        radial-gradient(ellipse 150px 48px  at 78% 11%, rgba(255,255,255,0.65) 55%, transparent 100%),
        radial-gradient(ellipse 200px 65px  at 92% 22%, rgba(255,255,255,0.80) 55%, transparent 100%),
        radial-gradient(ellipse 240px 72px  at 18% 45%, rgba(255,255,255,0.72) 55%, transparent 100%),
        radial-gradient(ellipse 190px 60px  at 65% 50%, rgba(255,255,255,0.70) 55%, transparent 100%);
    background-size: 100% 100%;
    animation: driftClouds1 70s linear infinite;
}
@keyframes driftClouds1 {
    from { transform: translateX(0); }
    to   { transform: translateX(40%); }
}

/* ─── Cloud layer 2 (faster, different shapes) ─── */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top: 0; left: -60%; right: 0; bottom: 0;
    width: 260%;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(ellipse 200px 60px at 15% 62%, rgba(255,255,255,0.68) 55%, transparent 100%),
        radial-gradient(ellipse 270px 78px at 45% 72%, rgba(255,255,255,0.65) 55%, transparent 100%),
        radial-gradient(ellipse 160px 52px at 72% 40%, rgba(255,255,255,0.62) 55%, transparent 100%),
        radial-gradient(ellipse 220px 68px at  3% 80%, rgba(255,255,255,0.65) 55%, transparent 100%),
        radial-gradient(ellipse 180px 55px at 85% 68%, rgba(255,255,255,0.62) 55%, transparent 100%);
    background-size: 100% 100%;
    animation: driftClouds2 100s linear infinite reverse;
}
@keyframes driftClouds2 {
    from { transform: translateX(0); }
    to   { transform: translateX(35%); }
}

/* ─── Content above clouds ─── */
[data-testid="block-container"],
.block-container {
    position: relative;
    z-index: 1;
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 1300px;
}

/* ─── Glass-white panel (map + data cols) ─── */
.glass-panel {
    background: rgba(255,255,255,0.86);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.75);
    box-shadow: 0 4px 28px rgba(80,130,180,0.10);
    padding: 1.1rem 1.2rem;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, header, footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ─── Typography ─── */
html, body, * { font-family: 'DM Sans', sans-serif !important; }

/* ─── App header ─── */
.app-header {
    background: rgba(255,255,255,0.84);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 0.9rem 1.3rem 0.85rem 1.3rem;
    margin-bottom: 1.2rem;
    border-bottom: 2px solid rgba(20,80,150,0.10);
    box-shadow: 0 2px 16px rgba(80,130,180,0.08);
}
.app-title {
    font-size: 1.55rem;
    font-weight: 600;
    color: #0f2a4a;
    letter-spacing: -0.02em;
    margin: 0;
}
.app-subtitle {
    font-size: 0.82rem;
    color: #6a8aaa;
    margin-top: 0.2rem;
    font-weight: 400;
}

/* ─── City card ─── */
.city-card {
    background: rgba(235,248,255,0.88);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.9rem;
    border: 1px solid rgba(190,220,245,0.65);
}
.city-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: #0f2a4a;
    margin: 0;
}
.city-meta {
    font-size: 0.78rem;
    color: #7a9ab8;
    font-family: 'DM Mono', monospace !important;
    margin-top: 0.2rem;
}

/* ─── Trend badges ─── */
.trend-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    margin-top: 0.6rem;
}
.trend-up     { background: #ffe5e5; color: #c0392b; }
.trend-down   { background: #e5f5ec; color: #1e8449; }
.trend-stable { background: rgba(215,232,245,0.80); color: #3a5a78; }

/* ─── Section label ─── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8aaac8;
    margin-bottom: 0.4rem;
}

/* ─── Hint box ─── */
.hint {
    background: rgba(255,255,255,0.82);
    border-left: 3px solid rgba(90,155,220,0.35);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.84rem;
    color: #3a5a78;
}

/* ─── Metric row ─── */
.metric-row {
    display: flex;
    gap: 0.65rem;
    margin-bottom: 0.9rem;
    flex-wrap: wrap;
}
.metric-box {
    flex: 1;
    min-width: 85px;
    background: rgba(235,248,255,0.82);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    border: 1px solid rgba(190,220,245,0.55);
}
.metric-label {
    font-size: 0.70rem;
    color: #8aaac8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.metric-value {
    font-size: 1.3rem;
    font-weight: 600;
    color: #0f2a4a;
    font-family: 'DM Mono', monospace !important;
    line-height: 1.2;
}
.metric-unit {
    font-size: 0.70rem;
    color: #8aaac8;
    font-family: 'DM Mono', monospace !important;
}

/* ─── Disclaimer ─── */
.disclaimer-box {
    background: rgba(255,255,255,0.82);
    border-left: 3px solid #f0a500;
    border-radius: 6px;
    padding: 0.85rem 1.2rem;
    margin: 1.6rem 0 0 0;
    font-size: 0.80rem;
    color: #4a5a6a;
    line-height: 1.6;
}
.disclaimer-box strong { color: #2a3a4a; }

/* ─── Pavan footer ─── */
.footer-bar {
    background: #1a2535;
    color: #fff;
    text-align: center;
    padding: 1.15rem 1.5rem 1.2rem 1.5rem;
    margin-top: 1.2rem;
    border-radius: 10px;
}
.footer-bar .brand {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.01em;
}
.footer-bar .tagline {
    font-size: 0.82rem;
    color: #96b8d4;
    margin-top: 0.15rem;
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

# ── City data: 85 locations ───────────────────────────────────────────────────
CITIES = {
    # ── Republic of Ireland ──────────────────────────────────────────────────
    "Dublin":           {"lat": 53.3498, "lon": -6.2603,  "country": "Ireland"},
    "Cork":             {"lat": 51.8985, "lon": -8.4756,  "country": "Ireland"},
    "Galway":           {"lat": 53.2707, "lon": -9.0568,  "country": "Ireland"},
    "Limerick":         {"lat": 52.6638, "lon": -8.6267,  "country": "Ireland"},
    "Waterford":        {"lat": 52.2593, "lon": -7.1101,  "country": "Ireland"},
    "Kilkenny":         {"lat": 52.6541, "lon": -7.2448,  "country": "Ireland"},
    "Drogheda":         {"lat": 53.7189, "lon": -6.3478,  "country": "Ireland"},
    "Dundalk":          {"lat": 54.0035, "lon": -6.4110,  "country": "Ireland"},
    "Sligo":            {"lat": 54.2697, "lon": -8.4694,  "country": "Ireland"},
    "Athlone":          {"lat": 53.4239, "lon": -7.9407,  "country": "Ireland"},
    "Tralee":           {"lat": 52.2675, "lon": -9.7022,  "country": "Ireland"},
    "Ennis":            {"lat": 52.8459, "lon": -8.9863,  "country": "Ireland"},
    "Wexford":          {"lat": 52.3369, "lon": -6.4633,  "country": "Ireland"},
    "Mullingar":        {"lat": 53.5252, "lon": -7.3389,  "country": "Ireland"},
    "Navan":            {"lat": 53.6527, "lon": -6.6819,  "country": "Ireland"},
    "Letterkenny":      {"lat": 54.9533, "lon": -7.7333,  "country": "Ireland"},
    "Carlow":           {"lat": 52.8408, "lon": -6.9261,  "country": "Ireland"},
    "Tullamore":        {"lat": 53.2756, "lon": -7.4878,  "country": "Ireland"},
    "Bray":             {"lat": 53.2008, "lon": -6.0986,  "country": "Ireland"},
    "Wicklow":          {"lat": 52.9800, "lon": -6.0444,  "country": "Ireland"},
    "Castlebar":        {"lat": 53.8594, "lon": -9.2986,  "country": "Ireland"},
    "Roscommon":        {"lat": 53.6311, "lon": -8.1892,  "country": "Ireland"},
    "Killarney":        {"lat": 52.0599, "lon": -9.5044,  "country": "Ireland"},
    "Clonmel":          {"lat": 52.3548, "lon": -7.7030,  "country": "Ireland"},
    "Portlaoise":       {"lat": 53.0341, "lon": -7.2993,  "country": "Ireland"},
    "Cavan":            {"lat": 53.9908, "lon": -7.3600,  "country": "Ireland"},
    "Monaghan":         {"lat": 54.2492, "lon": -6.9685,  "country": "Ireland"},
    "Longford":         {"lat": 53.7276, "lon": -7.7971,  "country": "Ireland"},
    "Westport":         {"lat": 53.7997, "lon": -9.5175,  "country": "Ireland"},
    # ── Northern Ireland ─────────────────────────────────────────────────────
    "Belfast":          {"lat": 54.5973, "lon": -5.9301,  "country": "Northern Ireland"},
    "Derry":            {"lat": 54.9966, "lon": -7.3086,  "country": "Northern Ireland"},
    "Lisburn":          {"lat": 54.5162, "lon": -6.0586,  "country": "Northern Ireland"},
    "Newry":            {"lat": 54.1751, "lon": -6.3400,  "country": "Northern Ireland"},
    "Armagh":           {"lat": 54.3503, "lon": -6.6528,  "country": "Northern Ireland"},
    "Omagh":            {"lat": 54.5978, "lon": -7.2989,  "country": "Northern Ireland"},
    "Enniskillen":      {"lat": 54.3447, "lon": -7.6328,  "country": "Northern Ireland"},
    "Ballymena":        {"lat": 54.8639, "lon": -6.2789,  "country": "Northern Ireland"},
    "Coleraine":        {"lat": 55.1322, "lon": -6.6683,  "country": "Northern Ireland"},
    "Bangor NI":        {"lat": 54.6536, "lon": -5.6679,  "country": "Northern Ireland"},
    # ── England ──────────────────────────────────────────────────────────────
    "London":           {"lat": 51.5074, "lon": -0.1278,  "country": "England"},
    "Manchester":       {"lat": 53.4808, "lon": -2.2426,  "country": "England"},
    "Birmingham":       {"lat": 52.4862, "lon": -1.8904,  "country": "England"},
    "Leeds":            {"lat": 53.8008, "lon": -1.5491,  "country": "England"},
    "Bristol":          {"lat": 51.4545, "lon": -2.5879,  "country": "England"},
    "Liverpool":        {"lat": 53.4084, "lon": -2.9916,  "country": "England"},
    "Newcastle":        {"lat": 54.9783, "lon": -1.6178,  "country": "England"},
    "Sheffield":        {"lat": 53.3811, "lon": -1.4701,  "country": "England"},
    "Nottingham":       {"lat": 52.9548, "lon": -1.1581,  "country": "England"},
    "Leicester":        {"lat": 52.6369, "lon": -1.1398,  "country": "England"},
    "Coventry":         {"lat": 52.4081, "lon": -1.5106,  "country": "England"},
    "Bradford":         {"lat": 53.7960, "lon": -1.7594,  "country": "England"},
    "Stoke-on-Trent":   {"lat": 53.0027, "lon": -2.1794,  "country": "England"},
    "Derby":            {"lat": 52.9225, "lon": -1.4746,  "country": "England"},
    "Southampton":      {"lat": 50.9097, "lon": -1.4044,  "country": "England"},
    "Portsmouth":       {"lat": 50.8198, "lon": -1.0880,  "country": "England"},
    "Brighton":         {"lat": 50.8225, "lon": -0.1372,  "country": "England"},
    "Hull":             {"lat": 53.7676, "lon": -0.3274,  "country": "England"},
    "Middlesbrough":    {"lat": 54.5742, "lon": -1.2350,  "country": "England"},
    "Sunderland":       {"lat": 54.9069, "lon": -1.3838,  "country": "England"},
    "Oxford":           {"lat": 51.7520, "lon": -1.2577,  "country": "England"},
    "Cambridge":        {"lat": 52.2053, "lon":  0.1218,  "country": "England"},
    "Exeter":           {"lat": 50.7184, "lon": -3.5339,  "country": "England"},
    "Plymouth":         {"lat": 50.3755, "lon": -4.1427,  "country": "England"},
    "Norwich":          {"lat": 52.6309, "lon":  1.2974,  "country": "England"},
    "Ipswich":          {"lat": 52.0567, "lon":  1.1482,  "country": "England"},
    "Peterborough":     {"lat": 52.5695, "lon": -0.2405,  "country": "England"},
    "Milton Keynes":    {"lat": 52.0406, "lon": -0.7594,  "country": "England"},
    "Wolverhampton":    {"lat": 52.5860, "lon": -2.1288,  "country": "England"},
    "Carlisle":         {"lat": 54.8951, "lon": -2.9382,  "country": "England"},
    "York":             {"lat": 53.9590, "lon": -1.0815,  "country": "England"},
    "Lancaster":        {"lat": 54.0466, "lon": -2.7998,  "country": "England"},
    "Blackpool":        {"lat": 53.8142, "lon": -3.0503,  "country": "England"},
    "Reading":          {"lat": 51.4543, "lon": -0.9781,  "country": "England"},
    "Luton":            {"lat": 51.8787, "lon": -0.4200,  "country": "England"},
    "Northampton":      {"lat": 52.2405, "lon": -0.9027,  "country": "England"},
    "Gloucester":       {"lat": 51.8642, "lon": -2.2380,  "country": "England"},
    "Truro":            {"lat": 50.2632, "lon": -5.0510,  "country": "England"},
    "Lincoln":          {"lat": 53.2307, "lon": -0.5406,  "country": "England"},
    # ── Scotland ─────────────────────────────────────────────────────────────
    "Edinburgh":        {"lat": 55.9533, "lon": -3.1883,  "country": "Scotland"},
    "Glasgow":          {"lat": 55.8642, "lon": -4.2518,  "country": "Scotland"},
    "Aberdeen":         {"lat": 57.1497, "lon": -2.0943,  "country": "Scotland"},
    "Dundee":           {"lat": 56.4620, "lon": -2.9707,  "country": "Scotland"},
    "Inverness":        {"lat": 57.4778, "lon": -4.2247,  "country": "Scotland"},
    "Stirling":         {"lat": 56.1165, "lon": -3.9369,  "country": "Scotland"},
    "Perth":            {"lat": 56.3950, "lon": -3.4310,  "country": "Scotland"},
    "Paisley":          {"lat": 55.8456, "lon": -4.4230,  "country": "Scotland"},
    "Ayr":              {"lat": 55.4628, "lon": -4.6293,  "country": "Scotland"},
    "Dumfries":         {"lat": 55.0704, "lon": -3.6052,  "country": "Scotland"},
    "Fort William":     {"lat": 56.8198, "lon": -5.1052,  "country": "Scotland"},
    "Kirkcaldy":        {"lat": 56.1107, "lon": -3.1615,  "country": "Scotland"},
    # ── Wales ─────────────────────────────────────────────────────────────────
    "Cardiff":          {"lat": 51.4816, "lon": -3.1791,  "country": "Wales"},
    "Swansea":          {"lat": 51.6214, "lon": -3.9436,  "country": "Wales"},
    "Newport":          {"lat": 51.5842, "lon": -2.9977,  "country": "Wales"},
    "Wrexham":          {"lat": 53.0461, "lon": -2.9925,  "country": "Wales"},
    "Bangor":           {"lat": 53.2274, "lon": -4.1293,  "country": "Wales"},
    "Aberystwyth":      {"lat": 52.4153, "lon": -4.0829,  "country": "Wales"},
    "Llanelli":         {"lat": 51.6842, "lon": -4.1625,  "country": "Wales"},
    "Merthyr Tydfil":   {"lat": 51.7459, "lon": -3.3785,  "country": "Wales"},
    "Rhyl":             {"lat": 53.3196, "lon": -3.4909,  "country": "Wales"},
    "Caernarfon":       {"lat": 53.1393, "lon": -4.2758,  "country": "Wales"},
}

COUNTRY_COLOURS = {
    "Ireland":          "#169b62",
    "Northern Ireland": "#003078",
    "England":          "#cf142b",
    "Scotland":         "#005eb8",
    "Wales":            "#d62828",
}

# ── Folium map ────────────────────────────────────────────────────────────────
def build_map(selected_city=None):
    m = folium.Map(
        location=[54.2, -4.0],
        zoom_start=6,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )
    for city, info in CITIES.items():
        is_sel  = city == selected_city
        colour  = COUNTRY_COLOURS.get(info["country"], "#333")
        radius  = 9 if is_sel else 5
        weight  = 3 if is_sel else 1.2
        fill_op = 0.95 if is_sel else 0.72

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=radius,
            color=colour,
            weight=weight,
            fill=True,
            fill_color=colour,
            fill_opacity=fill_op,
            tooltip=folium.Tooltip(
                f"<b style='font-family:DM Sans,sans-serif'>{city}</b>"
                f"<br><span style='font-size:11px;color:#888'>{info['country']}</span>",
                sticky=False,
            ),
            popup=folium.Popup(city, parse_html=False),
        ).add_to(m)

        if is_sel:
            folium.Marker(
                location=[info["lat"] + 0.17, info["lon"]],
                icon=folium.DivIcon(
                    html=f"<div style='font-family:DM Sans,sans-serif;font-size:11px;"
                         f"font-weight:600;color:{colour};white-space:nowrap;'>{city}</div>",
                    icon_size=(130, 20),
                    icon_anchor=(65, 0),
                ),
            ).add_to(m)
    return m

# ── Fetch air quality (AQI, PM2.5, PM10, NO₂) ────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_air_quality(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm2_5,pm10,nitrogen_dioxide"
        "&forecast_days=7"
        "&timezone=Europe%2FLondon"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    d = r.json()["hourly"]
    df = pd.DataFrame({
        "time":             pd.to_datetime(d["time"]),
        "european_aqi":     d.get("european_aqi"),
        "pm2_5":            d.get("pm2_5"),
        "pm10":             d.get("pm10"),
        "nitrogen_dioxide": d.get("nitrogen_dioxide"),
    })
    return df

# ── Trend ─────────────────────────────────────────────────────────────────────
def compute_trend(df):
    aqi = df["european_aqi"].dropna()
    if len(aqi) < 12:
        return "stable", "—"
    slope = np.polyfit(np.arange(len(aqi)), aqi, 1)[0]
    per_day = slope * 24
    if per_day > 2:
        return "up",   "Worsening ↑"
    elif per_day < -2:
        return "down", "Improving ↓"
    else:
        return "stable", "Stable →"

# ── 4-panel Plotly chart ──────────────────────────────────────────────────────
def build_chart(df):
    has_no2 = df["nitrogen_dioxide"].notna().any()
    rows    = 4 if has_no2 else 3
    titles  = ["European AQI", "PM2.5 (µg/m³)", "PM10 (µg/m³)"]
    if has_no2:
        titles.append("NO₂ – Nitrogen Dioxide (µg/m³)")

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.045,
        subplot_titles=titles,
    )

    # Colours stored as (hex, rgba-with-alpha) tuples so fillcolor is always valid
    C = {
        "aqi":  ("#1d6fa4", "rgba(29,111,164,0.09)"),
        "pm25": ("#e85d04", "rgba(232,93,4,0.09)"),
        "pm10": ("#7c3aed", "rgba(124,58,237,0.09)"),
        "no2":  ("#0f7a55", "rgba(15,122,85,0.09)"),
    }

    def add_trace(col, name, colour_key, row, fmt):
        line_colour, fill_colour = C[colour_key]
        fig.add_trace(go.Scatter(
            x=df["time"], y=df[col],
            mode="lines", name=name,
            line=dict(color=line_colour, width=1.8),
            fill="tozeroy",
            fillcolor=fill_colour,
            hovertemplate=f"%{{y:{fmt}}}<extra>{name}</extra>",
        ), row=row, col=1)

    add_trace("european_aqi",    "AQI",   "aqi",  1, ".0f")
    add_trace("pm2_5",           "PM2.5", "pm25", 2, ".1f")
    add_trace("pm10",            "PM10",  "pm10", 3, ".1f")
    if has_no2:
        add_trace("nitrogen_dioxide", "NO₂", "no2", 4, ".1f")

    fig.update_layout(
        height=560 if has_no2 else 420,
        margin=dict(l=8, r=8, t=32, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.80)",
        font=dict(family="DM Sans, sans-serif", size=11, color="#4a6a8a"),
        showlegend=False,
        hovermode="x unified",
    )
    for i in range(1, rows + 1):
        fig.update_xaxes(
            showgrid=True, gridcolor="rgba(170,205,230,0.30)",
            zeroline=False, tickformat="%a %d %b",
            tickfont=dict(size=10), row=i, col=1,
        )
        fig.update_yaxes(
            showgrid=True, gridcolor="rgba(170,205,230,0.30)",
            zeroline=False, tickfont=dict(size=10), row=i, col=1,
        )
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=11, color="#7a9ab8", family="DM Sans, sans-serif")
        ann["x"] = 0
    return fig

# ── AQI colour ────────────────────────────────────────────────────────────────
def aqi_colour(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "#aaa"
    if np.isnan(v): return "#aaa"
    if v <= 20: return "#1e8449"
    if v <= 40: return "#d4ac0d"
    if v <= 60: return "#e67e22"
    if v <= 80: return "#c0392b"
    return "#7b241c"

def fmt_val(v, dec=1):
    try:
        f = float(v)
        return "—" if np.isnan(f) else f"{f:.{dec}f}"
    except (TypeError, ValueError):
        return "—"

# ══════════════════════════════════════════════════════════════════════════════
#  LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
  <p class="app-title">🌍 UK & Ireland Air Quality Forecast</p>
  <p class="app-subtitle">
    7-day hourly forecast &nbsp;·&nbsp; European AQI · PM2.5 · PM10 · NO₂
    &nbsp;·&nbsp; 99 locations across Ireland, NI, England, Scotland & Wales
    &nbsp;·&nbsp; Powered by Open-Meteo
  </p>
</div>
""", unsafe_allow_html=True)

col_map, col_data = st.columns([1.15, 0.85], gap="large")

# ── MAP COLUMN ────────────────────────────────────────────────────────────────
with col_map:
    st.markdown('<p class="section-label">Click any marker to load its forecast</p>',
                unsafe_allow_html=True)

    selected = st.session_state.get("selected_city")
    m = build_map(selected_city=selected)

    map_data = st_folium(
        m,
        width=None,
        height=570,
        returned_objects=["last_object_clicked_popup"],
        key="main_map",
    )

    if map_data and map_data.get("last_object_clicked_popup"):
        clicked = map_data["last_object_clicked_popup"]
        if clicked in CITIES:
            st.session_state["selected_city"] = clicked

    # Legend
    legend = '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.7rem;">'
    for country, colour in COUNTRY_COLOURS.items():
        legend += (
            f'<span style="display:inline-flex;align-items:center;gap:5px;'
            f'font-size:0.75rem;color:#3a5a78;background:rgba(255,255,255,0.72);'
            f'padding:2px 9px;border-radius:999px;">'
            f'<span style="width:9px;height:9px;border-radius:50%;background:{colour};'
            f'display:inline-block;flex-shrink:0;"></span>{country}</span>'
        )
    legend += "</div>"
    st.markdown(legend, unsafe_allow_html=True)

# ── DATA COLUMN ───────────────────────────────────────────────────────────────
with col_data:
    active_city = st.session_state.get("selected_city")

    if not active_city:
        st.markdown("""
        <div style="height:340px;display:flex;align-items:center;justify-content:center;">
          <div class="hint" style="max-width:310px;text-align:center;">
            👆 Click any city or town marker on the map to load its 7-day air quality forecast.
            <br><br>
            <span style="font-size:0.76rem;color:#8aaac8;">
              99 locations across Ireland, Northern Ireland,<br>England, Scotland &amp; Wales
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        info = CITIES[active_city]

        with st.spinner(f"Fetching forecast for {active_city}…"):
            try:
                df = fetch_air_quality(info["lat"], info["lon"])
            except Exception as e:
                st.error(f"Could not fetch data: {e}")
                st.stop()

        trend_dir, trend_label = compute_trend(df)
        badge_cls = {"up": "trend-up", "down": "trend-down", "stable": "trend-stable"}[trend_dir]
        lon_dir = "W" if info["lon"] < 0 else "E"

        # City card
        st.markdown(f"""
        <div class="city-card">
          <p class="city-name">{active_city}</p>
          <p class="city-meta">
            {info['country']} &nbsp;·&nbsp;
            {info['lat']:.4f}°N &nbsp; {abs(info['lon']):.4f}°{lon_dir}
          </p>
          <span class="trend-badge {badge_cls}">7-day trend: {trend_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Snapshot metrics
        valid = df.dropna(subset=["european_aqi"])
        if not valid.empty:
            now   = valid.iloc[0]
            aqi_v = now["european_aqi"]
            no2_v = now["nitrogen_dioxide"]
            no2_box = (
                f'<div class="metric-box">'
                f'<div class="metric-label">NO₂</div>'
                f'<div class="metric-value">{fmt_val(no2_v)}</div>'
                f'<div class="metric-unit">µg/m³</div></div>'
            ) if fmt_val(no2_v) != "—" else ""

            st.markdown(f"""
            <div class="metric-row">
              <div class="metric-box">
                <div class="metric-label">AQI (now)</div>
                <div class="metric-value" style="color:{aqi_colour(aqi_v)}">{fmt_val(aqi_v, 0)}</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">PM2.5</div>
                <div class="metric-value">{fmt_val(now['pm2_5'])}</div>
                <div class="metric-unit">µg/m³</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">PM10</div>
                <div class="metric-value">{fmt_val(now['pm10'])}</div>
                <div class="metric-unit">µg/m³</div>
              </div>
              {no2_box}
            </div>
            """, unsafe_allow_html=True)

        # Chart
        st.markdown('<p class="section-label">7-day hourly forecast</p>',
                    unsafe_allow_html=True)
        fig = build_chart(df)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # AQI scale key
        st.markdown("""
        <div style="display:flex;flex-wrap:wrap;gap:0.35rem;margin-top:0.2rem;">
          <span style="font-size:0.70rem;color:#8aaac8;width:100%;font-weight:600;
                       text-transform:uppercase;letter-spacing:0.08em;">European AQI scale</span>
          <span style="font-size:0.72rem;background:#e5f5ec;color:#1e8449;padding:2px 8px;border-radius:999px;">0–20 Good</span>
          <span style="font-size:0.72rem;background:#fef9e7;color:#d4ac0d;padding:2px 8px;border-radius:999px;">21–40 Fair</span>
          <span style="font-size:0.72rem;background:#fdf2e9;color:#e67e22;padding:2px 8px;border-radius:999px;">41–60 Moderate</span>
          <span style="font-size:0.72rem;background:#fdedec;color:#c0392b;padding:2px 8px;border-radius:999px;">61–80 Poor</span>
          <span style="font-size:0.72rem;background:#f5eef8;color:#7b241c;padding:2px 8px;border-radius:999px;">81+ Very Poor</span>
        </div>
        """, unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-box">
  <strong>⚠️ Disclaimer:</strong>&nbsp; This tool is for indicative purposes only. Pollution forecasts
  are predictions based on available data and may not be fully accurate, as levels can be influenced
  by weather conditions, local events, and other external factors. This tool has been developed to help
  people identify general air quality trends in advance.
</div>
""", unsafe_allow_html=True)

# ── Pavan Clean Air footer ────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
  <div class="brand">Pavan Clean Air</div>
  <div class="tagline">
    Get in touch today to get your tailored air purifier ready for hybrid, indoor and outdoor spaces.
  </div>
</div>
""", unsafe_allow_html=True)
