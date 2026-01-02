"""Generate consolidated task inventory from TRIAL_MANIFEST.json and priority_tasks.csv

Usage:
  python scripts/generate_task_inventory.py

Writes: WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/task_inventory_<ts>.json
"""
import json
from pathlib import Path
from datetime import datetime
import csv

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'TRIAL_MANIFEST.json'
PRIORITY = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'priority_tasks.csv'
PROGRESS = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'PROGRESS'


def iso_now():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def load_manifest_tasks():
    if not MANIFEST.exists():
        return []
    j = json.loads(MANIFEST.read_text(encoding='utf-8'))
    tasks = j.get('tasks', [])
    out = []
    for t in tasks:
        out.append({
            'id': t.get('id'),
            'title': t.get('title'),
            'owner': t.get('owner'),
            'status': t.get('status'),
            'priority': t.get('priority'),
            'origin': t.get('origin'),
            'last_updated': t.get('last_updated'),
            'notes': t.get('notes'),
            'source': 'trial_manifest'
        })
    return out


def load_priority_csv():
    out = []
    if not PRIORITY.exists():
        return out
    with PRIORITY.open('r', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        for row in r:
            out.append({
                'id': row.get('id'),
                'title': row.get('title'),
                'owner': row.get('owner'),
                'status': row.get('status'),
                'priority': row.get('priority'),
                'created_at': row.get('created_at'),
                'updated_at': row.get('updated_at'),
                'notes': row.get('notes'),
                'assigned_session': row.get('assigned_session'),
                'type': row.get('type'),
                'source': 'priority_csv'
            })
    return out


def main():
    PROGRESS.mkdir(parents=True, exist_ok=True)
    tasks = []
    tasks.extend(load_manifest_tasks())
    tasks.extend(load_priority_csv())
    out = {'generated_at': datetime.utcnow().isoformat()+'Z', 'task_count': len(tasks), 'tasks': tasks}
    out_path = PROGRESS / f'task_inventory_{iso_now()}.json'
    out_path.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(str(out_path))


if __name__ == '__main__':
    from datetime import datetime
    main()