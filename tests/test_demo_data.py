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
    for section_id in ("welcome", "goal-dataset", "gate-spec", "isolated-run", "verdict"):
        assert f'id="{section_id}"' in page
    for contract_id in (
        "run-form",
        "run-button",
        "timeline",
        "gate-grid",
        "nosana-model",
        "sandbox-id",
        "exit-code",
        "duration",
    ):
        assert f'id="{contract_id}"' in page


def test_static_assets_use_root_paths_and_light_design_tokens() -> None:
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    styles = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")

    assert 'href="/styles.css"' in page
    assert 'src="/app.js"' in page
    assert '<meta name="color-scheme" content="light"' in page
    assert '<meta name="theme-color" content="#F4F7FB"' in page
    assert "--surface-canvas: #F4F7FB" in styles
    assert "--surface-card: #FFFFFF" in styles
    assert "--action-primary: #2563EB" in styles
    assert "grid-template-columns: 240px minmax(0, 1fr)" in styles
    assert "@media (prefers-reduced-motion: reduce)" in styles


def test_demo_fixtures_are_explicitly_labeled_in_the_ui() -> None:
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert page.count('data-i18n="demoBadge"') == 2
    assert 'demoDataLabel: { ko: "MVP 데모 · 센서 CSV 예시"' in script


def test_product_copy_covers_research_data_and_assigns_platform_roles() -> None:
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'heroTitle: { ko: "연구에 쓰기 전에, 데이터를 증명합니다."' in script
    assert "논문·연구에 사용할 데이터" in script
    assert "data for research and paper development" in script
    assert "This MVP demonstrates the workflow with sensor CSV files." in script
    assert "Nosana constrained specification" in script
    assert "Daytona verdict" in script
    for misleading_copy in (
        "Nosana 모델의 판단",
        "Nosana model decision",
        "Nosana 판단과 실행 정보",
        "Nosana decision and runtime evidence",
    ):
        assert misleading_copy not in script


def test_desktop_spa_shows_one_workflow_panel_without_document_scroll() -> None:
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    styles = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert '<body data-active-stage="welcome">' in page
    assert ".main-content > section { display: none; }" in styles
    assert 'body[data-active-stage="verdict"] #verdict { display: block; }' in styles
    assert "grid-template-rows: 64px minmax(0, 1fr) 44px" in styles
    assert "height: 100vh" in styles
    assert "document.body.dataset.activeStage = stage" in script


def test_root_mount_serves_page_and_assets_without_404() -> None:
    from fastapi.testclient import TestClient

    from app import app

    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/styles.css").status_code == 200
    assert client.get("/app.js").status_code == 200


def test_frontend_uses_backend_forbidden_columns_gate_id() -> None:
    script = (Path(__file__).resolve().parents[1] / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    assert '{ id: "forbidden_columns", labelKey: "gateLeakageColumns" }' in script
