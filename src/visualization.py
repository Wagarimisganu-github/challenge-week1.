import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import logging
from pathlib import Path
from .config import Config

logger = logging.getLogger(__name__)

def plot_wind_distribution(df: pd.DataFrame, save_path: Path) -> None:
    """Generate and save wind distribution plots"""
    try:
        fig = plt.figure(figsize=(15, 5))
        for i, region in enumerate(Config.REGIONS, 1):
            ax = fig.add_subplot(1, 3, i, projection='polar')
            region_data = df[df['Region'] == region]
            theta = np.radians(region_data['WD'])
            r = region_data['WS']
            scatter = ax.scatter(theta, r, alpha=0.5, c=region_data['Tamb'], cmap='viridis')
            ax.set_title(f'{region} Wind Patterns', pad=20)
        plt.colorbar(scatter, label='Temperature (°C)')
        plt.savefig(save_path)
        plt.close()
        logger.info(f"Saved wind distribution plot to {save_path}")
    except Exception as e:
        logger.error(f"Error generating wind plot: {e}")
        raise

def plot_correlation_matrix(df: pd.DataFrame, save_path: Path) -> None:
    """Generate and save correlation matrix as both HTML and PNG"""
    try:
        corr_df = df[Config.SOLAR_COLS + Config.CLIMATE_COLS].corr()
        
        # Save interactive HTML
        fig = px.imshow(
            corr_df,
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1,
            title='Variable Correlation Matrix'
        )
        fig.write_html(str(save_path.with_suffix('.html')))
        
        # Save static image
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_df, annot=True, cmap='RdBu', vmin=-1, vmax=1)
        plt.title('Correlation Matrix')
        plt.savefig(save_path.with_suffix('.png'))
        plt.close()
        
        logger.info(f"Saved correlation matrix to {save_path}.*")
    except Exception as e:
        logger.error(f"Error generating correlation matrix: {e}")
        raise

def plot_interactive_bubble(df: pd.DataFrame, save_path: Path) -> None:
    """Create and save interactive bubble chart"""
    try:
        if Config.DATE_COL not in df.columns:
            raise ValueError("Missing timestamp column for animation")
        
        fig = px.scatter(
            df,
            x='Tamb',
            y='GHI',
            size='WS',
            color='RH',
            animation_frame=df[Config.DATE_COL].dt.month,
            hover_name='Region',
            size_max=40,
            title='Interactive Solar Analysis'
        )
        fig.write_html(str(save_path))
        logger.info(f"Saved bubble chart to {save_path}")
    except KeyError as e:
        logger.error(f"Missing required column for bubble chart: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating bubble chart: {e}")
        raise