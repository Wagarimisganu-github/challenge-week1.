import os
import sys

sys.path.append(os.path.abspath('..'))

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from src.config import Config
from src.data_loading import load_all_regions_data
from src.data_cleaning import generate_quality_report, clean_data
from src.analysis import calculate_regional_stats, analyze_cleaning_impact, generate_recommendations
from src.visualization import plot_wind_distribution, plot_correlation_matrix, plot_interactive_bubble
from src.vizual import plot_wind_distribution, plot_correlation_matrix, plot_interactive_bubble


# Streamlit App
st.set_page_config(page_title="Solar Energy Analysis", layout="wide")
st.title("Solar Energy Analysis Dashboard")

# Load Data
data = load_all_regions_data()
st.write("### Raw Data Sample")
st.dataframe(data.head())

# Data cleaning
cleaned_df = clean_data(data)
cleaned_df.to_parquet(Config.OUTPUT_DIR / "cleaned_data.parquet")

# Data Quality Report
if st.checkbox("Show Data Quality Report"):
    quality_report = generate_quality_report(data)
    st.write("### Data Quality Report")
    st.dataframe(quality_report)

# Data Cleaning
cleaned_data = clean_data(data)
if st.checkbox("Show Cleaned Data Sample"):
    st.write("### Cleaned Data Sample")
    st.dataframe(cleaned_data.head())

# Regional Summary
st.write("### Regional Summary Statistics")
st.dataframe(calculate_regional_stats(cleaned_data))

# Wind Distribution Plot
st.write("### Wind Distribution Analysis")
fig_wind = plot_wind_distribution(cleaned_data)
st.pyplot(fig_wind)

# Correlation Matrix Plot
st.write("### Correlation Matrix")
fig_corr = plot_correlation_matrix(cleaned_data)
st.pyplot(fig_corr)

# Interactive Bubble Chart
st.write("### Interactive Solar Analysis")
fig_bubble = plot_interactive_bubble(cleaned_data)
st.plotly_chart(fig_bubble)

# Strategic Recommendations
st.write("### Strategic Installation Recommendations")
recommendations = generate_recommendations(cleaned_data)
for key, value in recommendations.items():
    st.write(f"- **{key}:** {value}")

