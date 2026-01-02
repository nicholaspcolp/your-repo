"""Generate statistics and simple predictions related to manifests and manifest operations.
Writes GOV/reports/jarvis_metrics/metrics_<run_id>.json
"""
import json
from pathlib import Path
from datetime import datetime
import statistics

OUTDIR = Path('GOV/reports/jarvis_metrics')
OUTDIR.mkdir(parents=True, exist_ok=True)

# load manifest index
MANIFEST_INDEX = Path('WORK/JARVIS_BRAIN_OPERATIONS/manifest_sources/index.json')
PROV_DIR = Path('GOV/reconciliation/provenance')
PRIORITY = Path('WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv')

import uuid
now = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
run_id = f"{now}-{uuid.uuid4().hex[:8]}"

# helper: safe file read

def read_manifest_index():
    if not MANIFEST_INDEX.exists():
        return []
    return json.loads(MANIFEST_INDEX.read_text(encoding='utf-8')).get('manifests', [])


def read_provenance_dates():
    dates = []
    if not PROV_DIR.exists():
        return dates
    for p in PROV_DIR.glob('manifest_apply_provenance_*.json'):
        try:
            obj = json.loads(p.read_text(encoding='utf-8'))
            dates.append(obj.get('applied_at'))
        except Exception:
            continue
    return dates


def read_task_stats():
    tasks = []
    if not PRIORITY.exists():
        return tasks
    import csv
    with PRIORITY.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            tasks.append(r)
    return tasks

manifests = read_manifest_index()
prov_dates = read_provenance_dates()
tasks = read_task_stats()

metrics = {}
metrics['generated_at'] = datetime.utcnow().isoformat()+'Z'
metrics['manifest_count'] = len(manifests)
metrics['total_manifest_bytes'] = sum(m.get('size_bytes',0) for m in manifests)
metrics['last_applies_count'] = len(prov_dates)
metrics['pending_tasks'] = len([t for t in tasks if t.get('status') in ('todo','in-progress')])
metrics['tasks_total'] = len(tasks)

# simple prediction: estimate completion based on average elapsed per completed task if we had durations
# fallback: assume default 2 hours per task
completed = [t for t in tasks if t.get('status')=='completed']
# for the moment we don't have per-task durations; use default
avg_task_hours = 2.0
metrics['avg_task_hours'] = avg_task_hours
metrics['estimated_hours_to_complete_pending'] = metrics['pending_tasks'] * avg_task_hours

# shared-info confirmations (check other jarvis windows / recent chat)
recent_chat = Path('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
found_messages = []
if recent_chat.exists():
    with recent_chat.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            msg = obj.get('message','')
            if 'manifest' in msg.lower() or 'trial_manifest' in msg.lower() or 'preflight' in msg.lower():
                found_messages.append({'timestamp': obj.get('timestamp'), 'sender': obj.get('sender'), 'message': msg})
metrics['manifest_related_messages_found'] = len(found_messages)
metrics['manifest_message_samples'] = found_messages[:10]

out = OUTDIR / f'metrics_{now}.json'
out.write_text(json.dumps(metrics, indent=2), encoding='utf-8')
print('Wrote metrics to', out)
