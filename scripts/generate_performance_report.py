"""Generate a JARVIS performance report for a run/task.
Usage:
  python scripts/generate_performance_report.py --run RUN_ID --task TASK_ID --out GOV/reports/jarvis_performance/report_<run>.json

This collects run/task metadata (from chat_index.csv and search_runs.csv) and produces a short JSON report skeleton.
"""
import argparse, json
from pathlib import Path
from datetime import datetime
import csv

p = argparse.ArgumentParser()
p.add_argument('--run', required=True)
p.add_argument('--task', required=True)
p.add_argument('--out', required=True)
args = p.parse_args()

OUT=Path(args.out)
OUT.parent.mkdir(parents=True, exist_ok=True)

report = {
    'report_id': args.run,
    'task_id': args.task,
    'generated_at': datetime.utcnow().isoformat()+'Z',
    'start_snapshot': None,
    'end_snapshot': None,
    'predictions': [],
    'actuals': [],
    'notes': []
}

# read chat_index
idx = Path('GOV/JARVIS/chat_index.csv')
if idx.exists():
    with idx.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['run_id']==args.run:
                report['start_snapshot']=r.get('start_timestamp')
                report['end_snapshot']=r.get('end_timestamp')
                break

# pull relevant search runs for this run_id
sr = Path('GOV/reconciliation/fix_missing_results/search_runs.csv')
related_searches=[]
if sr.exists():
    with sr.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if args.run in r.get('run_id',''):
                related_searches.append(r)

report['notes'].append(f"Related searches: {len(related_searches)}")

# simple KPI placeholders
report['predictions'].append({'name':'expected_find_rate','value':'20%', 'note':'initially optimistic'})
report['actuals'].append({'name':'found_count','value':0})

with OUT.open('w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print(f'Wrote report to {OUT}')
