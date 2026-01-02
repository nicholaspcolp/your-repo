"""Search JARVIS for large files and filenames matching patterns. Writes CSV of candidates.
"""
import argparse
import os
import time
import hashlib
from pathlib import Path
import csv

p = argparse.ArgumentParser()
p.add_argument('--base', default=r'C:\\JARVISBRAINSURGERY')
p.add_argument('--min-bytes', type=int, default=5_000_000_000)
p.add_argument('--name-patterns', default='pr_patch|pfmc|patch|feature_reference')
p.add_argument('--exact-size', type=int, default=None)
p.add_argument('--compute-sha', action='store_true', help='Compute SHA256 for matches (costly). Default: False')
p.add_argument('--out', default='GOV/reconciliation/fix_missing_results/jarvis_candidates.csv')
# optional run/task linking for audit
p.add_argument('--run-id', default=None, help='Optional run id to attach to this search')
p.add_argument('--task', default='', help='Optional task label')
args = p.parse_args()
compute_sha = bool(args.compute_sha)

base = Path(args.base)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
patterns = [p.lower() for p in args.name_patterns.split('|') if p]

start = time.time()
count = 0
candidates = []
for root, dirs, files in os.walk(base):
    for fname in files:
        fpath = Path(root) / fname
        try:
            size = fpath.stat().st_size
        except Exception:
            continue
        matched = False
        if size >= args.min_bytes:
            matched = True
            reason = f'size>={args.min_bytes}'
        else:
            lname = fname.lower()
            for pat in patterns:
                if pat in lname:
                    matched = True
                    reason = f'name_contains:{pat}'
                    break
        if args.exact_size and size == args.exact_size:
            matched = True
            reason = f'exact_size:{args.exact_size}'
        if matched:
            # compute sha256 for candidate only when requested (may be expensive)
            sha = ''
            if compute_sha:
                try:
                    h = hashlib.sha256()
                    with open(fpath, 'rb') as fh:
                        while True:
                            b = fh.read(8*1024*1024)
                            if not b:
                                break
                            h.update(b)
                    sha = h.hexdigest()
                except Exception:
                    sha = ''
            candidates.append({'path':str(fpath), 'size':size, 'sha':sha, 'reason':reason})
            count += 1

end = time.time()
with open(out, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['path','size_bytes','sha256','reason'])
    for c in candidates:
        w.writerow([c['path'], c['size'], c['sha'], c['reason']])

# write run-level audit
import uuid, datetime
run_id = args.run_id if args.run_id else datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
task = args.task or ''
runs_csv = Path('GOV/reconciliation/fix_missing_results/search_runs.csv')
if not runs_csv.exists():
    with runs_csv.open('w', newline='', encoding='utf-8') as rf:
        wr = csv.writer(rf)
        wr.writerow(['run_id','timestamp','script','base','task','min_bytes','name_patterns','exact_size','compute_sha','elapsed_seconds','hits_count','out'])
with runs_csv.open('a', newline='', encoding='utf-8') as rf:
    wr = csv.writer(rf)
    wr.writerow([run_id, datetime.datetime.utcnow().isoformat()+'Z', 'search_jarvis_large_and_names', str(base), task, args.min_bytes, args.name_patterns, args.exact_size, compute_sha, f"{end-start:.2f}", count, str(out)])

print(f'Found {count} candidate(s) in {end-start:.2f}s; results written to {out}; run_id={run_id}')
