#!/usr/bin/env python3
"""Compute progress statistics from WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/ and update TRIAL_MANIFEST.json.

Outputs:
- WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS_STATS.json
- updates `progress_stats` field in `TRIAL_MANIFEST.json`

Stats computed per task: owner, latest_status, percent_complete (max), last_updated, provenance sample, defection_count.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
PROGRESS_DIR = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS')
TRIAL_MANIFEST = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
OUT = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS_STATS.json')


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_manifest():
    if not TRIAL_MANIFEST.exists():
        return None
    return json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))


def compute_stats():
    files = list(PROGRESS_DIR.glob('*.json')) if PROGRESS_DIR.exists() else []
    task_records = {}
    for p in files:
        try:
            obj = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        tid = obj.get('task_id') or obj.get('task') or obj.get('taskId')
        if not tid:
            continue
        recs = task_records.setdefault(tid, [])
        recs.append({'file': str(p.name), 'obj': obj})

    stats = {'generated_at': _now_iso(), 'tasks': {}}
    for tid, recs in task_records.items():
        percent = None
        latest_ts = None
        latest_status = None
        owner = None
        defection_count = 0
        provenance_sample = None
        events_count = 0
        latest_notes = []
        for r in recs:
            o = r['obj']
            events_count += 1
            ts = o.get('last_updated') or o.get('timestamp') or o.get('generated_at')
            try:
                parsed = datetime.fromisoformat(ts) if ts else None
            except Exception:
                parsed = None
            if parsed and (latest_ts is None or parsed > latest_ts):
                latest_ts = parsed
                latest_status = o.get('status') or o.get('marker') or latest_status
            pval = o.get('percent_complete')
            if isinstance(pval, int) or isinstance(pval, float):
                if percent is None or pval > percent:
                    percent = pval
            if o.get('defection_flag'):
                defection_count += 1
            if not provenance_sample and o.get('provenance'):
                provenance_sample = o.get('provenance')
            # fallback provenance fields
            if not provenance_sample and (o.get('agent') or o.get('agent_id') or o.get('owner')):
                provenance_sample = {
                    'agent_id': o.get('agent_id') or o.get('agent') or o.get('owner'),
                    'rolecard_id': o.get('rolecard_id') or None,
                    'applied_rule': o.get('applied_rule') or None
                }
            # collect brief notes for summary
            note = o.get('notes') or o.get('note') or o.get('message')
            if note:
                latest_notes.append(str(note))
            if not owner and (o.get('owner') or o.get('agent_id') or o.get('agent')):
                owner = o.get('owner') or o.get('agent_id') or o.get('agent')

        # Create a short progress_summary from the most recent notes
        progress_summary = None
        if latest_notes:
            # prefer the last note
            progress_summary = latest_notes[-1]
            if len(progress_summary) > 200:
                progress_summary = progress_summary[:197] + '...'

        # enrich provenance sample with agent_version and executor_id if present
        if provenance_sample:
            if isinstance(provenance_sample, dict):
                provenance_sample.setdefault('agent_version', None)
                provenance_sample.setdefault('executor_id', None)
            else:
                provenance_sample = {'agent_id': str(provenance_sample), 'agent_version': None, 'executor_id': None}

        stats['tasks'][tid] = {
            'owner': owner,
            'latest_status': latest_status,
            'percent_complete': percent or 0,
            'last_updated': latest_ts.isoformat() if latest_ts else None,
            'defection_count': defection_count,
            'provenance_sample': provenance_sample,
            'events_count': events_count,
            'progress_summary': progress_summary
        }

    return stats


def save_stats(stats):
    OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')


def update_manifest(stats):
    m = load_manifest()
    if m is None:
        return False
    m['progress_stats'] = stats
    m['progress_stats_updated_at'] = _now_iso()
    TRIAL_MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')
    return True


def main():
    stats = compute_stats()
    save_stats(stats)
    ok = update_manifest(stats)
    print('Wrote PROGRESS_STATS.json, manifest updated' if ok else 'Wrote PROGRESS_STATS.json, manifest missing')


if __name__ == '__main__':
    main()
