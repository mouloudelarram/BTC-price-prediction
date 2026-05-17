"""Utility helpers for Correlation Engine."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Save dictionary as JSON file."""
    ensure_dir(file_path.parent)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file as dictionary."""
    if not file_path.exists():
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)


def timestamp_now() -> str:
    """Get current ISO timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def rotate_file(file_path: Path, max_count: int = 5) -> None:
    """Rotate files by renaming old versions."""
    if not file_path.exists():
        return

    old_dir = file_path.parent / "old"
    ensure_dir(old_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = file_path.suffix
    stem = file_path.stem
    new_name = f"{stem}_{timestamp}{suffix}"
    new_path = old_dir / new_name

    file_path.rename(new_path)

    # Clean up old files if exceeding max_count
    old_files = sorted(list(old_dir.glob(f"{stem}_*{suffix}")))
    if len(old_files) > max_count:
        for old_file in old_files[:-max_count]:
            old_file.unlink()
