import requests
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import Ridge

# Fetch USA data from API
api_key = "iWrhss3Cw3LicbEc1gUK1cj5Q83EXVeJOsacabDz"

apis = [
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPFL1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",  # Florida
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPNY1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",  # New York
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPPA1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",  # Pennsylvania
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPVA1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",  # Virginia
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPWV1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",  # West Virginia
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPIL1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPIN1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPKS1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPKY1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFP_SMI_1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPMO1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPNE1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPND1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPOH1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPOK1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPSD1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPTN1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPAL1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPAR1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPLA1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPMS1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPNM1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPTX1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFP3FM1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPCO1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=M_EPC0_FPF_SID_MBBL&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPMT1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPUT1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPWY1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    f"https://api.eia.gov/v2/petroleum/sum/crdsnd/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPAK1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPAZ1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPCA1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFPNV1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[series][]=MCRFP5F1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
]

# Series to State mapping
series_to_state = [
    ("MCRFPFL1", "Florida"),
    ("MCRFPNY1", "New York"),
    ("MCRFPPA1", "Pennsylvania"),
    ("MCRFPVA1", "Virginia"),
    ("MCRFPWV1", "West Virginia"),
    ("MCRFPIL1", "Illinois"),
    ("MCRFPIN1", "Indiana"),
    ("MCRFPKS1", "Kansas"),
    ("MCRFPKY1", "Kentucky"),
    ("MCRFP_SMI_1", "Michigan"),
    ("MCRFPMO1", "Missouri"),
    ("MCRFPNE1", "Nebraska"),
    ("MCRFPND1", "North Dakota"),
    ("MCRFPOH1", "Ohio"),
    ("MCRFPOK1", "Oklahoma"),
    ("MCRFPSD1", "South Dakota"),
    ("MCRFPTN1", "Tennessee"),
    ("MCRFPAL1", "Alabama"),
    ("MCRFPAR1", "Arkansas"),
    ("MCRFPLA1", "Louisiana"),
    ("MCRFPMS1", "Mississippi"),
    ("MCRFPNM1", "New Mexico"),
    ("MCRFPTX1", "Texas"),
    ("MCRFP3FM1", "Federal Offshore (PADD 3)"),
    ("MCRFPCO1", "Colorado"),
    ("MCRFPMT1", "Montana"),
    ("MCRFPUT1", "Utah"),
    ("MCRFPWY1", "Wyoming"),
    ("MCRFPAK1", "Alaska"),
    ("MCRFPAZ1", "Arizona"),
    ("MCRFPCA1", "California"),
    ("MCRFPNV1", "Nevada"),
    ("MCRFP5F1", "Federal Offshore (PADD 5)")
]

# PADD regions
padd_to_states = {
    "PADD 1": ['Florida','New York','Pennsylvania','Virginia','West Virginia','Kentucky','Tennessee'],
    "PADD 2": ['Illinois','Indiana','Kansas','Michigan','Missouri','North Dakota','Nebraska','Ohio','South Dakota'],
    "PADD 3": ['Alabama','Arkansas','Louisiana','Mississippi','New Mexico','Oklahoma','Texas','Federal Offshore (PADD 3)'],
    "PADD 4": ['Colorado','Montana','Utah','Wyoming'],
    "PADD 5": ['Alaska','Arizona','California','Nevada','Federal Offshore (PADD 5)']
}

def fetch_usa_data():
    all_data = []
    for series, state in series_to_state:
        url = (
            f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/"
            f"?api_key={api_key}&frequency=monthly&data[0]=value"
            f"&facets[series][]={series}&sort[0][column]=period&sort[0][direction]=asc"
            f"&offset=0&length=5000"
        )
        r = requests.get(url)
        r.raise_for_status()
        raw = r.json().get('response', {}).get('data', [])
        df_api = pd.DataFrame(raw)
        df_api['period'] = pd.to_datetime(df_api['period'], errors='coerce')
        df_api['value'] = pd.to_numeric(df_api['value'], errors='coerce')
        df_api['country'] = 'USA'
        df_api['state'] = state
        all_data.append(df_api)
    df = pd.concat(all_data, ignore_index=True)
    df['year'] = df['period'].dt.year
    df['month'] = df['period'].dt.month
    df['days_in_month'] = df['period'].dt.days_in_month
    df['daily_value'] = df['value'] / df['days_in_month']
    return df[df['year'] >= 2000]
