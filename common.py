"""Shared data download and cleaning helpers for the capstone project."""
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

COURSE_BASES = [
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/",
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork/api/",
]
SQL_CSV_URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv"


def download_course_csv(filename: str, refresh: bool = False) -> Path:
    """Download a course CSV into data/; try both published IBM dataset paths."""
    out = DATA_DIR / filename
    if out.exists() and not refresh:
        return out
    errors = []
    for base in COURSE_BASES:
        url = base + filename
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            if not response.text.strip():
                raise ValueError("empty response")
            out.write_bytes(response.content)
            # Quick parse so HTML error pages do not silently become CSVs.
            pd.read_csv(out, nrows=3)
            return out
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Could not download course data. Check your internet connection and URL access.\n" + "\n".join(errors))


def load_course_csv(filename: str) -> pd.DataFrame:
    """Load an IBM course dataset, downloading it if absent."""
    return pd.read_csv(download_course_csv(filename))


def ensure_class(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with binary landing-success target Class where derivable."""
    out = df.copy()
    if "Class" in out.columns:
        out["Class"] = pd.to_numeric(out["Class"], errors="coerce")
        return out
    if "Outcome" in out.columns:
        # Course outcome strings typically begin True/False for attempted landings.
        s = out["Outcome"].astype(str).str.strip()
        out["Class"] = s.str.startswith("True", na=False).astype(int)
    elif "landing__outcome" in out.columns:
        s = out["landing__outcome"].astype(str).str.strip()
        out["Class"] = s.str.startswith("Success", na=False).astype(int)
    else:
        raise ValueError("Cannot derive Class: expected Class, Outcome, or landing__outcome column.")
    return out
