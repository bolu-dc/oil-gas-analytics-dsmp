import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Load your data
def load_data():
    # Replace with your actual data loading logic
    geo_maps_oil = pd.read_csv("/Users/boluwatifeoduyemi/Documents/Data Science/SPE DSMP/Oil and Gas Analytics Dashboard/geo_maps_oil.csv")
    return geo_maps_oil

geo_maps_oil = load_data()

st.title("Oil Wells Data Visualization")
st.write("This app visualizes American oil wells data on a map and other interactive charts.")

# Sidebar filters
st.sidebar.header("Filters")
month = st.sidebar.selectbox("Select Month", ["All"] + sorted(geo_maps_oil['month'].unique()))
year = st.sidebar.selectbox("Select Year", ["All"] + sorted(geo_maps_oil['year'].unique()))
state = st.sidebar.selectbox("Select State", ["All"] + sorted(geo_maps_oil['name'].unique()))

# Filter the data based on user input
filtered_data = geo_maps_oil.copy()
if month != "All":
    filtered_data = filtered_data[filtered_data['month'] == month]
if year != "All":
    filtered_data = filtered_data[filtered_data['year'] == year]
if state != "All":
    filtered_data = filtered_data[filtered_data['name'] == state]


# Call geopandas to load the shapefile for US states
states_prov = gpd.read_file('/Users/boluwatifeoduyemi/Documents/Data Science/Python Packages/ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces.shp')


# Create the Plotly choropleth map
fig = px.choropleth(
    filtered_data,
    geojson=states_prov.set_index('iso_3166_2')['geometry'].__geo_interface__,
    locations='iso_3166_2',
    color='value',
    hover_name='series-description',
    title='Oil Production by State',
    color_continuous_scale='Viridis',
    labels={'value': 'Production (MBBL)'}
)

# Update map layout
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

# Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)

# streamlit run app.py