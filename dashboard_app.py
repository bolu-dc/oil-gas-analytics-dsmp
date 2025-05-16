import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objs as go
from shapely.geometry import mapping
from sklearn.linear_model import Ridge
from eia_api_fetcher import fetch_usa_data

# --- Load Canadian Data ---
@st.cache_data
def load_canadian_data(path="estimated-production-canadian-crude-oil-equivalent.xlsx"):
    df_raw = pd.read_excel(path, sheet_name="HIST - barrels per day")
    df_raw.dropna(how='all', inplace=True)
    df_raw.dropna(axis=1, how='all', inplace=True)
    df_raw.rename(columns={df_raw.columns[0]: 'period'}, inplace=True)
    df_raw['period'] = pd.to_datetime(df_raw['period'], errors='coerce')
    df_raw.dropna(subset=['period'], inplace=True)
    exclude = ['Canada Total', 'Raw Mined Bitumen', 'Raw In Situ Bitumen']
    df_raw = df_raw.loc[:, ~df_raw.columns.isin(exclude)]
    province_groups = {}
    for col in df_raw.columns[1:]:
        if isinstance(col, str) and len(col) >= 2:
            prov = col.strip()[:2]
            province_groups.setdefault(prov, []).append(col)
    data = {'period': df_raw['period']}
    for prov, cols in province_groups.items():
        data[prov] = df_raw[cols].sum(axis=1) / 1000
    df_can = pd.DataFrame(data)
    df_long = df_can.melt(id_vars='period', var_name='state', value_name='daily_value')
    province_map = {
        'AB':'Alberta','BC':'British Columbia','MB':'Manitoba','NB':'New Brunswick',
        'NL':'Newfoundland & Labrador','NS':'Nova Scotia','ON':'Ontario','PE':'Prince Edward Island',
        'QC':'Quebec','SK':'Saskatchewan','NT':'Northwest Territories','NW':'Northwest Territories',
        'NU':'Nunavut','YT':'Yukon'
    }
    df_long['state'] = df_long['state'].map(province_map).fillna(df_long['state'])
    df_long['country'] = 'Canada'
    df_long['year'] = df_long['period'].dt.year
    df_long['month'] = df_long['period'].dt.month
    return df_long[df_long['year'] >= 2000]

# --- PADD Regions ---
padd_to_states = {
    "PADD 1": ['Maine','New Hampshire','Vermont','Massachusetts','Rhode Island','Connecticut',
               'New York','New Jersey','Pennsylvania'],
    "PADD 2": ['Ohio','Michigan','Indiana','Illinois','Wisconsin','Minnesota','Iowa','Missouri',
               'North Dakota','South Dakota','Nebraska','Kansas'],
    "PADD 3": ['Texas','Louisiana','Mississippi','Alabama','Florida','Arkansas','Oklahoma',
               'New Mexico','Federal Offshore (Gulf)'],
    "PADD 4": ['Montana','Idaho','Wyoming','Colorado','Utah','Nevada','Arizona','Washington',
               'Oregon'],
    "PADD 5": ['California','Alaska','Hawaii','Washington (Pacific)','Oregon (Pacific)',
               'Federal Offshore (Pacific)']
}

# --- Load Data ---
@st.cache_data
def load_data():
    df_usa = fetch_usa_data()
    df_can = load_canadian_data()
    df_all = pd.concat([df_usa, df_can], ignore_index=True)
    df_all = df_all[df_all['period'] <= pd.Timestamp('2025-01-31')]
    return df_all

# --- Load Map Data directly from CSV ---
@st.cache_data
def load_map_data():
    df = pd.read_csv('geo_maps_oil_UPDATED.csv')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
    return gdf

df_all = load_data()
gdf_map_full = load_map_data()
countries = df_all['country'].unique()
states_by_country = {c: sorted(df_all[df_all['country']==c]['state'].unique()) for c in countries}

# --- Sidebar filters (from deploy.py style) ---
st.sidebar.header("Filters")
country = st.sidebar.multiselect("Country", countries, default=['USA'])

padd = st.sidebar.multiselect("PADD (USA only)", list(padd_to_states.keys()), default=[])
state_options = []
if 'USA' in country and padd:
    valid_states = []
    for p in padd:
        valid_states.extend(padd_to_states.get(p, []))
    valid_states = sorted(set(valid_states))
    state_options = valid_states
states = st.sidebar.multiselect("State(s)", state_options, default=state_options if state_options else [])

province_options = states_by_country.get('Canada', []) if 'Canada' in country else []
provinces = st.sidebar.multiselect("Province(s)", province_options, default=province_options if province_options else [])

years = sorted(df_all.year.unique())
start_year, end_year = st.sidebar.select_slider("Year Range", options=years, value=(years[0], years[-1]))
months = list(range(1, 13))
start_month = st.sidebar.selectbox("Start Month", months, index=0)
end_month = st.sidebar.selectbox("End Month", months, index=11)

forecast = st.sidebar.checkbox("Forecast Next 12 Months")
recent = st.sidebar.checkbox("Use Most Recent 10 Years")

# --- Data Filtering for line chart ---
latest = df_all['period'].max()
latest_year, latest_month = latest.year, latest.month
use_recent = recent
error_text = ""
if forecast and not (use_recent or (end_year == latest_year and end_month == latest_month)):
    error_text = "⚠️ Forecast disabled: end date must be latest unless using recent data."
start = pd.Timestamp(year=start_year, month=start_month, day=1)
end = pd.Timestamp(year=end_year, month=end_month, day=1)
df = df_all.copy()
if use_recent:
    cutoff = df['period'].max() - pd.DateOffset(years=10)
    df = df[df['period'] >= cutoff]
else:
    df = df[(df['period'] >= start) & (df['period'] <= end)]

# --- Map Data Filtering (always use geo_maps_oil_UPDATED.csv as base) ---
gdf_map = gdf_map_full.copy()

# Filter by year and month range
gdf_map = gdf_map[
    (gdf_map['year'] >= start_year) &
    (gdf_map['year'] <= end_year) &
    (gdf_map['month'] >= start_month) &
    (gdf_map['month'] <= end_month)
]

# Apply country-level filter
gdf_map = gdf_map[gdf_map['country'].isin(country)]

# Apply region-specific filters
if 'USA' in country and states:
    gdf_map = gdf_map[(gdf_map['country'] != 'USA') | (gdf_map['state'].isin(states))]

if 'Canada' in country and provinces:
    gdf_map = gdf_map[(gdf_map['country'] != 'Canada') | (gdf_map['state'].isin(provinces))]

# --- MAP VISUALIZATION ---
st.title("Oil & Gas Analytics Dashboard")

st.subheader("Average Daily Oil Production Map")
if gdf_map.empty:
    st.warning("No map data available for selected filters.")
else:
    # Aggregate for average daily value
    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}-01")
    end_date = pd.to_datetime(f"{end_year}-{end_month:02d}-01")
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

    # Ensure proper aggregation
    average_data = gdf_map.groupby(['state'], as_index=False).agg({'daily_value': 'sum'})
    average_data['daily_value'] = average_data['daily_value'] / num_months

    # Merge with full geometries to ensure all provinces appear
    geometry_lookup = gdf_map_full.drop_duplicates('state')[['state', 'geometry']]
    average_data = geometry_lookup.merge(average_data, on='state', how='left')
    average_data['daily_value'] = average_data['daily_value'].fillna(0)

    # Build GeoJSON
    features = []
    for _, row in average_data.iterrows():
        if pd.notnull(row['geometry']):
            features.append({
                'type': 'Feature',
                'id': row['state'],
                'properties': {},
                'geometry': mapping(row['geometry'])
            })
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    # Plot Map with 'plasma' color scale
    fig_map = px.choropleth(
        average_data,
        geojson=geojson,
        locations='state',
        color='daily_value',
        hover_name='state',
        title='Average Daily Oil Production by State/Province',
        color_continuous_scale='plasma',
        labels={'daily_value': 'Average Daily Production (MBBL)'}
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

# --- Line Chart (from deploy.py logic) ---
st.subheader("Production Trend (Line Chart)")
fig_line = go.Figure()
colors = px.colors.qualitative.Plotly
rows = []
for c in country:
    regs = states if c == 'USA' else provinces
    for r in regs or []:
        dsub = df[(df.country == c) & (df.state == r)]
        idx = len(fig_line.data)
        col = colors[idx % len(colors)]
        # historical trace
        fig_line.add_trace(go.Scatter(
            x=dsub.period,
            y=dsub.daily_value,
            mode='lines+markers',
            name=f"{c}-{r}",
            legendgroup=f"{c}-{r}",
            line=dict(color=col),
            marker=dict(color=col)
        ))
        rows += dsub.to_dict('records')
        # forecast trace
        if forecast and (use_recent or (end_year == latest_year and end_month == latest_month)) and len(dsub) > 24:
            X = dsub.period.map(pd.Timestamp.toordinal).values.reshape(-1,1)
            y = dsub.daily_value.values
            m = Ridge().fit(X, y)
            last = dsub.period.max()
            fut = pd.date_range(last + pd.DateOffset(months=1), periods=12, freq='MS')
            yf = m.predict(fut.map(pd.Timestamp.toordinal).values.reshape(-1,1))
            fig_line.add_trace(go.Scatter(
                x=fut,
                y=yf,
                mode='lines',
                line=dict(color=col, dash='dash'),
                name=f"{c}-{r} Forecast",
                legendgroup=f"{c}-{r}",
                showlegend=True
            ))
fig_line.update_layout(
    title='Crude Oil Production (Line Chart)',
    xaxis_title='Date',
    yaxis_title='Barrels/day',
    yaxis=dict(rangemode='tozero'),
    colorway=colors
)

if error_text:
    st.warning(error_text)

st.plotly_chart(fig_line, use_container_width=True)

# --- Data Table ---
if rows:
    df_table = pd.DataFrame(rows)
    st.dataframe(df_table)
else:
    st.info("No data available for selected filters.")