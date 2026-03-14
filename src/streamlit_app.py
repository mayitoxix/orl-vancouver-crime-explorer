import streamlit as st
import pandas as pd
import altair as alt
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from pyproj import Transformer
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Vancouver Neighbourhood Safety Explorer", 
    layout="wide"
)

st.title("🍁 Vancouver Neighbourhood Safety")
st.markdown(
    "Explore where incidents cluster, which crime types are most common, "
    "and review filtered records. For year 2025."
)

# -----------------
# Data
# -----------------
@st.cache_data
def load_crime_data():
    return pd.read_csv("data/processed/processed_vancouver_crime_data_2025.csv")


crime_df = load_crime_data()

@st.cache_data
def load_neighbourhoods():
    gdf = gpd.read_file(
        "data/processed/merged_vancity.gpkg",
        layer="merged_vancity"
    )
    return gdf.to_crs(epsg=4326)


neigh_gdf = load_neighbourhoods()

@st.cache_data
def filtered_latlon():
    df = load_crime_data().copy()

    df["X"] = pd.to_numeric(df["X"], errors="coerce")
    df["Y"] = pd.to_numeric(df["Y"], errors="coerce")
    df = df.dropna(subset=["X", "Y"])

    if df.empty:
        return pd.DataFrame(columns=["lat", "lon"])
    
    # Source UTM Zone 10N WGS84 EPSG:32610 to WGS84 lat/lon EPSG:4326
    transformer = Transformer.from_crs("EPSG:32610", "EPSG:4326", always_xy=True)
    lons, lats = transformer.transform(df["X"].to_numpy(), df["Y"].to_numpy())
    
    df["lat"] = lats
    df["lon"] = lons

    return df


crime_df = filtered_latlon()


# -----------------
# Sidebar
# -----------------
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

# if st.sidebar.button("Reset filters"):
#     st.rerun()


# -----------------
# Filtered data
# -----------------
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


all_filtered_df = get_filtered_data(
    crime_df,
    selected_nb,
    selected_crime_trype,
    selected_month,
    selected_time_of_day
)

def get_filtered_data_no_creime_type(df, neighbourhood, month, time_of_day):
    out = df.copy()

    if neighbourhood:
        out = out[out["NEIGHBOURHOOD"].isin(neighbourhood)]
    if month:
        out = out[out["MONTH_NAME"].isin(month)]
    if time_of_day:
        out = out[out["TIME_OF_DAY"].isin(time_of_day)]

    return out


no_crime_filtered_df = get_filtered_data_no_creime_type(
    crime_df,
    selected_nb,
    selected_month,
    selected_time_of_day
)

top_5_crimes = (
    no_crime_filtered_df.groupby("TYPE")
    .size()
    .sort_values(ascending=False)
    .head(5)
    .reset_index(name="Incidents")
)

if not top_5_crimes.empty:
    total = top_5_crimes["Incidents"].sum()
    top_5_crimes["Percent Share"] = (top_5_crimes["Incidents"] / total) * 100


# -----------------
# Dashboard
# -----------------

# Layout
col1, col2 = st.columns([7, 5])

# Map side
with col1:
    st.subheader("Crime Across Neighbourhoods")

    vancity_center = [49.2827, -123.1207]
        
    # Map base
    m = folium.Map(
        location=vancity_center,
        zoom_start=12,
        tiles="CartoDB positron",
        #width="100%",
        #height="100%",
    )
    
    # Add neighbourhood polygons (default-persistent style)
    folium.GeoJson(
        neigh_gdf.__geo_interface__,
        name="Neighbourhoods",
        style_function=lambda _feature: {
            "fillOpacity": 0.03,
            "weight": 1,
            "color": "#555555",
        },
    ).add_to(m)

    # Heatmap
    heat_data = all_filtered_df[["lat", "lon"]].values.tolist()

    if heat_data:
                HeatMap(
                    heat_data,
                    radius=14,
                    blur=18,
                    max_zoom=13,
                ).add_to(m)

    st_folium(
        m,
        #width=None,
        height=400,
        width="stretch"
    )


# Top 5 Bar Chart
with col2:
    st.subheader("Top 5 Crime Types")
    if top_5_crimes.empty:
        st.warning("No data for current filters.")
    else:
        bar_chart = (
            alt.Chart(top_5_crimes)
            .mark_bar(size=40)
            .encode(
                x=alt.X("Percent Share:Q", title="Percent of Incidents"),
                y=alt.Y(
                    "TYPE:N",
                    sort="-x",
                    title="",
                    axis=alt.Axis(labelLimit=150),
                    scale=alt.Scale(paddingInner=0)
                ),
                color=alt.Color(
                    "Percent Share:Q",
                    scale=alt.Scale(scheme="tealblues"),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("TYPE:N", title="Crime Type"),
                    alt.Tooltip("Incidents:Q"),
                    alt.Tooltip("Percent Share:Q", format=".1f"),
                ]   
            )
            .properties(
                height=400,
                # title="Top 5 Crime Types"
            )
        )

    st.altair_chart(bar_chart, width="stretch")

# Quick check
st.write(f"**{len(all_filtered_df):,} incidents match the selected filters**")

# Show filtered data (all columns)
st.dataframe(
    # all_filtered_df[available_preview_cols],
    all_filtered_df,
    # use_container_width=True, # to be deprecated
    width="stretch",
    height=500
)

