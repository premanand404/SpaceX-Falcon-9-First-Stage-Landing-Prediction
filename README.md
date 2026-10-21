# Notebook run order

1. `01_data_collection_api.ipynb` — fetch API snapshot.
2. `02_data_collection_web_scraping.ipynb` — scrape launch history.
3. `03_data_wrangling_and_eda.ipynb` — clean labels and explore the teaching sample.
4. `04_eda_with_sql.ipynb` — SQL queries in local SQLite.
5. `05_folium_interactive_map.ipynb` — create interactive map HTML.
6. `06_predictive_analysis.ipynb` — model comparison and evaluation.

The Dash app is in `src/dashboard.py`; start it from the repository root with `python -m src.dashboard`.
