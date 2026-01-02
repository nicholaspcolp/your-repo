"""Search for missing pilot files by basename under candidate base directories.
Writes `GOV/reconciliation/fix_missing_results/search_missing_candidates.csv` with columns:
  sha (if known), expected_path, basename, candidate_path, candidate_size, candidate_sha, match_type

Usage:
  python scripts/search_missing_sources.py --pilot GOV/reports/efmc_pilot_files.csv --candidates "C:\\JARVISBRAINSURGERY;C:\\Users\\Tensh\\Downloads\\AI Studio.worktrees" --out GOV/reconciliation/fix_missing_results/search_missing_candidates.csv
"""
import argparse
import csv
import hashlib
from pathlib import Path
import os

p = argparse.ArgumentParser()
p.add_argument('--pilot', required=True)
p.add_argument('--candidates', required=True, help="Semicolon-separated base dirs to search")
p.add_argument('--compute-sha', action='store_true', help='Compute SHA256 for matches (costly). Default: False')
p.add_argument('--out', required=True)
# optional run/task link
p.add_argument('--run-id', default=None, help='Optional run id to attach to this search')
p.add_argument('--task', default='', help='Optional task label')
args = p.parse_args()
compute_sha = bool(args.compute_sha)

pilot = Path(args.pilot)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
base_dirs = [Path(x) for x in args.candidates.split(';') if x]

# Helper
def sha256_of_file(path, chunk_size=8*1024*1024):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                b = f.read(chunk_size)
                if not b:
                    break
                h.update(b)
    except Exception as e:
        return None
    return h.hexdigest()

# read pilot and collect missing entries
missing = []
with open(pilot, newline='', encoding='utf-8') as inf:
    r = csv.DictReader(inf)
    for row in r:
        fp = row.get('FILEPATH')
        size = int(row.get('SIZE_BYTES') or 0)
        if not Path(fp).exists():
            missing.append({'expected':fp, 'basename':Path(fp).name, 'size':size})

# search
results = []
for m in missing:
    basename = m['basename']
    expected = m['expected']
    for base in base_dirs:
        if not base.exists():
            continue
        # Walk but limit depth reasonably (say 6)
        for root, dirs, files in os.walk(base):
            if basename in files:
                cand = Path(root) / basename
                try:
                    sz = cand.stat().st_size
                except Exception:
                    sz = ''
                cand_sha = ''
                if compute_sha:
                    cand_sha = sha256_of_file(cand)
                match_type = 'basename_found'
                if m['size'] and sz == m['size']:
                    match_type = 'basename_size_match'
                results.append({'expected_path':expected,'basename':basename,'candidate_path':str(cand),'candidate_size':sz,'candidate_sha':cand_sha,'match_type':match_type})

# write results
with open(out, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['expected_path','basename','candidate_path','candidate_size','candidate_sha','match_type'])
    for r in results:
        w.writerow([r['expected_path'],r['basename'],r['candidate_path'],r['candidate_size'],r['candidate_sha'],r['match_type']])

print(f"Wrote candidates to {out} ({len(results)} matches found)")

# write run-level audit
import uuid, datetime
run_id = args.run_id if args.run_id else datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
task = args.task or ''
runs_csv = Path('GOV/reconciliation/fix_missing_results/search_runs.csv')
if not runs_csv.exists():
    with runs_csv.open('w', newline='', encoding='utf-8') as rf:
        wr = csv.writer(rf)
        wr.writerow(['run_id','timestamp','script','pilot','task','candidates','compute_sha','hits_count','out'])
with runs_csv.open('a', newline='', encoding='utf-8') as rf:
    wr = csv.writer(rf)
    wr.writerow([run_id, datetime.datetime.utcnow().isoformat()+'Z', 'search_missing_sources', str(pilot), task, args.candidates, compute_sha, len(results), str(out)])

print(f'run_id={run_id}')
