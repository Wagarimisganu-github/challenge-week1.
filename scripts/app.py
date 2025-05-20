import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy import stats
from io import BytesIO
from typing import Dict

# Configuration
DATE_COL = 'Timestamp'
SOLAR_COLS = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB']
CLIMATE_COLS = ['Tamb', 'RH', 'WS', 'Precipitation']

# Set page config
st.set_page_config(page_title="Solar Data Analytics", layout="wide")
sns.set_theme(style='whitegrid')

def load_region_data(uploaded_file):
    """Load and validate regional dataset from uploaded file"""
    try:
        region = uploaded_file.name.split('_')[0]
        df = pd.read_csv(
            uploaded_file,
            parse_dates=[DATE_COL],
            dtype={'Comments': 'category'}
        )
        df['Region'] = region
        return df
    except Exception as e:
        st.error(f"Error loading {uploaded_file.name}: {str(e)}")
        return pd.DataFrame()

def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Generate comprehensive data quality report"""
    report = pd.DataFrame({
        'Missing Values': df.isna().sum(),
        'Zero Values': (df == 0).sum(),
        'Negative Values': (df.select_dtypes(include=np.number) < 0).sum()
    })

    ranges = {
        'GHI': (0, 1500),
        'RH': (0, 100),
        'Tamb': (-20, 60)
    }
    for col, (min_val, max_val) in ranges.items():
        report.loc[col, 'Out of Range'] = ((df[col] < min_val) | (df[col] > max_val)).sum()

    return report

@st.cache_data
def clean_solar_data(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline with outlier handling"""
    df_clean = df.drop(columns='Comments', errors='ignore').ffill()
    
    for col in SOLAR_COLS:
        df_clean[col] = df_clean[col].clip(lower=0)
    df_clean['RH'] = df_clean['RH'].clip(0, 100)

    for col in SOLAR_COLS + ['Tamb', 'WS']:
        q1 = df_clean[col].quantile(0.25)
        q3 = df_clean[col].quantile(0.75)
        iqr = q3 - q1
        df_clean = df_clean[(df_clean[col] >= q1 - 1.5*iqr) & (df_clean[col] <= q3 + 1.5*iqr)]

    return df_clean.reset_index(drop=True)

def regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate key statistics by region"""
    return df.groupby('Region').agg({
        'GHI': ['mean', 'std', 'max'],
        'DNI': ['median', 'max'],
        'Tamb': ['mean', 'std'],
        'WS': ['mean', 'max'],
        'Precipitation': 'sum'
    }).T.round(2)

def plot_wind_distribution(df: pd.DataFrame):
    """Wind speed and direction analysis"""
    regions = df['Region'].unique()
    num_cols = 3
    num_rows = (len(regions) + num_cols - 1) // num_cols
    fig = plt.figure(figsize=(15, 5*num_rows))
    
    for i, region in enumerate(regions, 1):
        ax = fig.add_subplot(num_rows, num_cols, i, projection='polar')
        region_data = df[df['Region'] == region]
        theta = np.radians(region_data['WD'])
        r = region_data['WS']
        scatter = ax.scatter(theta, r, alpha=0.5, c=region_data['Tamb'], cmap='viridis')
        ax.set_title(f'{region} Wind Patterns', pad=20)
    
    plt.colorbar(scatter, ax=fig.axes, label='Temperature (°C)')
    return fig

def plot_correlation_matrix(df: pd.DataFrame):
    """Interactive correlation analysis"""
    corr_df = df[SOLAR_COLS + CLIMATE_COLS].corr()
    fig = px.imshow(
        corr_df,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1,
        title='Variable Correlation Matrix'
    )
    fig.update_layout(width=800, height=800)
    return fig

def analyze_cleaning_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Quantify cleaning effects on module performance"""
    results = []
    clean_events = df[df['Cleaning'] == 1].index

    for idx in clean_events:
        if idx > 3 and idx < len(df)-3:
            pre = df.loc[idx-3:idx-1, ['ModA', 'ModB']].mean()
            post = df.loc[idx+1:idx+3, ['ModA', 'ModB']].mean()
            results.append({
                'Region': df.at[idx, 'Region'],
                'ModA_Improvement': post['ModA'] - pre['ModA'],
                'ModB_Improvement': post['ModB'] - pre['ModB']
            })

    return pd.DataFrame(results).groupby('Region').mean().style.background_gradient()

def interactive_bubble_chart(df: pd.DataFrame):
    """Create interactive bubble chart"""
    return px.scatter(
        df,
        x='Tamb',
        y='GHI',
        size='WS',
        color='RH',
        animation_frame=df[DATE_COL].dt.month,
        hover_name='Region',
        size_max=40,
        title='Interactive Solar Analysis - GHI vs Temperature vs Wind Speed'
    )

def generate_recommendations(df: pd.DataFrame) -> Dict:
    """Generate data-driven installation recommendations"""
    analysis = df.groupby('Region').agg({
        'GHI': ['mean', 'std'],
        'DNI': 'median',
        'Tamb': ['mean', 'std'],
        'Precipitation': 'sum',
        'WSgust': 'max'
    })

    return {
        'Best Overall Potential': analysis[('GHI', 'mean')].idxmax(),
        'Most Stable Radiation': analysis[('GHI', 'std')].idxmin(),
        'Lowest Maintenance Risk': analysis[('Precipitation', 'sum')].idxmin(),
        'Optimal CSP Location': analysis[('DNI', 'median')].idxmax()
    }

# Streamlit UI
st.title("🌞 Solar Energy Performance Analyzer")

st.write("""
        ## **Business Overview**

MoonLight Energy Solutions is committed to enhancing operational efficiency and sustainability through strategic solar investments. As an Analytics Engineer, my role is to analyze environmental measurement data provided by the engineering team and translate key insights into a data-driven strategy report. This analysis focuses on identifying high-potential regions for solar installation, ensuring alignment with the company’s long-term sustainability goals. By leveraging statistical analysis and exploratory data analysis (EDA), the report provides actionable recommendations that support informed decision-making and contribute to MoonLight Energy Solutions' overarching objectives.
""")


st.info("""This application analyzes solar energy performance data across multiple regions. Upload CSV files named like `RegionName_solar_data.csv` to begin analysis.""")
    
# File upload section
uploaded_files = st.file_uploader(
    "Upload regional solar data CSV files",
    type=['csv'],
    accept_multiple_files=True,
    help="Files should be named like 'RegionName_solar_data.csv'"
)

if not uploaded_files:
    st.info("Please upload CSV files to begin analysis")
    st.stop()

# Data loading and processing
with st.spinner("Loading and processing data..."):
    dfs = [load_region_data(f) for f in uploaded_files]
    full_df = pd.concat(dfs, ignore_index=True)
    cleaned_df = clean_solar_data(full_df)

# Sidebar with expandable dataset information
st.sidebar.title("Navigation")
section = st.sidebar.selectbox(
    "Select a section:",
    ["Project Overview", "Dataset Overview", "Tasks Completed"]
)

if section == "Project Overview":
    st.sidebar.write("This project analyzes solar and wind energy data to gain insights into weather patterns and energy efficiency.")
elif section == "Dataset Overview":
    with st.sidebar.expander("Dataset Information"):
        st.write("The dataset contains meteorological data, including:")
        st.write("- Temperature (Tamb)")
        st.write("- Wind Speed (WS)")
        st.write("- Wind Direction (WD)")
        st.write("- Global Horizontal Irradiance (GHI)")
        st.write("- Relative Humidity (RH)")
elif section == "Tasks Completed":
    st.sidebar.write("- Data cleaning\n- Exploratory Data Analysis\n- Wind Distribution Analysis\n- Correlation Matrix\n- Interactive Visualizations")


if section == "Project Overview":
    st.sidebar.write("This project analyzes solar and wind energy data to gain insights into weather patterns and energy efficiency.")
elif section == "Dataset Overview":
    st.sidebar.write("The dataset contains meteorological data, including temperature, wind speed, wind direction, and solar irradiance.")
elif section == "Tasks Completed":
    st.sidebar.write("- Data cleaning\n- Exploratory Data Analysis\n- Wind Distribution Analysis\n- Correlation Matrix\n- Interactive Visualizations")


# Main dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Data Quality", "📈 Visualizations", "📋 Recommendations"])

with tab1:
    st.subheader("Data Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Records", full_df.shape[0])
        st.dataframe(full_df.head(), use_container_width=True)
    
    with col2:
        st.metric("Clean Records", cleaned_df.shape[0])
        st.dataframe(cleaned_df.describe(), use_container_width=True)
    
    st.download_button(
        label="📥 Download Cleaned Data",
        data=cleaned_df.to_csv(index=False).encode('utf-8'),
        file_name='cleaned_solar_data.csv',
        mime='text/csv'
    )

with tab2:
    st.subheader("Data Quality Report")
    quality_report = data_quality_report(full_df)
    st.dataframe(quality_report.style.background_gradient(cmap='Reds'), use_container_width=True)

with tab3:
    st.subheader("Interactive Visualizations")
    
    with st.expander("Wind Patterns Analysis"):
        fig = plot_wind_distribution(cleaned_df)
        st.pyplot(fig)
    
    with st.expander("Variable Correlations"):
        corr_fig = plot_correlation_matrix(cleaned_df)
        st.plotly_chart(corr_fig, use_container_width=True)
    
    with st.expander("Temporal Analysis"):
        bubble_fig = interactive_bubble_chart(cleaned_df)
        st.plotly_chart(bubble_fig, use_container_width=True)
    
    with st.expander("Cleaning Impact Analysis"):
        cleaning_impact = analyze_cleaning_impact(cleaned_df)
        st.dataframe(cleaning_impact, use_container_width=True)

with tab4:
    st.subheader("Strategic Recommendations")
    recommendations = generate_recommendations(cleaned_df)
    
    cols = st.columns(len(recommendations))
    for (title, region), col in zip(recommendations.items(), cols):
        col.metric(title, region)
    
    st.subheader("Regional Performance Summary")
    st.dataframe(regional_summary(cleaned_df), use_container_width=True)

st.sidebar.markdown("### Settings")
st.sidebar.info("""
This application analyzes solar energy performance data across multiple regions.
Upload CSV files named like `RegionName_solar_data.csv` to begin analysis.
""")