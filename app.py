# app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

st.set_page_config(page_title="NYC Taxi Analysis", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("🚖 NYC Taxi Trip Analysis Dashboard")
st.markdown("### Advanced Statistical Analysis for Pricing & Demand Insights")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("yellow_tripdata_2020-06.csv")

    # Basic Cleaning
    df = df[df['trip_distance'] > 0]
    df = df[df['fare_amount'] > 0]

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    # Feature Engineering
    df['trip_duration'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds()/60
    df['trip_speed'] = df['trip_distance'] / (df['trip_duration']/60)
    df['fare_per_km'] = df['fare_amount'] / df['trip_distance']
    df['tip_percentage'] = (df['tip_amount']/df['fare_amount'])*100
    df['hour'] = df['tpep_pickup_datetime'].dt.hour
    df['day_type'] = df['tpep_pickup_datetime'].dt.dayofweek.apply(lambda x: 'Weekend' if x>=5 else 'Weekday')
    df['peak'] = df['hour'].apply(lambda x: 'Peak' if 7<=x<=10 or 17<=x<=20 else 'Non-Peak')

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Filters")

hour = st.sidebar.slider("Select Hour", 0, 23, (0, 23))
filtered_df = df[(df['hour'] >= hour[0]) & (df['hour'] <= hour[1])]

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Fare", round(filtered_df['fare_amount'].mean(), 2))
col2.metric("Avg Distance", round(filtered_df['trip_distance'].mean(), 2))
col3.metric("Avg Duration", round(filtered_df['trip_duration'].mean(), 2))
col4.metric("Avg Tip %", round(filtered_df['tip_percentage'].mean(), 2))

# -----------------------------
# DISTRIBUTIONS
# -----------------------------
st.subheader("📈 Distributions")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.histplot(filtered_df['fare_amount'], bins=50, ax=ax)
    ax.set_title("Fare Distribution")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.histplot(filtered_df['trip_distance'], bins=50, ax=ax)
    ax.set_title("Distance Distribution")
    st.pyplot(fig)

# -----------------------------
# DEMAND ANALYSIS
# -----------------------------
st.subheader("📊 Demand by Hour")

fig, ax = plt.subplots()
filtered_df['hour'].value_counts().sort_index().plot(ax=ax)
ax.set_title("Trips per Hour")
st.pyplot(fig)

# -----------------------------
# SPEED ANALYSIS
# -----------------------------
st.subheader("🚦 Speed Analysis")

fig, ax = plt.subplots()
filtered_df.groupby('hour')['trip_speed'].mean().plot(ax=ax)
ax.set_title("Average Speed by Hour")
st.pyplot(fig)

# -----------------------------
# CORRELATION
# -----------------------------
st.subheader("🔗 Correlation Insights")

corr = filtered_df[['trip_distance','fare_amount','trip_duration']].corr()

fig, ax = plt.subplots()
sns.heatmap(corr, annot=True, ax=ax)
st.pyplot(fig)

# -----------------------------
# HYPOTHESIS TESTING
# -----------------------------
st.subheader("🧪 Hypothesis Testing")

peak = df[df['peak']=='Peak']['fare_amount']
non_peak = df[df['peak']=='Non-Peak']['fare_amount']

t_stat, p_val = stats.ttest_ind(peak, non_peak)

st.write("### Peak vs Non-Peak Fare")
st.write(f"P-value: {p_val}")

if p_val < 0.05:
    st.success("Significant difference in fare (Peak Pricing Exists)")
else:
    st.warning("No significant difference")

# -----------------------------
# BUSINESS INSIGHTS
# -----------------------------
st.subheader("💡 Business Insights")

st.markdown("""
- 🚖 High duration + low distance trips indicate inefficiency  
- 💰 Fare per km variation suggests pricing inconsistency  
- 📊 Peak hours show high demand and lower speeds  
- 🎯 Few high-value trips drive majority revenue  
""")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("Made by Beesam Gayathri 🚀")