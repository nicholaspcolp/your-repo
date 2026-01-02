"""Search C:\ for files matching name substrings or large size, skipping common system folders.
Writes results to specified CSV with timing and SHA256 where feasible.
"""
import argparse
import os
import time
import hashlib
from pathlib import Path
import csv

p = argparse.ArgumentParser()
p.add_argument('--root', default='C:\\')
p.add_argument('--name-substring', default='pr_patch')
p.add_argument('--min-bytes', type=int, default=10_000_000_000)
p.add_argument('--compute-sha', action='store_true', help='Compute SHA256 for matches (costly). Default: False')
p.add_argument('--out', default='GOV/reconciliation/fix_missing_results/system_search_candidates.csv')
# optional run/task linking for audits
p.add_argument('--run-id', default=None, help='Externally provided run id to link searches to a run')
p.add_argument('--task', default='', help='Optional task id or short label to attach to this run')
args = p.parse_args()

root = Path(args.root)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
sub = args.name_substring.lower()
minb = args.min_bytes
compute_sha = bool(args.compute_sha)

exclude_dirs = { 'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\ProgramData', 'C:\\$Recycle.Bin' }

start = time.time()
results = []
count = 0
for dirpath, dirnames, filenames in os.walk(root):
    # skip excluded prefixes
    rp = Path(dirpath)
    if any(str(rp).startswith(ed) for ed in exclude_dirs):
        continue
    for fname in filenames:
        try:
            fpath = Path(dirpath) / fname
            size = fpath.stat().st_size
        except Exception:
            continue
        found = False
        reason = ''
        if sub in fname.lower():
            found = True
            reason = f'name_contains:{sub}'
        if size >= minb:
            found = True
            reason = f'size>={minb}'
        if found:
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
            results.append({'path':str(fpath),'size':size,'sha':sha,'reason':reason})
            count += 1

end = time.time()
with open(out, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['path','size_bytes','sha256','reason'])
    for r in results:
        w.writerow([r['path'], r['size'], r['sha'], r['reason']])

# Write run-level audit record
import uuid, datetime
run_id = args.run_id if args.run_id else datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
task = args.task or ''
runs_csv = Path('GOV/reconciliation/fix_missing_results/search_runs.csv')
if not runs_csv.exists():
    with runs_csv.open('w', newline='', encoding='utf-8') as rf:
        wr = csv.writer(rf)
        wr.writerow(['run_id','timestamp','script','root','task','name_substring','min_bytes','compute_sha','elapsed_seconds','hits_count','out'])
with runs_csv.open('a', newline='', encoding='utf-8') as rf:
    wr = csv.writer(rf)
    wr.writerow([run_id, datetime.datetime.utcnow().isoformat()+'Z', 'search_system_for_pattern', str(root), task, sub, minb, compute_sha, f"{end-start:.2f}", count, str(out)])

print(f'Found {count} candidate(s) in {end-start:.2f}s; results written to {out}; run_id={run_id}')
