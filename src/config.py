from pathlib import Path
import logging

class Config:
    DATA_DIR = Path("./data/raw/")
    OUTPUT_DIR = Path("./data/processed/")
    REGIONS = ['Benin', 'Sierraleon', 'Togo']
    SOLAR_COLS = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB']
    CLIMATE_COLS = ['Tamb', 'RH', 'WS', 'Precipitation']
    DATE_COL = 'Timestamp'

    @classmethod
    def setup(cls):
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.OUTPUT_DIR / 'processing.log'),
                logging.StreamHandler()
            ]
        )