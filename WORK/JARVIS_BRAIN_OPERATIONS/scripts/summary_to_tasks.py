#!/usr/bin/env python3
"""summary_to_tasks.py
Convert summaries into proposed task candidates (PoC).
Writes PROGRESS/summary_actions_<ts>.json and optionally appends to priority_tasks_m8_candidates.csv
"""
from pathlib import Path
import json, datetime, csv

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / 'PROGRESS'
PRIORITY_CSV = ROOT / 'priority_tasks_m8_candidates.csv'


def process_summary(path: Path, append_to_csv: bool = False):
    j = json.loads(path.read_text(encoding='utf-8'))
    actions = j.get('summary',{}).get('actions',[])
    proposals = []
    for a in actions:
        proposals.append({'session_id': j.get('session_id'), 'window_id': j.get('window_id'), 'text': a})
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    outp = PROG / f'summary_actions_{j.get("session_id")}_{ts}.json'
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({'session_id': j.get('session_id'), 'actions': proposals, 'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2, ensure_ascii=False), encoding='utf-8')
    if append_to_csv:
        exist = PRIORITY_CSV.exists()
        with PRIORITY_CSV.open('a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if not exist:
                w.writerow(['id','title','owner','status','priority','created_at','notes','assigned_umbrella'])
            for idx,a in enumerate(proposals):
                rowid = f"AUTO-{j.get('session_id')}-{idx}"
                w.writerow([rowid, a['text'], '', 'todo', 'medium', datetime.datetime.now(datetime.timezone.utc).isoformat(), f"from_summary:{j.get('session_id')}", ''])
    return outp


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('path')
    p.add_argument('--append-csv', action='store_true')
    args = p.parse_args()
    p = process_summary(Path(args.path), append_to_csv=args.append_csv)
    print('Wrote', p)
