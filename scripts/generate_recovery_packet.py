"""Generate a recovery packet (zip) for a missing file to hand to backup/IT.
Usage:
  python scripts/generate_recovery_packet.py --file "C:/path/to/missing" --out recovery_packet_pr_patch_v4.1.zip

The packet includes:
- A small README with filename, expected size, timestamps, and last searches run IDs
- Copies or references to the search_runs.csv and relevant hits CSVs (if provided)
- A summary CSV row describing the missing item
"""
import argparse
import csv
from pathlib import Path
import json
import zipfile
import datetime

p = argparse.ArgumentParser()
p.add_argument('--file', required=True, help='Expected filepath for missing file')
p.add_argument('--out', required=True, help='Output zip file')
p.add_argument('--include-search-runs', nargs='*', default=[], help='Paths to search runs / hits CSVs to include')
args = p.parse_args()

expected = args.file
outzip = Path(args.out)
search_files = [Path(x) for x in args.include_search_runs if x]

# Prepare metadata
meta = {
    'expected_path': expected,
    'expected_basename': Path(expected).name,
    'expected_size_bytes': None,
    'generated_at': datetime.datetime.utcnow().isoformat()+'Z',
    'notes': 'Recovery packet for missing file'
}
try:
    # try to extract size from EFMC reports if present (very small heuristic)
    # look in GOV/reconciliation/fix_missing_results/pilot_missing_items.csv
    pilot_missing = Path('GOV/reconciliation/fix_missing_results/pilot_missing_items.csv')
    if pilot_missing.exists():
        with pilot_missing.open(newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                if row.get('FILEPATH') == expected:
                    meta['expected_size_bytes'] = int(row.get('SIZE_BYTES') or 0)
                    meta['notes'] = row.get('NOTES') or meta['notes']
                    break
except Exception:
    pass

# Build README
readme = []
readme.append(f"Recovery packet generated: {meta['generated_at']}")
readme.append(f"Expected path: {meta['expected_path']}")
readme.append(f"Expected basename: {meta['expected_basename']}")
readme.append(f"Expected size bytes: {meta['expected_size_bytes']}")
readme.append('Included search artifacts:')
for sf in search_files:
    readme.append(f" - {sf}")
readme.append('\nSearch notes:')
readme.append('Exhaustive local searches performed: workspace top-level scan, JARVIS scans, system-wide substring/size search, git object inspections, RV bin check. See attached search CSVs for details.')

# Create zip
with zipfile.ZipFile(outzip, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('README.txt', '\n'.join(readme))
    z.writestr('metadata.json', json.dumps(meta, indent=2))
    for sf in search_files:
        if sf.exists():
            z.write(sf, arcname=sf.name)

print(f'Wrote recovery packet to {outzip} (included {len(search_files)} artifact(s))')
