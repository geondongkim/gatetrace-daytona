from __future__ import annotations

import csv
from pathlib import Path


_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DATASET_FILES = {
    "clean": "clean_sensor.csv",
    "contaminated": "contaminated_sensor.csv",
}


def get_dataset(dataset_id: str) -> list[dict[str, object]]:
    """Load one of the two allowlisted demo datasets; no user path is accepted."""
    with (_DATA_DIR / _DATASET_FILES[dataset_id]).open(encoding="utf-8", newline="") as source:
        return [dict(row) for row in csv.DictReader(source)]


def dataset_profile(dataset_id: str) -> dict[str, object]:
    rows = get_dataset(dataset_id)
    columns = sorted({key for row in rows for key in row})
    return {"dataset_id": dataset_id, "columns": columns, "row_count": len(rows)}
