"""Run the main analysis tasks; network access is required for first data download."""
from src.analyze_spacex import run_eda, run_models
from src.eda_sql import main as run_sql
from src.folium_map import main as run_map

if __name__ == "__main__":
    run_eda()
    run_sql()
    run_map()
    run_models()
