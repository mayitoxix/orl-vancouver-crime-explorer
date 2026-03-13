import streamlit as st
import pandas as pd
import altair as alt
import geopandas as gpd

st.set_page_config(
    page_title="Vancouver Neighbourhood Safety Explorer", 
    layout = "wide"
)

st.title("🍁 Vancouver Neighbourhood Safety")
st.markdown(
    "Explore where incidents cluster, which crime types are most common, "
    "and review filtered records. For year 2025."
)

# Data
@st.cache_data
def load_crime_data():
    return pd.read_csv("data/processed/processed_vancouver_crime_data_2025.csv")

crime_df = load_crime_data()

# Sidebar filters
months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
time_of_day_order = ["Morning", "Afternoon", "Evening/Night"]


st.sidebar.header("Filters")

selected_nb = st.sidebar.multiselect(
    "Neighbourhood",
    sorted(crime_df["NEIGHBOURHOOD"].unique()),
    default=["Downtown", "West End"]
)

selected_crime_trype = st.sidebar.multiselect(
    "Crime Type",
    sorted(crime_df["TYPE"].unique()),
    default=["Break and Enter Residential/Other"]
)

selected_month = st.sidebar.multiselect(
    "Month",
    months_order
)

selected_time_of_day = st.sidebar.multiselect(
    "Time of Day",
    time_of_day_order
)

def get_filtered_data(df, neighbourhood, crime_type, month, time_of_day):
    
    out = df.copy()

    if neighbourhood:
        out = out[out["NEIGHBOURHOOD"].isin(neighbourhood)]

    if crime_type:
        out = out[out["TYPE"].isin(crime_type)]

    if month:
        out = out[out["MONTH_NAME"].isin(month)]

    if time_of_day:
        out = out[out["TIME_OF_DAY"].isin(time_of_day)]

    return out


filtered_df = get_filtered_data(
    crime_df,
    selected_nb,
    selected_crime_trype,
    selected_month,
    selected_time_of_day
)

# Quick check
st.write(f"**{len(filtered_df):,} incidents match the selected filters**")

if st.sidebar.button("Reset filters"):
    st.rerun()

