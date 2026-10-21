"""Reproducible SQLite version of the capstone EDA-with-SQL lab."""
from pathlib import Path
import sqlite3
import requests
import pandas as pd
from src.common import ROOT, OUTPUT_DIR, SQL_CSV_URL


def main():
    local = ROOT / "data" / "Spacex.csv"
    if not local.exists():
        r = requests.get(SQL_CSV_URL, timeout=30); r.raise_for_status(); local.write_bytes(r.content)
    df = pd.read_csv(local)
    # Normalize headers to their source labels; retain the original source values.
    df.columns = [str(c).strip() for c in df.columns]
    db_path = ROOT / "data" / "spacex_sql.sqlite"
    with sqlite3.connect(db_path) as conn:
        df.to_sql("SPACEXTBL", conn, if_exists="replace", index=False)
        queries = {
            "unique_launch_sites": "SELECT DISTINCT launch_site FROM SPACEXTBL ORDER BY launch_site",
            "nasa_crs_payload_mass": "SELECT SUM(payload_mass__kg_) AS total_payload_mass_kg FROM SPACEXTBL WHERE customer = 'NASA (CRS)'",
            "average_f9_v1_1_payload": "SELECT ROUND(AVG(payload_mass__kg_), 0) AS avg_payload_mass_kg FROM SPACEXTBL WHERE booster_version LIKE 'F9 v1.1%'",
            "first_successful_ground_pad_landing": "SELECT MIN(DATE) AS first_date FROM SPACEXTBL WHERE landing__outcome = 'Success (ground pad)'",
            "drone_ship_success_4k_6k": "SELECT booster_version FROM SPACEXTBL WHERE landing__outcome = 'Success (drone ship)' AND payload_mass__kg_ BETWEEN 4000 AND 6000 ORDER BY booster_version",
            "landing_outcome_counts": "SELECT landing__outcome, COUNT(*) AS rows FROM SPACEXTBL GROUP BY landing__outcome ORDER BY rows DESC",
            "success_vs_other_counts": "SELECT CASE WHEN landing__outcome LIKE 'Success%' THEN 'Success' ELSE 'Other' END AS outcome_group, COUNT(*) AS rows FROM SPACEXTBL GROUP BY outcome_group ORDER BY outcome_group",
            "max_payload_booster": "SELECT DISTINCT booster_version, payload_mass__kg_ FROM SPACEXTBL WHERE payload_mass__kg_ = (SELECT MAX(payload_mass__kg_) FROM SPACEXTBL)",
        }
        for name, query in queries.items():
            result = pd.read_sql_query(query, conn)
            result.to_csv(OUTPUT_DIR / f"sql_{name}.csv", index=False)
            print(f"\n-- {name}\n{result.to_string(index=False)}")
    print(f"\nLoaded {len(df)} source rows; SQL outputs saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
