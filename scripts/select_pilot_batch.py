"""Select a pilot batch of files from the enriched EFMC CSV.
Writes a `pilot_files.csv` listing filepaths to hash, and a `pilot_folders.csv` summary.

Usage:
  python scripts/select_pilot_batch.py --input GOV/reports/efmc_v5.3_file_level_decision_attribution_enriched.csv --target-bytes 2500000000 --out pilot_files.csv --summary pilot_folders.csv
"""
import argparse
import csv
from pathlib import Path
from collections import defaultdict

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--target-bytes', type=int, default=2500000000)
p.add_argument('--out', default='pilot_files.csv')
p.add_argument('--summary', default='pilot_folders.csv')
args = p.parse_args()

input_csv = Path(args.input)
out_csv = Path(args.out)
summary_csv = Path(args.summary)

# Determine EFMC root prefix to make relative grouping
# We'll group by the first component after the EFMC root path (common prefix in FILEPATH)
# Find common prefix by inspecting first path

paths = []
with open(input_csv, newline='', encoding='utf-8') as inf:
    rdr = csv.DictReader(inf)
    for r in rdr:
        fp = r.get('FILEPATH') or r.get('Filepath') or r.get('FILEPATH'.upper())
        if not fp:
            continue
        size = int(r.get('SIZE_BYTES') or r.get('SIZE_BYTES'.upper()) or 0)
        paths.append((fp, size))

# Compute grouping by top-level folder relative to EFMC root
# Detect EFMC root as the common prefix 'C:/Users/Tensh/Downloads/AI Studio/'.
# We'll find the longest common starting substring up to that path.

import os
common_prefix = os.path.commonprefix([p for p,s in paths[:100]])
# trim to nearest path separator
if '/' in common_prefix:
    lastsep = common_prefix.rfind('/')
else:
    lastsep = common_prefix.rfind('\\')
if lastsep != -1:
    efmc_root = common_prefix[:lastsep+1]
else:
    efmc_root = common_prefix

# Group by top-level folder under efmc_root
groups = defaultdict(lambda: {'bytes':0,'count':0,'files':[]})
for fp,size in paths:
    rel = fp
    if fp.startswith(efmc_root):
        rel = fp[len(efmc_root):]
    first = rel.split('/')[0].split('\\')[0]
    groups[first]['bytes'] += size
    groups[first]['count'] += 1
    groups[first]['files'].append((fp,size))

# Sort groups by bytes descending and pick until target
sorted_groups = sorted(groups.items(), key=lambda kv: kv[1]['bytes'], reverse=True)
selected = []
acc = 0
for name,data in sorted_groups:
    if acc >= args.target_bytes:
        break
    selected.append((name,data))
    acc += data['bytes']

# If none selected (all small), pick largest single folder
if not selected and sorted_groups:
    selected.append(sorted_groups[0])
    acc = selected[0][1]['bytes']

# Write pilot_files.csv
with open(out_csv, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['FILEPATH','SIZE_BYTES','TOP_FOLDER'])
    for name,data in selected:
        for fp,size in data['files']:
            w.writerow([fp,size,name])

# Write summary
with open(summary_csv, 'w', newline='', encoding='utf-8') as sf:
    w = csv.writer(sf)
    w.writerow(['TOP_FOLDER','bytes','files'])
    for name,data in selected:
        w.writerow([name,data['bytes'],data['count']])

print(f"Selected {len(selected)} top folders totalling {acc} bytes. Files written to {out_csv}. Summary: {summary_csv}")
