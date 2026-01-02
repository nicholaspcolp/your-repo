"""Compute overall percent complete from the latest task_inventory file.

Usage:
  python scripts/compute_overall_progress.py
Outputs JSON to stdout: {"percent_complete": <float>, "completed": int, "total": int}
"""
import json
from pathlib import Path
from datetime import datetime

PROGRESS = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS')


def latest_task_inventory():
    files = sorted(PROGRESS.glob('task_inventory_*.json'))
    return files[-1] if files else None


def compute():
    p = latest_task_inventory()
    if not p:
        print(json.dumps({'percent_complete': 0.0, 'completed': 0, 'total': 0}))
        return 0.0
    j = json.loads(p.read_text(encoding='utf-8'))
    tasks = j.get('tasks', [])
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('status') in ('completed','done'))
    percent = (completed / total * 100.0) if total else 0.0
    print(json.dumps({'percent_complete': round(percent,2), 'completed': completed, 'total': total}))
    return percent


if __name__ == '__main__':
    compute()
