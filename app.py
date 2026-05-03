# app.py (FINAL VERSION - STABLE & PROFESSIONAL)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="NYC Taxi Pro Dashboard", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("🚖 NYC Taxi Pro Dashboard")
st.markdown("### Advanced Statistical Insights for Pricing & Demand Optimization")

# -----------------------------
# LOAD DATA (SAFE + FAST)
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("yellow_tripdata_2020-06.csv")

        # Basic Cleaning
        df = df[(df['trip_distance'] > 0) & (df['fare_amount'] > 0)]

        # Datetime conversion
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')

        # Drop invalid datetime rows
        df = df.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])

        # Feature Engineering
        df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds()/60

        # Avoid division errors
        df = df[df['trip_duration'] > 0]

        df['trip_speed'] = df['trip_distance'] / (df['trip_duration']/60)
        df['fare_per_km'] = df['fare_amount'] / df['trip_distance']
        df['tip_percentage'] = (df['tip_amount']/df['fare_amount'])*100
        df['hour'] = df['tpep_pickup_datetime'].dt.hour

        # SAFE SAMPLING (🔥 FIXED)
        df = df.sample(min(50000, len(df)), random_state=42)

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# Stop app if data not loaded
if df.empty:
    st.stop()

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("🔎 Filters")

hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
filtered_df = df[(df['hour'] >= hour_range[0]) & (df['hour'] <= hour_range[1])]

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Key Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Avg Fare", f"{filtered_df['fare_amount'].mean():.2f}")
c2.metric("📏 Avg Distance", f"{filtered_df['trip_distance'].mean():.2f}")
c3.metric("⏱ Avg Duration", f"{filtered_df['trip_duration'].mean():.2f}")
c4.metric("💡 Avg Tip %", f"{filtered_df['tip_percentage'].mean():.2f}")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "📈 Trends", "🗺️ Map", "🧠 Insights"])

# -----------------------------
# TAB 1: ANALYSIS
# -----------------------------
with tab1:
    st.subheader("Distance vs Fare")

    fig = px.scatter(
        filtered_df,
        x="trip_distance",
        y="fare_amount",
        color="trip_duration",
        title="Distance vs Fare Relationship"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2: TRENDS
# -----------------------------
with tab2:
    st.subheader("Demand Trends")

    demand = filtered_df['hour'].value_counts().sort_index()

    fig = px.line(
        x=demand.index,
        y=demand.values,
        labels={'x': 'Hour', 'y': 'Trips'},
        title="Trips by Hour"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speed Trends")

    speed = filtered_df.groupby('hour')['trip_speed'].mean()

    fig2 = px.line(
        x=speed.index,
        y=speed.values,
        title="Average Speed by Hour"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TAB 3: MAP (SAFE)
# -----------------------------
with tab3:
    st.subheader("Trip Locations")

    if 'pickup_latitude' in df.columns and 'pickup_longitude' in df.columns:
        map_df = df[['pickup_latitude', 'pickup_longitude']].dropna()

        if len(map_df) > 0:
            map_df = map_df.sample(min(2000, len(map_df)), random_state=42)

            st.map(map_df.rename(columns={
                'pickup_latitude': 'lat',
                'pickup_longitude': 'lon'
            }))
        else:
            st.warning("No valid location data available")
    else:
        st.warning("Map columns not found in dataset")

# -----------------------------
# TAB 4: INSIGHTS
# -----------------------------
with tab4:
    st.subheader("Correlation Analysis")

    corr = filtered_df[['trip_distance', 'fare_amount', 'trip_duration']].corr()
    st.dataframe(corr)

    st.subheader("Hypothesis Testing")

    peak = df[(df['hour'] >= 7) & (df['hour'] <= 10)]['fare_amount']
    non_peak = df[(df['hour'] < 7) | (df['hour'] > 10)]['fare_amount']

    t_stat, p_val = stats.ttest_ind(peak, non_peak)

    st.write(f"P-value: {p_val:.5f}")

    if p_val < 0.05:
        st.success("Significant difference → Peak pricing exists")
    else:
        st.warning("No significant difference")

    # SMART INSIGHTS
    st.subheader("Smart Insights")

    if filtered_df['trip_speed'].mean() < 20:
        st.info("🚦 Traffic congestion is high")
    else:
        st.success("🚀 Traffic flow is smooth")

    if filtered_df['fare_per_km'].std() > 2:
        st.warning("💰 Pricing inconsistency detected")

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
st.subheader("📥 Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="taxi_data.csv",
    mime="text/csv"
)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("✨ Built by Beesam Gayathri | Advanced Statistical Project")
