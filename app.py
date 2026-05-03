# app.py (UPGRADED UI)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="NYC Taxi Dashboard", layout="wide")

# -----------------------------
# CUSTOM STYLE (🔥 UI BOOST)
# -----------------------------
st.markdown("""
<style>
.metric-box {
    background-color: #111;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🚖 NYC Taxi Analytics Dashboard")
st.markdown("### Advanced Statistical Insights for Business Optimization")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("yellow_tripdata_2020-06.csv")

    df = df[(df['trip_distance'] > 0) & (df['fare_amount'] > 0)]

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds()/60
    df['trip_speed'] = df['trip_distance'] / (df['trip_duration']/60)
    df['fare_per_km'] = df['fare_amount'] / df['trip_distance']
    df['tip_percentage'] = (df['tip_amount']/df['fare_amount'])*100
    df['hour'] = df['tpep_pickup_datetime'].dt.hour

    return df

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔎 Filters")

hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
filtered_df = df[(df['hour'] >= hour_range[0]) & (df['hour'] <= hour_range[1])]

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Avg Fare", f"{filtered_df['fare_amount'].mean():.2f}")
col2.metric("📏 Avg Distance", f"{filtered_df['trip_distance'].mean():.2f}")
col3.metric("⏱ Avg Duration", f"{filtered_df['trip_duration'].mean():.2f}")
col4.metric("💡 Avg Tip %", f"{filtered_df['tip_percentage'].mean():.2f}")

# -----------------------------
# TABS (🔥 PROFESSIONAL LOOK)
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📈 Trends", "🧠 Insights"])

# -----------------------------
# TAB 1: ANALYSIS
# -----------------------------
with tab1:
    st.subheader("Fare vs Distance")

    fig = px.scatter(filtered_df.sample(5000),
                     x="trip_distance",
                     y="fare_amount",
                     color="trip_duration",
                     title="Distance vs Fare")

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2: TRENDS
# -----------------------------
with tab2:
    st.subheader("Demand by Hour")

    demand = filtered_df['hour'].value_counts().sort_index()

    fig = px.line(x=demand.index, y=demand.values,
                  labels={'x':'Hour','y':'Trips'},
                  title="Trips by Hour")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speed Trends")

    speed = filtered_df.groupby('hour')['trip_speed'].mean()

    fig2 = px.line(x=speed.index, y=speed.values,
                   title="Average Speed by Hour")

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TAB 3: INSIGHTS
# -----------------------------
with tab3:
    st.subheader("Statistical Insights")

    # Correlation
    corr = filtered_df[['trip_distance','fare_amount','trip_duration']].corr()

    st.write("### Correlation Matrix")
    st.dataframe(corr)

    # Hypothesis Test
    peak = df[(df['hour']>=7)&(df['hour']<=10)]['fare_amount']
    non_peak = df[(df['hour']<7)|(df['hour']>10)]['fare_amount']

    t_stat, p_val = stats.ttest_ind(peak, non_peak)

    st.write("### Peak vs Non-Peak Pricing")
    st.write(f"P-value: {p_val:.5f}")

    if p_val < 0.05:
        st.success("Significant difference → Peak pricing exists")
    else:
        st.warning("No significant difference")

    st.markdown("""
    ### 💡 Key Insights
    - 🚖 Inefficient trips exist (high duration, low distance)
    - 💰 Pricing varies across trips → inconsistency
    - 📊 Peak hours show high demand and congestion
    - 🎯 Few trips generate most revenue
    """)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("✨ Developed by Beesam Gayathri")
