import pandas as pd
import numpy as np
import logging
from typing import Tuple
from .config import Config

logger = logging.getLogger(__name__)

def generate_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Generate comprehensive data quality report"""
    try:
        report = pd.DataFrame({
            'Missing': df.isna().sum(),
            'Zeros': (df == 0).sum(),
            'Negatives': (df.select_dtypes(include=np.number) < 0).sum()
        })
        
        ranges = {
            'GHI': (0, 1500),
            'RH': (0, 100),
            'Tamb': (-20, 60)
        }
        
        for col, (min_val, max_val) in ranges.items():
            if col in df.columns:
                report.loc[col, 'Out of Range'] = ((df[col] < min_val) | (df[col] > max_val)).sum()
        
        return report
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline with outlier handling"""
    try:
        logger.info("Starting data cleaning process")
        
        # Handle missing values
        df_clean = df.drop(columns='Comments', errors='ignore').ffill()
        
        # Validate numerical ranges
        for col in Config.SOLAR_COLS:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(lower=0)
        
        if 'RH' in df_clean.columns:
            df_clean['RH'] = df_clean['RH'].clip(0, 100)
        
        # Outlier removal
        for col in Config.SOLAR_COLS + ['Tamb', 'WS']:
            if col in df_clean.columns:
                q1 = df_clean[col].quantile(0.25)
                q3 = df_clean[col].quantile(0.75)
                iqr = q3 - q1
                df_clean = df_clean[(df_clean[col] >= q1 - 1.5*iqr) 
                                  & (df_clean[col] <= q3 + 1.5*iqr)]
        
        logger.info(f"Cleaned data shape: {df_clean.shape}")
        return df_clean.reset_index(drop=True)
    except Exception as e:
        logger.error(f"Data cleaning failed: {e}")
        raise