#!/usr/bin/env python3
"""Simple task API for creating task drafts to be ingested into the live TODO list.
Tasks are written to `GOV/reports/jarvis_trials/task_drafts_<ts>.json` for review and/or automated ingestion by the parser.
"""
import json
from datetime import datetime
from pathlib import Path

OUT_DIR = Path('GOV/reports/jarvis_trials')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def now_ts():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def create_task_draft(title, description, owner=None, lifecycle_status='prelim-planning', percent_complete=0, subtasks=None, verification_steps=None, requester_type='anyjarvis', hold=False, severity='low', dependencies=None, eta=None):
    task = {
        'title': title,
        'description': description,
        'owner': owner,
        'lifecycle_status': lifecycle_status,
        'percent_complete': percent_complete,
        'subtasks': subtasks or [],
        'verification_steps': verification_steps or [],
        'requester_type': requester_type,
        'hold': bool(hold),
        'severity': severity,
        'dependencies': dependencies or [],
        'eta': eta,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    out = OUT_DIR / f'task_draft_{now_ts()}.json'
    out.write_text(json.dumps(task, indent=2))
    print('Wrote task draft:', out)
    return out


if __name__ == '__main__':
    # simple demo
    create_task_draft('Rotate PAT for runner', 'Automated: token failed auth — rotate PAT and authorize for SSO if needed', owner='tensh', severity='high')