"""enrich_efmc_metadata.py

Usage:
  python scripts/enrich_efmc_metadata.py \
    --filelist GOV/reports/efmc_v5.3_file_level_decision_attribution.csv \
    --manifest "GOV/EFMC 5.2 - VS_TRASH - SAFE_EXCLUDE_MOVE_MANIFEST_v0.2.csv" \
    --out GOV/reports/efmc_v5.3_file_level_decision_attribution_enriched.csv

What it does:
- Reads the per-file EFMC attribution CSV (has FILEPATH,SIZE_BYTES,DECISION,CATEGORY)
- Reads the manifest and builds a mapping by canonical_path and original_path (normalized)
- For each file row, attempts to match manifest entry and attaches moved_path,moved_exists,moved_sha_match,sha256
- Writes enriched CSV with the new columns appended
"""

import argparse
import csv
from pathlib import Path


def norm_path(p):
    if not p:
        return ''
    return str(Path(p).as_posix()).replace('\\', '/').lower()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--filelist', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    filelist = Path(args.filelist)
    manifest = Path(args.manifest)
    out = Path(args.out)

    # build manifest map
    manifest_map = {}
    with open(manifest, newline='', encoding='utf-8') as mfin:
        mreader = csv.DictReader(mfin)
        for r in mreader:
            sha = r.get('sha256')
            cand_paths = [r.get('canonical_path') or '', r.get('original_path') or '']
            for cp in cand_paths:
                key = norm_path(cp)
                if not key:
                    continue
                manifest_map[key] = {
                    'sha256': sha,
                    'moved_path': r.get('moved_path',''),
                    'moved_exists': r.get('moved_exists',''),
                    'moved_sha_match': r.get('moved_sha_match',''),
                    'move_status': r.get('move_status',''),
                }

    with open(filelist, newline='', encoding='utf-8') as fin, open(out, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames + ['manifest_sha256','moved_path','moved_exists','moved_sha_match','move_status']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in reader:
            fp = r.get('FILEPATH')
            k = norm_path(fp)
            m = manifest_map.get(k)
            if m:
                r['manifest_sha256'] = m.get('sha256')
                r['moved_path'] = m.get('moved_path')
                r['moved_exists'] = m.get('moved_exists')
                r['moved_sha_match'] = m.get('moved_sha_match')
                r['move_status'] = m.get('move_status')
            else:
                r['manifest_sha256'] = ''
                r['moved_path'] = ''
                r['moved_exists'] = ''
                r['moved_sha_match'] = ''
                r['move_status'] = ''
            writer.writerow(r)

    print(f"Wrote enriched file to {out}")

if __name__ == '__main__':
    main()
