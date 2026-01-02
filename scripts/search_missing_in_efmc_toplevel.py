"""Search EFMC top-level folders for missing pilot basenames.
- Reads pilot file list (CSV) and finds missing entries.
- Determines EFMC top-level folders under the workspace root (the directories directly under the root path of filepaths in pilot CSV).
- Walks each top-level folder and searches for files with matching basenames (case-insensitive).
- Computes SHA-256 for any found candidates.
- Writes results to specified output CSV with timing and stats.

Usage:
  python scripts/search_missing_in_efmc_toplevel.py --pilot GOV/reports/efmc_pilot_files.csv --workspace-root "C:/Users/Tensh/Downloads/AI Studio" --out GOV/reconciliation/fix_missing_results/efmc_toplevel_search.csv
"""
import argparse
import csv
import hashlib
import os
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--pilot', required=True)
p.add_argument('--workspace-root', required=True)
p.add_argument('--compute-sha', action='store_true', help='Compute SHA256 for matches (costly). Default: False')
p.add_argument('--out', required=True)
# optional linking to a higher-level run/task
p.add_argument('--run-id', default=None, help='Optional run id to attach to this search')
p.add_argument('--task', default='', help='Optional task label')
args = p.parse_args()

pilot = Path(args.pilot)
root = Path(args.workspace_root)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
compute_sha = bool(args.compute_sha)

# read pilot and find missing basenames
missing_basenames = set()
missing_map = {}  # basename -> expected path
with open(pilot, newline='', encoding='utf-8') as inf:
    r = csv.DictReader(inf)
    for row in r:
        fp = row.get('FILEPATH')
        if not fp:
            continue
        pth = Path(fp)
        if not pth.exists():
            b = pth.name
            missing_basenames.add(b)
            missing_map[b] = fp

if not missing_basenames:
    print('No missing pilot files to search for.')
    exit(0)

# find top-level folders under root (exclude files)
top_level = []
for entry in root.iterdir():
    if entry.is_dir():
        top_level.append(entry)

print(f"Searching {len(top_level)} top-level folders under {root} for {len(missing_basenames)} missing basenames")
start = time.time()
results = []

# prepare lowercase set for case-insensitive compare
missing_lower = {b.lower() for b in missing_basenames}

for tl in top_level:
    print(f"Scanning top-level folder: {tl.name}")
    for dirpath, dirnames, filenames in os.walk(tl):
        for fname in filenames:
            if fname.lower() in missing_lower:
                fpath = Path(dirpath) / fname
                try:
                    size = fpath.stat().st_size
                except Exception as e:
                    size = ''
                # compute sha only when requested
                sha = None
                if compute_sha:
                    try:
                        h = hashlib.sha256()
                        with open(fpath, 'rb') as fh:
                            while True:
                                chunk = fh.read(8*1024*1024)
                                if not chunk:
                                    break
                                h.update(chunk)
                        sha = h.hexdigest()
                    except Exception:
                        sha = None
                results.append({'basename':fname,'expected_path':missing_map.get(fname,''),'found_path':str(fpath),'size_bytes':size,'sha256':sha,'top_level':tl.name})

end = time.time()
elapsed = end - start

with open(out, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['basename','expected_path','found_path','size_bytes','sha256','top_level'])
    for r in results:
        w.writerow([r['basename'],r['expected_path'],r['found_path'],r['size_bytes'],r['sha256'],r['top_level']])

# run-level audit record
import uuid, datetime
run_id = args.run_id if args.run_id else datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
task = args.task or ''
runs_csv = Path('GOV/reconciliation/fix_missing_results/search_runs.csv')
if not runs_csv.exists():
    with runs_csv.open('w', newline='', encoding='utf-8') as rf:
        wr = csv.writer(rf)
        wr.writerow(['run_id','timestamp','script','workspace_root','task','compute_sha','elapsed_seconds','hits_count','out'])
with runs_csv.open('a', newline='', encoding='utf-8') as rf:
    wr = csv.writer(rf)
    wr.writerow([run_id, datetime.datetime.utcnow().isoformat()+'Z', 'search_missing_in_efmc_toplevel', str(root), task, compute_sha, f"{elapsed:.2f}", len(results), str(out)])

print(f"Search complete in {elapsed:.2f}s. Found {len(results)} matches. Results written to {out}; run_id={run_id}")
