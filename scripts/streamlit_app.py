import os
import sys
sys.path.append(os.path.abspath('..'))

import streamlit as st
import pandas as pd
from src.config import Config
from src.data_loading import load_all_regions_data
from src.data_cleaning import generate_quality_report, clean_data
from src.analysis import calculate_regional_stats, analyze_cleaning_impact, generate_recommendations
from src.visualization import plot_wind_distribution, plot_correlation_matrix, plot_interactive_bubble
from pathlib import Path

# Streamlit setup
st.set_page_config(page_title="Solar Energy Dashboard", layout="wide")
st.title("Solar Energy Analysis Dashboard")

# Load data
st.sidebar.header("Data Loading")
if st.sidebar.button("Load Data"):
    try:
        df = load_all_regions_data()
        st.session_state['df'] = df
        st.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Display raw data
if 'df' in st.session_state:
    df = st.session_state['df']
    st.subheader("Raw Data")
    st.dataframe(df.head())
    
    # Quality Report
    st.subheader("Data Quality Report")
    quality_report = generate_quality_report(df)
    st.dataframe(quality_report)
    
    # Clean Data
    st.sidebar.header("Data Cleaning")
    if st.sidebar.button("Clean Data"):
        df_clean = clean_data(df)
        st.session_state['df_clean'] = df_clean
        st.success("Data cleaned successfully!")
    
    if 'df_clean' in st.session_state:
        df_clean = st.session_state['df_clean']
        st.subheader("Cleaned Data")
        st.dataframe(df_clean.head())
    
    # Analysis
    st.subheader("Regional Statistics")
    stats = calculate_regional_stats(df_clean)
    st.dataframe(stats)
    
    st.subheader("Cleaning Impact Analysis")
    cleaning_impact = analyze_cleaning_impact(df_clean)
    st.dataframe(cleaning_impact)
    
    st.subheader("Installation Recommendations")
    recommendations = generate_recommendations(df_clean)
    for key, value in recommendations.items():
        st.write(f"**{key}:** {value}")
    
    # Visualization
    st.subheader("Visualizations")
    save_path = Path(Config.OUTPUT_DIR) / "plots"
    save_path.mkdir(parents=True, exist_ok=True)
    
    if st.button("Generate Wind Distribution Plot"):
        plot_wind_distribution(df_clean, save_path / "wind_plot.png")
        st.image(str(save_path / "wind_plot.png"), caption="Wind Distribution")
    
    if st.button("Generate Correlation Matrix"):
        plot_correlation_matrix(df_clean, save_path / "correlation_matrix")
        st.image(str(save_path / "correlation_matrix.png"), caption="Correlation Matrix")
    
    if st.button("Generate Interactive Bubble Chart"):
        plot_interactive_bubble(df_clean, save_path / "bubble_chart.html")
        st.markdown(f"[View Interactive Bubble Chart](./data/processed/plots/bubble_chart.html)", unsafe_allow_html=True)
