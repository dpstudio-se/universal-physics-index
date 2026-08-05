"""Evaluator: benchmarks versions against UPI RNA runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..adapters.upi_rna import UPI_RNA

CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "config"
BENCHMARKS_PATH = CONFIG_DIR / "benchmarks.yaml"


def load_benchmarks() -> list[dict[str, Any]]:
    """Load benchmark task definitions from benchmarks.yaml or benchmarks.json."""
    if not BENCHMARKS_PATH.exists():
        return []

    content = BENCHMARKS_PATH.read_text(encoding="utf-8").strip()

    try:
        import yaml
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            yaml_tasks: list[dict[str, Any]] = list(data.get("tasks", []))
            return yaml_tasks
    except ImportError:
        pass

    # Simple zero-dependency YAML line parser for tasks list
    tasks: list[dict[str, Any]] = []
    current_task: dict[str, Any] = {}

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- id:"):
            if current_task:
                tasks.append(current_task)
            current_task = {"id": line.split(":", 1)[1].strip().strip('"')}
        elif line.startswith("prompt:") and current_task:
            current_task["prompt"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("expected_keyword:") and current_task:
            current_task["expected_keyword"] = line.split(":", 1)[1].strip().strip('"')

    if current_task:
        tasks.append(current_task)

    return tasks



def evaluate(version_id: str) -> float:
    """Evaluate version against benchmarks returning fitness score in [0.0, 1.0]."""
    rna = UPI_RNA()
    tasks = load_benchmarks()

    if not tasks:
        return 0.0

    successes = 0

    for task in tasks:
        prompt = task.get("prompt", "")
        expected_keyword = task.get("expected_keyword", "").lower()

        if not prompt:
            continue

        try:
            res_str = rna.evaluate_physics(prompt)
            if expected_keyword in res_str.lower():
                successes += 1
        except Exception:
            continue

    return float(successes / max(len(tasks), 1))
