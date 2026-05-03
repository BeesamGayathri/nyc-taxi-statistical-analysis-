import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="NYC Taxi Pro Dashboard", layout="wide")

# -----------------------------
# STYLE (🔥 PREMIUM LOOK)
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🚖 NYC Taxi Pro Dashboard")
st.markdown("### Data-Driven Insights for Pricing & Demand Optimization")

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

    return df.sample(50000)  # ⚡ speed optimization

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔎 Filters")

hour = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
filtered_df = df[(df['hour'] >= hour[0]) & (df['hour'] <= hour[1])]

# -----------------------------
# KPIs
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
# ANALYSIS
# -----------------------------
with tab1:
    fig = px.scatter(filtered_df,
                     x="trip_distance",
                     y="fare_amount",
                     color="trip_duration",
                     title="Distance vs Fare")

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TRENDS
# -----------------------------
with tab2:
    demand = filtered_df['hour'].value_counts().sort_index()

    fig = px.line(x=demand.index, y=demand.values,
                  labels={'x':'Hour','y':'Trips'},
                  title="Trips by Hour")

    st.plotly_chart(fig, use_container_width=True)

    speed = filtered_df.groupby('hour')['trip_speed'].mean()

    fig2 = px.line(x=speed.index, y=speed.values,
                   title="Average Speed by Hour")

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# MAP (🔥 WOW FEATURE)
# -----------------------------
with tab3:
    st.subheader("NYC Trip Locations")

    if 'pickup_longitude' in filtered_df.columns:
        map_df = filtered_df[['pickup_latitude','pickup_longitude']].dropna().sample(2000)

        st.map(map_df.rename(columns={
            'pickup_latitude':'lat',
            'pickup_longitude':'lon'
        }))
    else:
        st.warning("Map data not available in dataset")

# -----------------------------
# INSIGHTS + AI STYLE
# -----------------------------
with tab4:
    st.subheader("🔗 Correlation")

    corr = filtered_df[['trip_distance','fare_amount','trip_duration']].corr()
    st.dataframe(corr)

    st.subheader("🧪 Hypothesis Testing")

    peak = df[(df['hour']>=7)&(df['hour']<=10)]['fare_amount']
    non_peak = df[(df['hour']<7)|(df['hour']>10)]['fare_amount']

    t_stat, p_val = stats.ttest_ind(peak, non_peak)

    st.write(f"P-value: {p_val:.5f}")

    if p_val < 0.05:
        st.success("Peak pricing exists (Significant)")
    else:
        st.warning("No strong difference")

    # 🤖 AUTO INSIGHTS
    st.subheader("🤖 Smart Insights")

    avg_speed = filtered_df['trip_speed'].mean()

    if avg_speed < 20:
        st.info("🚦 Traffic congestion is high during selected hours")
    else:
        st.success("🚀 Traffic flow is smooth")

    if filtered_df['fare_per_km'].std() > 2:
        st.warning("💰 Pricing inconsistency detected")

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
st.subheader("📥 Download Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='taxi_data.csv',
    mime='text/csv'
)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("✨ Built by Beesam Gayathri | Advanced Statistical Project")
