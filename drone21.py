import streamlit as st
import random
import time
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
from datetime import datetime

st.set_page_config(page_title="Drone Dashboard", layout="wide")

# Session state initialization
if 'alt' not in st.session_state:
    st.session_state.alt = random.uniform(100, 200)
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Altitude", "Battery", "Temperature"])
if 'page' not in st.session_state:
    st.session_state.page = "ℹ️ Info"

# Custom styles
st.markdown("""
    <style>
    .stRadio > div { flex-direction: column; gap: 1rem; }
    [data-testid="stSidebar"] .stRadio label {
        font-weight: 600;
        font-size: 18px;
        padding: 8px 12px;
        border-radius: 8px;
        background: linear-gradient(to right, #f5f7fa, #c3cfe2);
        transition: 0.3s ease;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    .metric-card {
        border-radius: 12px;
        padding: 16px;
        background-color: #ffffff;
        color: black;
        font-weight: bold;
        text-align: center;
        height: 100%;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 14px;
        margin-bottom: 5px;
        opacity: 0.85;
    }
    .metric-value {
        font-size: 20px;
    }
    .sidebar-footer {
        position: fixed;
        bottom: 10px;
        left: 16px;
        font-size: 13px;
        opacity: 0.7;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom: 10px;'>🌈 Drone Monitor</h2>", unsafe_allow_html=True)
    menu = st.radio("Navigation", ["ℹ️ Info", "📊 Graph", "🗺️ Location"],
                    index=["ℹ️ Info", "📊 Graph", "🗺️ Location"].index(st.session_state.page),
                    label_visibility="collapsed")
    st.session_state.page = menu
    now = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
    st.markdown(f"<div class='sidebar-footer'>📅 {now}</div>", unsafe_allow_html=True)

# Telemetry data generation
def generate_data():
    battery = round(random.uniform(7.4, 12.6), 2)
    roll = round(random.uniform(-180, 180), 2)
    pitch = round(random.uniform(-90, 90), 2)
    yaw = round(random.uniform(-180, 180), 2)
    temp = round(random.uniform(20, 40), 1)
    alt_change = random.uniform(-1, 2)
    st.session_state.alt = max(0, min(500, st.session_state.alt + alt_change))
    altitude = round(st.session_state.alt, 2)
    conn = random.choice(["Excellent", "Poor", "No Signal"])
    lat, lon = 20.5937, 78.9629  # Center of India
    return {"Battery": battery, "Roll": roll, "Pitch": pitch, "Yaw": yaw,
            "Temp": temp, "Altitude": altitude, "Connection": conn,
            "Lat": lat, "Lon": lon}

data = generate_data()
st.session_state.history.loc[len(st.session_state.history)] = [
    data["Altitude"], data["Battery"], data["Temp"]
]

# Metric card template
def colored_card(title, value):
    return f"""<div class='metric-card'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value'>{value}</div>
    </div>"""

# Info View
if menu.startswith("ℹ️"):
    st.markdown("<h2 style='text-align:center; color:#2d6cdf;'>📡 Drone Overview</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col7 = st.columns(1)[0]

    with col1: st.markdown(colored_card("🔋 Battery", f"{data['Battery']} V"), unsafe_allow_html=True)
    with col2: st.markdown(colored_card("🌀 Roll", f"{data['Roll']}°"), unsafe_allow_html=True)
    with col3: st.markdown(colored_card("🧭 Pitch", f"{data['Pitch']}°"), unsafe_allow_html=True)
    with col4: st.markdown(colored_card("🛰️ Yaw", f"{data['Yaw']}°"), unsafe_allow_html=True)
    with col5: st.markdown(colored_card("🌡️ Temp", f"{data['Temp']} °C"), unsafe_allow_html=True)
    with col6: st.markdown(colored_card("⛰️ Altitude", f"{data['Altitude']} m"), unsafe_allow_html=True)
    with col7: st.markdown(colored_card("📶 Connection", data["Connection"]), unsafe_allow_html=True)

    st.markdown("### 🚁 3D Drone View")
    fig = go.Figure(data=[go.Scatter3d(
        x=[0], y=[0], z=[data["Altitude"]],
        mode='markers',
        marker=dict(size=12, color='red'),
        name='Drone'
    )])
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X'), yaxis=dict(title='Y'), zaxis=dict(title='Altitude'),
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Graph View
elif menu.startswith("📊"):
    st.markdown("<h2 style='text-align:center; color:#16a085;'>📈 Live Graph</h2>", unsafe_allow_html=True)
    history = st.session_state.history.tail(50)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=history["Altitude"], name="Altitude", line=dict(color="royalblue")))
    fig.add_trace(go.Scatter(y=history["Battery"], name="Battery", line=dict(color="orange")))
    fig.add_trace(go.Scatter(y=history["Temperature"], name="Temperature", line=dict(color="green")))
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        height=400,
        legend=dict(orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

# Location View - Focus on India
elif menu.startswith("🗺️"):
    st.markdown("<h2 style='text-align:center; color:#c0392b;'>🌍 Drone Location - India</h2>", unsafe_allow_html=True)

    india_view = pdk.ViewState(
        latitude=data["Lat"],
        longitude=data["Lon"],
        zoom=4.5,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame({'lat': [data["Lat"]], 'lon': [data["Lon"]]}),
        get_position='[lon, lat]',
        get_color='[255, 0, 0, 160]',
        get_radius=50000,
    )

    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=india_view,
        layers=[layer],
    )

    st.pydeck_chart(r)

# Auto-refresh
if st.session_state.page in ["ℹ️ Info", "📊 Graph"]:
    time.sleep(1)
    st.rerun()
