import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK & Ireland Air Quality",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Force white background everywhere */
  html, body, [data-testid="stApp"],
  [data-testid="stAppViewContainer"],
  [data-testid="block-container"],
  section.main, .stMain, .main {
      background-color: #ffffff !important;
  }

  /* Hide Streamlit chrome */
  #MainMenu, header, footer { visibility: hidden; }
  [data-testid="stToolbar"] { display: none; }

  /* Typography */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
  html, body, * { font-family: 'DM Sans', sans-serif !important; }

  /* Remove default padding */
  .block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1200px; }

  /* Header */
  .app-header {
      border-bottom: 2px solid #111;
      padding-bottom: 0.75rem;
      margin-bottom: 1.5rem;
  }
  .app-title {
      font-size: 1.55rem;
      font-weight: 600;
      color: #111;
      letter-spacing: -0.02em;
      margin: 0;
  }
  .app-subtitle {
      font-size: 0.82rem;
      color: #888;
      margin-top: 0.2rem;
      font-weight: 400;
  }

  /* City info card */
  .city-card {
      background: #f7f7f7;
      border-radius: 10px;
      padding: 1rem 1.25rem;
      margin-bottom: 1rem;
  }
  .city-name {
      font-size: 1.3rem;
      font-weight: 600;
      color: #111;
      margin: 0;
  }
  .city-meta {
      font-size: 0.78rem;
      color: #888;
      font-family: 'DM Mono', monospace !important;
      margin-top: 0.2rem;
  }

  /* Trend badge */
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
  .trend-up   { background: #ffe5e5; color: #c0392b; }
  .trend-down { background: #e5f5ec; color: #1e8449; }
  .trend-stable { background: #f0f0f0; color: #555; }

  /* Section label */
  .section-label {
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #aaa;
      margin-bottom: 0.4rem;
  }

  /* Instruction hint */
  .hint {
      background: #f7f7f7;
      border-left: 3px solid #ddd;
      border-radius: 4px;
      padding: 0.65rem 0.9rem;
      font-size: 0.82rem;
      color: #666;
  }

  /* Metric boxes */
  .metric-row {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
  }
  .metric-box {
      flex: 1;
      min-width: 100px;
      background: #f7f7f7;
      border-radius: 8px;
      padding: 0.65rem 0.9rem;
  }
  .metric-label {
      font-size: 0.72rem;
      color: #aaa;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
  }
  .metric-value {
      font-size: 1.35rem;
      font-weight: 600;
      color: #111;
      font-family: 'DM Mono', monospace !important;
  }
  .metric-unit {
      font-size: 0.72rem;
      color: #aaa;
      font-family: 'DM Mono', monospace !important;
  }

  /* Plotly chart container */
  .chart-wrapper {
      border: 1px solid #eee;
      border-radius: 10px;
      overflow: hidden;
      padding: 0.5rem 0.25rem;
  }
</style>
""", unsafe_allow_html=True)

# ── City data ─────────────────────────────────────────────────────────────────
CITIES = {
    # Ireland
    "Dublin":       {"lat": 53.3498, "lon": -6.2603,  "country": "Ireland"},
    "Cork":         {"lat": 51.8985, "lon": -8.4756,  "country": "Ireland"},
    "Galway":       {"lat": 53.2707, "lon": -9.0568,  "country": "Ireland"},
    "Limerick":     {"lat": 52.6638, "lon": -8.6267,  "country": "Ireland"},
    "Waterford":    {"lat": 52.2593, "lon": -7.1101,  "country": "Ireland"},
    "Kilkenny":     {"lat": 52.6541, "lon": -7.2448,  "country": "Ireland"},
    # Northern Ireland
    "Belfast":      {"lat": 54.5973, "lon": -5.9301,  "country": "Northern Ireland"},
    "Derry":        {"lat": 54.9966, "lon": -7.3086,  "country": "Northern Ireland"},
    # England
    "London":       {"lat": 51.5074, "lon": -0.1278,  "country": "England"},
    "Manchester":   {"lat": 53.4808, "lon": -2.2426,  "country": "England"},
    "Birmingham":   {"lat": 52.4862, "lon": -1.8904,  "country": "England"},
    "Leeds":        {"lat": 53.8008, "lon": -1.5491,  "country": "England"},
    "Bristol":      {"lat": 51.4545, "lon": -2.5879,  "country": "England"},
    "Liverpool":    {"lat": 53.4084, "lon": -2.9916,  "country": "England"},
    "Newcastle":    {"lat": 54.9783, "lon": -1.6178,  "country": "England"},
    # Scotland
    "Edinburgh":    {"lat": 55.9533, "lon": -3.1883,  "country": "Scotland"},
    "Glasgow":      {"lat": 55.8642, "lon": -4.2518,  "country": "Scotland"},
    # Wales
    "Cardiff":      {"lat": 51.4816, "lon": -3.1791,  "country": "Wales"},
    "Swansea":      {"lat": 51.6214, "lon": -3.9436,  "country": "Wales"},
}

COUNTRY_COLOURS = {
    "Ireland":          "#169b62",   # Irish green
    "Northern Ireland": "#003078",   # UK blue (distinct shade)
    "England":          "#cf142b",   # English red
    "Scotland":         "#005eb8",   # Scottish blue
    "Wales":            "#d62828",   # Welsh red
}

# ── Helper: build Folium map ──────────────────────────────────────────────────
def build_map(selected_city=None):
    m = folium.Map(
        location=[54.0, -4.5],
        zoom_start=6,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )
    for city, info in CITIES.items():
        is_selected = city == selected_city
        colour = COUNTRY_COLOURS.get(info["country"], "#333")
        radius = 10 if is_selected else 7
        weight = 3 if is_selected else 1.5
        fill_opacity = 0.95 if is_selected else 0.75

        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=radius,
            color=colour,
            weight=weight,
            fill=True,
            fill_color=colour,
            fill_opacity=fill_opacity,
            tooltip=folium.Tooltip(
                f"<b style='font-family:DM Sans,sans-serif'>{city}</b>"
                f"<br><span style='font-size:11px;color:#888'>{info['country']}</span>",
                sticky=False,
            ),
            popup=folium.Popup(city, parse_html=False),
        ).add_to(m)

        # Label for selected city
        if is_selected:
            folium.Marker(
                location=[info["lat"] + 0.18, info["lon"]],
                icon=folium.DivIcon(
                    html=f"<div style='font-family:DM Sans,sans-serif;font-size:11px;"
                         f"font-weight:600;color:{colour};white-space:nowrap;'>{city}</div>",
                    icon_size=(100, 20),
                    icon_anchor=(50, 0),
                ),
            ).add_to(m)
    return m

# ── Helper: fetch air quality ─────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_air_quality(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm2_5,pm10"
        "&forecast_days=7"
        "&timezone=Europe%2FLondon"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame({
        "time":         pd.to_datetime(data["hourly"]["time"]),
        "european_aqi": data["hourly"]["european_aqi"],
        "pm2_5":        data["hourly"]["pm2_5"],
        "pm10":         data["hourly"]["pm10"],
    })
    return df

# ── Helper: trend analysis ────────────────────────────────────────────────────
def compute_trend(df):
    aqi = df["european_aqi"].dropna()
    if len(aqi) < 12:
        return "stable", "—"
    x = np.arange(len(aqi))
    slope = np.polyfit(x, aqi, 1)[0]
    per_day = slope * 24
    if per_day > 2:
        return "up",   "Worsening ↑"
    elif per_day < -2:
        return "down", "Improving ↓"
    else:
        return "stable", "Stable →"

# ── Helper: build Plotly chart ────────────────────────────────────────────────
def build_chart(df, city_name):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("European AQI", "PM2.5 (µg/m³)", "PM10 (µg/m³)"),
    )

    COLOUR_AQI  = "#2563eb"
    COLOUR_PM25 = "#e85d04"
    COLOUR_PM10 = "#7c3aed"

    # AQI
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["european_aqi"],
        mode="lines", name="AQI",
        line=dict(color=COLOUR_AQI, width=1.8),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.07)",
        hovertemplate="%{y:.0f}<extra>AQI</extra>",
    ), row=1, col=1)

    # PM2.5
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["pm2_5"],
        mode="lines", name="PM2.5",
        line=dict(color=COLOUR_PM25, width=1.8),
        fill="tozeroy", fillcolor="rgba(232,93,4,0.07)",
        hovertemplate="%{y:.1f} µg/m³<extra>PM2.5</extra>",
    ), row=2, col=1)

    # PM10
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["pm10"],
        mode="lines", name="PM10",
        line=dict(color=COLOUR_PM10, width=1.8),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.07)",
        hovertemplate="%{y:.1f} µg/m³<extra>PM10</extra>",
    ), row=3, col=1)

    fig.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", size=11, color="#555"),
        showlegend=False,
        hovermode="x unified",
    )

    for i in range(1, 4):
        fig.update_xaxes(
            showgrid=True, gridcolor="#f0f0f0",
            zeroline=False, tickformat="%a %d %b",
            tickfont=dict(size=10), row=i, col=1,
        )
        fig.update_yaxes(
            showgrid=True, gridcolor="#f0f0f0",
            zeroline=False,
            tickfont=dict(size=10), row=i, col=1,
        )

    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=11, color="#888", family="DM Sans, sans-serif")
        ann["x"] = 0

    return fig

# ── App layout ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <p class="app-title">🌍 UK & Ireland Air Quality Forecast</p>
  <p class="app-subtitle">7-day hourly forecast · European AQI · PM2.5 · PM10 · Powered by Open-Meteo</p>
</div>
""", unsafe_allow_html=True)

# Two-column layout
col_map, col_data = st.columns([1.1, 0.9], gap="large")

with col_map:
    st.markdown('<p class="section-label">Click a city marker</p>', unsafe_allow_html=True)

    # Build map with current selection (if any)
    selected = st.session_state.get("selected_city")
    m = build_map(selected_city=selected)

    map_data = st_folium(
        m,
        width=None,          # fill column
        height=540,
        returned_objects=["last_object_clicked_popup"],
        key="main_map",
    )

    # Capture click
    clicked_city = None
    if map_data and map_data.get("last_object_clicked_popup"):
        clicked_city = map_data["last_object_clicked_popup"]
        if clicked_city in CITIES:
            st.session_state["selected_city"] = clicked_city

    # Colour legend
    st.markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.6rem;">
    """, unsafe_allow_html=True)
    for country, colour in COUNTRY_COLOURS.items():
        st.markdown(
            f'<span style="display:inline-flex;align-items:center;gap:5px;'
            f'font-size:0.75rem;color:#555;">'
            f'<span style="width:10px;height:10px;border-radius:50%;'
            f'background:{colour};display:inline-block;"></span>{country}</span>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col_data:
    active_city = st.session_state.get("selected_city")

    if not active_city:
        st.markdown("""
        <div style="height:300px;display:flex;align-items:center;justify-content:center;">
          <div class="hint" style="max-width:280px;text-align:center;">
            👆 Click any city marker on the map to load its 7-day air quality forecast.
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

        # City card
        st.markdown(f"""
        <div class="city-card">
          <p class="city-name">{active_city}</p>
          <p class="city-meta">{info['country']} · {info['lat']:.4f}°N, {abs(info['lon']):.4f}°{'W' if info['lon']<0 else 'E'}</p>
          <span class="trend-badge {badge_cls}">7-day trend: {trend_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Current snapshot metrics
        now_row = df.dropna(subset=["european_aqi"]).iloc[0] if not df.empty else None
        if now_row is not None:
            aqi_now  = now_row["european_aqi"]
            pm25_now = now_row["pm2_5"]
            pm10_now = now_row["pm10"]

            # AQI colour
            def aqi_colour(v):
                if v is None: return "#aaa"
                if v <= 20:  return "#1e8449"
                if v <= 40:  return "#f39c12"
                if v <= 60:  return "#e67e22"
                if v <= 80:  return "#c0392b"
                return "#7b241c"

            st.markdown(f"""
            <div class="metric-row">
              <div class="metric-box">
                <div class="metric-label">AQI (now)</div>
                <div class="metric-value" style="color:{aqi_colour(aqi_now)}">{int(aqi_now) if aqi_now else '—'}</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">PM2.5</div>
                <div class="metric-value">{f'{pm25_now:.1f}' if pm25_now else '—'}</div>
                <div class="metric-unit">µg/m³</div>
              </div>
              <div class="metric-box">
                <div class="metric-label">PM10</div>
                <div class="metric-value">{f'{pm10_now:.1f}' if pm10_now else '—'}</div>
                <div class="metric-unit">µg/m³</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Chart
        st.markdown('<p class="section-label">7-day hourly forecast</p>', unsafe_allow_html=True)
        fig = build_chart(df, active_city)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # AQI key
        st.markdown("""
        <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:0.25rem;">
          <span style="font-size:0.7rem;color:#aaa;width:100%;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">European AQI scale</span>
          <span style="font-size:0.72rem;background:#e5f5ec;color:#1e8449;padding:2px 8px;border-radius:999px;">0–20 Good</span>
          <span style="font-size:0.72rem;background:#fef9e7;color:#f39c12;padding:2px 8px;border-radius:999px;">21–40 Fair</span>
          <span style="font-size:0.72rem;background:#fdf2e9;color:#e67e22;padding:2px 8px;border-radius:999px;">41–60 Moderate</span>
          <span style="font-size:0.72rem;background:#fdedec;color:#c0392b;padding:2px 8px;border-radius:999px;">61–80 Poor</span>
          <span style="font-size:0.72rem;background:#f5eef8;color:#7b241c;padding:2px 8px;border-radius:999px;">81+ Very Poor</span>
        </div>
        """, unsafe_allow_html=True)
