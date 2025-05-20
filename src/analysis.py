import pandas as pd
import logging
from typing import Dict
from .config import Config

logger = logging.getLogger(__name__)

def calculate_regional_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Generate key statistics by region"""
    try:
        stats = df.groupby('Region').agg({
            'GHI': ['mean', 'std', 'max'],
            'DNI': ['median', 'max'],
            'Tamb': ['mean', 'std'],
            'WS': ['mean', 'max'],
            'Precipitation': 'sum'
        })
        return stats.round(2)
    except KeyError as e:
        logger.error(f"Missing required column for stats: {e}")
        raise
    except Exception as e:
        logger.error(f"Error calculating regional stats: {e}")
        raise

def analyze_cleaning_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Quantify cleaning effects on module performance"""
    try:
        clean_events = df[df['Cleaning'] == 1].index
        results = []
        
        for idx in clean_events:
            if idx > 3 and idx < len(df)-3:
                pre = df.loc[idx-3:idx-1, ['ModA', 'ModB']].mean()
                post = df.loc[idx+1:idx+3, ['ModA', 'ModB']].mean()
                results.append({
                    'Region': df.at[idx, 'Region'],
                    'ModA_Improvement': post['ModA'] - pre['ModA'],
                    'ModB_Improvement': post['ModB'] - pre['ModB']
                })
        
        return pd.DataFrame(results).groupby('Region').mean()
    except KeyError as e:
        logger.error(f"Missing required column for cleaning analysis: {e}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing cleaning impact: {e}")
        raise

def generate_recommendations(df: pd.DataFrame) -> Dict[str, str]:
    """Generate data-driven installation recommendations"""
    try:
        analysis = df.groupby('Region').agg({
            'GHI': ['mean', 'std'],
            'DNI': 'median',
            'Tamb': ['mean', 'std'],
            'Precipitation': 'sum',
            'WSgust': 'max'
        }).round(2)

        return {
            'Best Overall Potential': analysis[('GHI', 'mean')].idxmax(),
            'Most Stable Radiation': analysis[('GHI', 'std')].idxmin(),
            'Lowest Maintenance Risk': analysis[('Precipitation', 'sum')].idxmin(),
            'Optimal CSP Location': analysis[('DNI', 'median')].idxmax()
        }
    except KeyError as e:
        logger.error(f"Missing required column for recommendations: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise