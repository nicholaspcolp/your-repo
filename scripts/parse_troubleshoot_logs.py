#!/usr/bin/env python3
"""Parse the latest troubleshoot logs and generate follow-up tasks summary.
Writes `GOV/reports/jarvis_trials/followups_<ts>.json` with suggested tasks.
"""
import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path('GOV/reports/jarvis_trials')
LOG_DIR.mkdir(parents=True, exist_ok=True)


def now_ts():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def find_latest_troubleshoot():
    files = sorted(LOG_DIR.glob('troubleshoot_*.json'))
    return files[-1] if files else None


def parse_and_suggest():
    latest = find_latest_troubleshoot()
    if not latest:
        print('No troubleshoot logs found')
        return None
    data = json.loads(latest.read_text(encoding='utf-8'))
    findings = data.get('findings', [])
    suggestions = []
    from scripts.task_api import create_task_draft
    for f in findings:
        if f.get('step') == 'token' and f.get('status') in ('fail','error'):
            suggestions.append({'title':'Rotate or fix PAT','severity':'high','reason':f.get('text') or f.get('error')})
            # also create a task draft
            create_task_draft('Rotate PAT for runner', f"Token auth failed: {f.get('text') or f.get('error')}", owner='tensh', severity='high', lifecycle_status='prelim-planning', requester_type='anyjarvis')
        if f.get('step') == 'repo' and f.get('status') == 'fail':
            suggestions.append({'title':'Grant repo access to token','severity':'medium','reason':f.get('text')})
            create_task_draft('Grant repo access to token', f"Repo access check failed: {f.get('text')}", owner='tensh', severity='medium', lifecycle_status='prelim-planning', requester_type='anyjarvis')
    out = {'generated_at': datetime.utcnow().isoformat()+'Z','source': str(latest),'suggestions': suggestions}
    outp = LOG_DIR / f'followups_{now_ts()}.json'
    outp.write_text(json.dumps(out, indent=2))
    print('Wrote followups:', outp)
    return outp


if __name__ == '__main__':
    parse_and_suggest()
