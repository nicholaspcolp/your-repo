import csv
from pathlib import Path
import sys

inp = Path(sys.argv[1]) if len(sys.argv)>1 else Path('GOV/reports/efmc_pilot_files.csv')
out = Path(sys.argv[2]) if len(sys.argv)>2 else Path('GOV/reports/efmc_pilot_files_filtered.csv')
exclude = set()
# read pilot_missing_items.csv to build exclude set
pm = Path('GOV/reconciliation/fix_missing_results/pilot_missing_items.csv')
if pm.exists():
    with pm.open(newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            exclude.add(row.get('FILEPATH'))

with inp.open(newline='', encoding='utf-8') as inf, out.open('w', newline='', encoding='utf-8') as outf:
    r = csv.DictReader(inf)
    w = csv.DictWriter(outf, fieldnames=r.fieldnames)
    w.writeheader()
    kept=0
    skipped=0
    for row in r:
        fp = row.get('FILEPATH')
        if fp in exclude:
            skipped+=1
            continue
        w.writerow(row)
        kept+=1
print(f'Wrote {out} (kept={kept}, skipped={skipped})')
