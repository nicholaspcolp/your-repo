"""Search for files containing substrings of pilot basenames (case-insensitive).
Usage:
  python scripts/search_by_substring.py --pilot GOV/reports/efmc_pilot_files.csv --roots "C:\\Users\\Tensh\\Downloads\\AI Studio" --out GOV/reconciliation/fix_missing_results/search_substring_candidates.csv
"""
import argparse
import csv
import os
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--pilot', required=True)
p.add_argument('--roots', required=True, help='Semicolon-separated roots to search')
p.add_argument('--out', required=True)
args = p.parse_args()

pilot = Path(args.pilot)
roots = [Path(x) for x in args.roots.split(';') if x]
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

substrings = []
with open(pilot, newline='', encoding='utf-8') as inf:
    r = csv.DictReader(inf)
    for row in r:
        basename = Path(row['FILEPATH']).name
        name_no_ext = os.path.splitext(basename)[0]
        substrings.append(basename.lower())
        substrings.append(name_no_ext.lower())
        # also add tokens
        for token in name_no_ext.replace('_',' ').split():
            if len(token) > 3:
                substrings.append(token.lower())

# dedupe
substrings = list(dict.fromkeys(substrings))

matches = []
for root in roots:
    if not root.exists():
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            fn_l = fn.lower()
            for sub in substrings:
                if sub in fn_l:
                    full = Path(dirpath) / fn
                    try:
                        sz = full.stat().st_size
                    except Exception:
                        sz = ''
                    matches.append({'found':str(full), 'size':sz, 'matched_substring':sub})
                    break

# write
with open(out, 'w', newline='', encoding='utf-8') as outf:
    w = csv.writer(outf)
    w.writerow(['found_path','size_bytes','matched_substring'])
    for m in matches:
        w.writerow([m['found'], m['size'], m['matched_substring']])

print(f"Wrote substring matches to {out} ({len(matches)} matches)")
