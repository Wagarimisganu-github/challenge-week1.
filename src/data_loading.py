import pandas as pd
from pathlib import Path
import logging
from typing import List
from .config import Config

logger = logging.getLogger(__name__)

def load_region_data(region: str) -> pd.DataFrame:
    """Load and validate regional dataset"""
    try:
        file_path = Config.DATA_DIR / f"{region}_solar_data.csv"
        logger.info(f"Loading data for {region} from {file_path}")
        
        df = pd.read_csv(
            file_path,
            parse_dates=[Config.DATE_COL],
            dtype={'Comments': 'category'}
        )
        df['Region'] = region.replace('_', ' ')
        return df
    except FileNotFoundError as e:
        logger.error(f"Data file not found for {region}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading data for {region}: {e}")
        raise

def load_all_regions_data() -> pd.DataFrame:
    """Load and merge all regional datasets"""
    dfs = []
    for region in Config.REGIONS:
        try:
            dfs.append(load_region_data(region))
        except Exception as e:
            logger.warning(f"Skipping {region} due to loading error: {e}")
            continue
    
    if not dfs:
        logger.error("No data loaded for any region")
        raise ValueError("No valid data available")
    
    return pd.concat(dfs, ignore_index=True)