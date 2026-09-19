"""Deterministic contract tests for GateTrace's demo sensor datasets."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
REQUIRED_COLUMNS = {
    "timestamp",
    "equipment_id",
    "temperature_c",
    "vibration_mm_s",
    "pressure_bar",
    "rpm",
    "failure_within_1h",
}
FEATURE_COLUMNS = (
    "temperature_c",
    "vibration_mm_s",
    "pressure_bar",
    "rpm",
)
FORBIDDEN_LEAKAGE_COLUMNS = {
    "failure_timestamp",
    "future_failure",
    "future_failure_label",
}
MAX_MISSING_RATE = 0.05


def load_dataset(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or ()), list(reader)


def missing_rate(rows: list[dict[str, str]]) -> float:
    cells = [row[column].strip() for row in rows for column in FEATURE_COLUMNS]
    return sum(not cell for cell in cells) / len(cells)


def timestamps(rows: list[dict[str, str]]) -> list[datetime]:
    return [datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")) for row in rows]


def test_clean_dataset_passes_all_four_gates() -> None:
    columns, rows = load_dataset("clean_sensor.csv")

    assert rows
    assert REQUIRED_COLUMNS.issubset(columns)  # schema gate
    assert missing_rate(rows) <= MAX_MISSING_RATE  # missing-rate gate
    assert timestamps(rows) == sorted(timestamps(rows))  # time-order gate
    assert FORBIDDEN_LEAKAGE_COLUMNS.isdisjoint(columns)  # leakage-column gate


def test_contaminated_dataset_fails_exactly_the_expected_three_gates() -> None:
    columns, rows = load_dataset("contaminated_sensor.csv")

    gate_results = {
        "schema": REQUIRED_COLUMNS.issubset(columns),
        "missing_rate": missing_rate(rows) <= MAX_MISSING_RATE,
        "time_order": timestamps(rows) == sorted(timestamps(rows)),
        "leakage_columns": FORBIDDEN_LEAKAGE_COLUMNS.isdisjoint(columns),
    }

    assert gate_results == {
        "schema": True,
        "missing_rate": False,
        "time_order": False,
        "leakage_columns": False,
    }


def test_demo_labels_are_binary_and_cover_both_outcomes() -> None:
    for name in ("clean_sensor.csv", "contaminated_sensor.csv"):
        _, rows = load_dataset(name)
        labels = {row["failure_within_1h"] for row in rows}
        assert labels == {"0", "1"}


def test_static_ui_has_language_persistence_and_exact_run_contract() -> None:
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'const DEFAULT_LANGUAGE = "both"' in script
    assert 'window.localStorage.getItem(LANGUAGE_STORAGE_KEY)' in script
    assert 'window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language)' in script
    assert 'fetch("/api/runs"' in script
    assert "dataset_id: selected" in script
    assert "research_goal:" in script
    for response_field in (
        "run_id",
        "status",
        "verdict",
        "gates",
        "summary",
        "timeline",
        "sandbox_id",
        "nosana_model_id",
        "duration_ms",
    ):
        assert f"payload.{response_field}" in script


def test_static_page_exposes_three_language_modes_and_four_steps() -> None:
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    assert page.count('class="language-button"') == 3
    assert all(f'data-language="{mode}"' in page for mode in ("ko", "en", "both"))
    assert page.count("<li data-step=") == 4
    assert 'id="nosana-model"' in page
    assert 'id="sandbox-id"' in page
    assert 'id="exit-code"' in page
    assert 'id="duration"' in page


def test_root_mount_serves_page_and_assets_without_404() -> None:
    from fastapi.testclient import TestClient

    from app import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/styles.css").status_code == 200
    assert client.get("/app.js").status_code == 200
