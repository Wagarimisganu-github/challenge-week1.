import os
import sys

sys.path.append(os.path.abspath('..'))

import logging
from pathlib import Path
from src.config import Config
from src.data_loading import load_all_regions_data
from src.data_cleaning import generate_quality_report, clean_data
from src.analysis import calculate_regional_stats, analyze_cleaning_impact, generate_recommendations
from src.visualization import plot_wind_distribution, plot_correlation_matrix, plot_interactive_bubble

def main():
    Config.setup()
    logger = logging.getLogger(__name__)
    
    try:
        # Data loading
        logger.info("Starting data processing pipeline")
        raw_df = load_all_regions_data()
        logger.info(f"Loaded raw data with shape: {raw_df.shape}")
        
        # Data quality
        quality_report = generate_quality_report(raw_df)
        quality_report.to_csv(Config.OUTPUT_DIR / "data_quality_report.csv")
        
        # Data cleaning
        cleaned_df = clean_data(raw_df)
        cleaned_df.to_parquet(Config.OUTPUT_DIR / "cleaned_data.parquet")
        
        # Analysis
        regional_stats = calculate_regional_stats(cleaned_df)
        regional_stats.to_csv(Config.OUTPUT_DIR / "regional_stats.csv")
        
        cleaning_impact = analyze_cleaning_impact(cleaned_df)
        cleaning_impact.to_csv(Config.OUTPUT_DIR / "cleaning_impact.csv")
        
        # Visualization
        plot_wind_distribution(cleaned_df, Config.OUTPUT_DIR / "wind_distribution.png")
        plot_correlation_matrix(cleaned_df, Config.OUTPUT_DIR / "correlation_matrix")
        plot_interactive_bubble(cleaned_df, Config.OUTPUT_DIR / "bubble_chart.html")
        
        # Recommendations
        recommendations = generate_recommendations(cleaned_df)
        with open(Config.OUTPUT_DIR / "recommendations.txt", "w") as f:
            f.write("Strategic Installation Recommendations:\n")
            for k, v in recommendations.items():
                f.write(f"- {k}: {v}\n")
        logger.info("Recommendations generated successfully")
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()