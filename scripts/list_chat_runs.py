"""List chat JSONL runs across workspace and write an index to GOV/reports/jarvis_chats_index.csv
Usage: python scripts/list_chat_runs.py --out GOV/reports/jarvis_chats_index.csv
"""
import argparse
import csv
from pathlib import Path
import time

p = argparse.ArgumentParser()
p.add_argument('--out', default='GOV/reports/jarvis_chats_index.csv')
args = p.parse_args()

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

# search for jsonl files in workspace - simple walk from workspace root
workspace_root = Path('.').resolve()
files = list(workspace_root.rglob('*.jsonl'))

rows = []
for f in files:
    try:
        mt = f.stat().st_mtime
        sz = f.stat().st_size
    except Exception:
        mt = ''
        sz = ''
    rows.append({'path':str(f.resolve()), 'mtime':mt, 'size':sz})

with out.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['path','modified_epoch','size_bytes'])
    for r in rows:
        w.writerow([r['path'], r['mtime'], r['size']])

print(f'Wrote {len(rows)} entries to {out}')
