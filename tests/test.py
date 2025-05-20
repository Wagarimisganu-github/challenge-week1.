import os
import sys
sys.path.append(os.path.abspath('..'))
import unittest
import pandas as pd
import numpy as np
from src.data_loading import load_all_regions_data
from src.data_cleaning import clean_data
from src.visualization import plot_wind_distribution, plot_correlation_matrix, plot_interactive_bubble
from src.config import Config


class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        """Load sample data before each test"""
        self.df = load_all_regions_data()
        self.cleaned_df = clean_data(self.df)

    def test_data_loading(self):
        """Test if data is loaded correctly"""
        self.assertFalse(self.df.empty, "Loaded dataset should not be empty")
        self.assertIn('Region', self.df.columns, "Dataset should contain 'Region' column")
    
    def test_data_cleaning(self):
        """Test if cleaning removes invalid values"""
        self.assertFalse(self.cleaned_df.isna().sum().sum(), "Cleaned dataset should have no missing values")
        self.assertTrue((self.cleaned_df[Config.SOLAR_COLS] >= 0).all().all(), "Solar columns should have non-negative values")
    


if __name__ == "__main__":
    unittest.main()