import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go

from mqtt_handler import HomeMQTTClient, sensor_data, ROOMS

mqtt_client = HomeMQTTClient()
mqtt_client.start()

st.set_page_config(page_title="🏠 Home Climate Dashboard", layout="wide")
st.title("🏠 Home Climate Dashboard")

with st.sidebar:
    st.subheader("🔄 Refresh Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    if auto_refresh:
        interval = st.slider("Interval (seconds)", 5, 60, 15)
        st_autorefresh(interval * 1000, key="auto_refresh")
    else:
        st.button("Refresh Now")

if "history" not in st.session_state:
    st.session_state.history = {
        room: {"timestamp": [], "temperature": [], "humidity": []}
        for room in ROOMS
    }
    st.session_state.last_append = None

ts = sensor_data.get("timestamp")
if ts and ts != st.session_state.last_append:
    for room in ROOMS:
        vals = sensor_data[room]
        st.session_state.history[room]["timestamp"].append(ts)
        try:
            st.session_state.history[room]["temperature"].append(float(vals["temperature"]))
        except (TypeError, ValueError):
            st.session_state.history[room]["temperature"].append(None)
        try:
            st.session_state.history[room]["humidity"].append(float(vals["humidity"]))
        except (TypeError, ValueError):
            st.session_state.history[room]["humidity"].append(None)
    st.session_state.last_append = ts

dfs = {
    room: pd.DataFrame(st.session_state.history[room]).set_index("timestamp")
    for room in ROOMS
}

rooms_tab, stats_tab = st.tabs(["Rooms", "Statistics"])

with rooms_tab:
    st.header("🏠 Rooms Overview")
    cols = st.columns(len(ROOMS), gap="small")
    for col, room in zip(cols, ROOMS):
        with col:
            st.subheader(room.capitalize())
            temp = sensor_data[room]["temperature"]
            hum  = sensor_data[room]["humidity"]

            gauge_cols = st.columns(2, gap="small")
            with gauge_cols[0]:
                if temp is not None:
                    try:
                        t = float(temp)
                        fig_t = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=t,
                            title={'text': "Temperature (°C)"},
                            gauge={
                                'axis': {'range': [0, 50]},
                                'steps': [
                                    {'range': [0, 18], 'color': "lightblue"},
                                    {'range': [18, 24], 'color': "lightgreen"},
                                    {'range': [24, 30], 'color': "orange"},
                                    {'range': [30, 50], 'color': "red"}
                                ]
                            }
                        ))
                        st.plotly_chart(fig_t, use_container_width=True)
                    except ValueError:
                        st.error("Invalid temperature")
                else:
                    st.write("Temp: —")

            with gauge_cols[1]:
                if hum is not None:
                    try:
                        h = float(hum)
                        fig_h = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=h,
                            title={'text': "Humidity (%)"},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'steps': [
                                    {'range': [0, 30], 'color': "orange"},
                                    {'range': [30, 60], 'color': "lightgreen"},
                                    {'range': [60, 100], 'color': "lightblue"}
                                ]
                            }
                        ))
                        st.plotly_chart(fig_h, use_container_width=True)
                    except ValueError:
                        st.error("Invalid humidity")
                else:
                    st.write("Hum: —")

            with st.expander("▶ Controls", expanded=False):
                spray = sensor_data[room]["sprayer"] or "OFF"
                heat  = sensor_data[room]["heater"]  or "OFF"
                ctrl_cols = st.columns(2, gap="small")
                if ctrl_cols[0].button(
                    f"{'⏸ Stop' if spray=='ON' else '▶ Start'} Sprayer", key=f"{room}-spray"):
                    mqtt_client.publish_command(room, "sprayer", "OFF" if spray=="ON" else "ON")
                if ctrl_cols[1].button(
                    f"{'⏸ Stop' if heat=='ON' else '▶ Start'} Heater", key=f"{room}-heat"):
                    mqtt_client.publish_command(room, "heater", "OFF" if heat=="ON" else "ON")

            st.caption(f"Last update: {ts or '—'}")
            st.markdown("---")

with stats_tab:
    st.header("📊 All Rooms Heatmap Statistics")
    timestamps = dfs[ROOMS[0]].index.tolist()
    temp_matrix = [dfs[room]["temperature"].fillna(0).tolist() for room in ROOMS]
    fig_temp = go.Figure(go.Heatmap(
        z=temp_matrix,
        x=timestamps,
        y=[r.capitalize() for r in ROOMS],
        colorscale="RdBu",
        colorbar=dict(title="°C")
    ))
    fig_temp.update_layout(title="Temperature Over Time", xaxis_nticks=20)
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("---")

    hum_matrix = [dfs[room]["humidity"].fillna(0).tolist() for room in ROOMS]
    fig_hum = go.Figure(go.Heatmap(
        z=hum_matrix,
        x=timestamps,
        y=[r.capitalize() for r in ROOMS],
        colorscale="Blues",
        colorbar=dict(title="%")
    ))
    fig_hum.update_layout(title="Humidity Over Time", xaxis_nticks=20)
    st.plotly_chart(fig_hum, use_container_width=True)
