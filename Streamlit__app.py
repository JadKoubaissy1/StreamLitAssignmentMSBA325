import os
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set the title of the app
st.title("Waste Transfer Data Visualizations")

# Use a relative file path for the dataset
file_path = 'WasteByRegion.csv'  # Ensure the CSV file is in the same directory or adjust the path accordingly

# Load the dataset
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    st.error(f"File not found: {file_path}. Please ensure the file is in the correct location.")
    st.stop()

# Rename columns for clarity
df.rename(columns={
    'Waste transfer destination - factory': 'Waste destination: factory',
    'Waste transfer destination - unknown': 'Waste destination: unknown',
    'Waste transfer destination - internal dumpsite': 'Waste destination: internal dumpsite',
    'Waste transfer destination - external dumpsite': 'Waste destination: external dumpsite',
    'Waste transfer destination - sanitary landfill': 'Waste destination: sanitary landfill'
}, inplace=True)

# Add a mock 'refPeriod' column for testing
if 'refPeriod' not in df.columns:
    df['refPeriod'] = np.random.choice(pd.date_range(start='2021-01-01', periods=12, freq='M'), size=len(df))

# Function to categorize regions
def categorize_region(area):
    if 'Beirut' in area:
        return 'Beirut'
    elif 'North' in area:
        return 'North'
    elif 'South' in area:
        return 'South'
    elif 'Bekaa' in area or 'Baalbek' in area or 'Hermel' in area or 'Zahle' in area:
        return 'East'
    elif 'Mount Lebanon' in area:
        return 'West'
    else:
        return 'West'

df['Region_Category'] = df['refArea'].apply(lambda x: categorize_region(x))

# Define waste columns
waste_columns = [
    'Waste destination: factory', 
    'Waste destination: unknown', 
    'Waste destination: internal dumpsite', 
    'Waste destination: external dumpsite', 
    'Waste destination: sanitary landfill'
]

# Sidebar for navigation
st.sidebar.title("Choose Visualization")
option = st.sidebar.radio(
    "Select a visualization type:",
    ("Bar Chart", "Bubble Map", "Pie Chart", "Line Chart", "Treemap")
)

# Bar Chart
if option == "Bar Chart":
    df_grouped = df.groupby(['Region_Category'])[waste_columns].sum().reset_index()
    df_melted = df_grouped.melt(id_vars='Region_Category', var_name='Waste Transfer Type', value_name='Count')

    fig = px.bar(
        df_melted, 
        x='Region_Category', 
        y='Count', 
        color='Waste Transfer Type', 
        title='Waste Transfer Destinations by Region',
        labels={'Region_Category': 'Region', 'Count': 'Total Waste Transfers'},
        text_auto=True
    )
    st.plotly_chart(fig)

# Bubble Map
elif option == "Bubble Map":
    region_coords = {
        'Beirut': (33.8938, 35.5018),
        'North': (34.4367, 35.8506),
        'South': (33.2707, 35.2037),
        'East': (33.8765, 36.089),
        'West': (33.8172, 35.5428)
    }

    df_grouped = df.groupby(['Region_Category'])[waste_columns].sum().reset_index()
    df_grouped['lat'] = df_grouped['Region_Category'].map(lambda x: region_coords[x][0])
    df_grouped['lon'] = df_grouped['Region_Category'].map(lambda x: region_coords[x][1])
    df_grouped['Total Waste'] = df_grouped[waste_columns].sum(axis=1)

    fig = px.scatter_mapbox(
        df_grouped, 
        lat='lat', 
        lon='lon', 
        size='Total Waste', 
        color='Region_Category', 
        hover_name='Region_Category', 
        title='Waste Transfer by Region',
        mapbox_style="open-street-map", 
        size_max=50, 
        zoom=6
    )
    st.plotly_chart(fig)

# Pie Chart
elif option == "Pie Chart":
    df_melted = df.melt(id_vars=['Region_Category'], 
                        value_vars=waste_columns, 
                        var_name='Waste Transfer Type', 
                        value_name='Count')

    fig = px.pie(
        df_melted, 
        names='Waste Transfer Type', 
        values='Count', 
        title='Proportion of Waste Transfer Types (Overall)',
        height=600
    )
    st.plotly_chart(fig)

# Simplified Line Chart
elif option == "Line Chart":
    df_melted = df.melt(id_vars=['refPeriod'], 
                        value_vars=waste_columns, 
                        var_name='Waste Transfer Type', 
                        value_name='Count')

    fig = px.line(
        df_melted, 
        x='refPeriod', 
        y='Count', 
        color='Waste Transfer Type', 
        title='Overall Waste Transfer Trend Over Time',
        markers=True
    )
    st.plotly_chart(fig)

# Treemap with Warmer Colors and Number Labels
elif option == "Treemap":
    df_melted = df.melt(id_vars=['Region_Category'], 
                        value_vars=waste_columns, 
                        var_name='Waste Transfer Type', 
                        value_name='Count')

    # Filter out zero values
    df_melted = df_melted[df_melted['Count'] > 0]

    if not df_melted.empty:
        fig = px.treemap(
            df_melted, 
            path=['Region_Category', 'Waste Transfer Type'], 
            values='Count', 
            title='Waste Transfer Distribution by Region and Type',
            color='Count',
            color_continuous_scale='YlOrRd',  # Warmer color scale
            hover_data={'Count': True}
        )
        fig.update_traces(texttemplate="%{label}<br>%{value}", textinfo="label+value")
        st.plotly_chart(fig)
    else:
        st.warning("No data available for the treemap.")
