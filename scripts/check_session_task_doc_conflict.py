"""Check for sessions assigned both documentation and task work simultaneously.
Writes a defection row for any conflicts found.
Usage: python scripts/check_session_task_doc_conflict.py
"""
import csv
from pathlib import Path
from datetime import datetime

PRIORITY = Path('WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv')
ACTIVE = Path('GOV/reports/active_windows.json')
DEFECTIONS = Path('GOV/JARVIS/defections.csv')

# read tasks
sessions = {}
if PRIORITY.exists():
    with PRIORITY.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            sid = (r.get('assigned_session') or '').strip()
            if not sid:
                continue
            typ = r.get('type') or 'task'
            sessions.setdefault(sid, set()).add(typ)

# read active
active_ids = set()
if ACTIVE.exists():
    import json
    j = json.loads(ACTIVE.read_text(encoding='utf-8'))
    for s in j.get('active_sessions', []):
        active_ids.add(s.get('session_id'))

conflicts = []
for sid, types in sessions.items():
    if sid in active_ids and len(types) > 1:
        conflicts.append((sid, list(types)))

if conflicts:
    # record defection rows for each conflict
    for sid, types in conflicts:
        ts = datetime.utcnow().isoformat()+'Z'
        row = f'{ts},{sid},system,session-assigned-both-doc-and-task,Assigned types: {"/".join(types)},session-conflict\n'
        try:
            DEFECTIONS.parent.mkdir(parents=True, exist_ok=True)
            if not DEFECTIONS.exists():
                DEFECTIONS.write_text('timestamp,run_id,actor,summary,details,tags\n', encoding='utf-8')
            with DEFECTIONS.open('a', encoding='utf-8') as df:
                df.write(row)
        except Exception:
            pass
    print('Conflicts detected and recorded:', conflicts)
else:
    print('No session conflicts detected')
