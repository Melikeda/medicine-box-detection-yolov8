"""YOLO weight path resolver tests."""

from __future__ import annotations

from pathlib import Path

from src.services.model_paths import (
    candidate_model_paths,
    missing_model_help,
    resolve_default_model_path,
)


def test_resolve_prefers_first_existing_candidate(tmp_path: Path) -> None:
    nested = (
        tmp_path
        / "runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt"
    )
    train_out = (
        tmp_path / "runs/detect/medicine_box_yolov8n/weights/best.pt"
    )
    train_out.parent.mkdir(parents=True)
    train_out.write_bytes(b"fake")

    resolved = resolve_default_model_path(tmp_path)
    assert resolved == train_out.resolve()

    nested.parent.mkdir(parents=True)
    nested.write_bytes(b"fake")
    resolved_nested = resolve_default_model_path(tmp_path)
    assert resolved_nested == nested.resolve()


def test_resolve_falls_back_to_primary_when_missing(tmp_path: Path) -> None:
    resolved = resolve_default_model_path(tmp_path)
    assert resolved == candidate_model_paths(tmp_path)[0]
    assert not resolved.exists()


def test_missing_model_help_lists_candidates() -> None:
    help_text = missing_model_help()
    assert "YOLO weights not found" in help_text
    assert "models/best.pt" in help_text
    assert "src/train.py" in help_text
