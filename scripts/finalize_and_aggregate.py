"""finalize_and_aggregate.py

Produces:
- GOV/reconciliation/finalized_missing_manifest_reconciliation_v0.2.csv
- GOV/reports/efmc_v5.3_decision_size_summary_with_move_verification.csv
- prints counts and sizes for requested buckets
"""
import csv
from pathlib import Path
from collections import defaultdict

ENRICHED = Path("GOV/reports/efmc_v5.3_file_level_decision_attribution_enriched.csv")
MANIFEST = Path("GOV/EFMC 5.2 - VS_TRASH - SAFE_EXCLUDE_MOVE_MANIFEST_v0.2.csv")
OUT_DIR = Path("GOV/reconciliation/fix_missing_results")
OUT_DIR.mkdir(parents=True, exist_ok=True)

finalized = Path("GOV/reconciliation/finalized_missing_manifest_reconciliation_v0.2.csv")
summary_out = Path("GOV/reports/efmc_v5.3_decision_size_summary_with_move_verification.csv")

# 1) Finalized missing manifest rows
with open(MANIFEST, newline='', encoding='utf-8') as mf, open(finalized, 'w', newline='', encoding='utf-8') as outf:
    mreader = csv.DictReader(mf)
    fieldnames = list(mreader.fieldnames) + ['reason']
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()
    missing_count = 0
    for r in mreader:
        moved_path = (r.get('moved_path') or '').strip()
        moved_exists = (r.get('moved_exists') or '').strip().upper()
        if not moved_path or moved_exists != 'TRUE':
            reason = []
            if not moved_path:
                reason.append('no_moved_path')
            if moved_exists != 'TRUE':
                reason.append('moved_not_found')
            r['reason'] = ';'.join(reason)
            writer.writerow(r)
            missing_count += 1

print(f"Wrote finalized missing manifest reconciliation to {finalized} ({missing_count} rows)")

# 2) Aggregate decision-level summary with move verification
# Fields per row: DECISION, CATEGORY, total_bytes, total_files, moved_exists_bytes, moved_exists_files, moved_sha_match_bytes, moved_sha_match_files
agg = defaultdict(lambda: {'total_bytes':0,'total_files':0,'moved_exists_bytes':0,'moved_exists_files':0,'moved_sha_match_bytes':0,'moved_sha_match_files':0})
rows_count = 0

with open(ENRICHED, newline='', encoding='utf-8') as ef:
    reader = csv.DictReader(ef)
    for r in reader:
        rows_count += 1
        try:
            size = int(r.get('SIZE_BYTES') or r.get('SIZE_BYTES'.upper()) or r.get('SIZE_BYTES'.lower()) or 0)
        except:
            size = int(r.get('SIZE_BYTES') or 0)
        decision = (r.get('DECISION') or '').strip() or 'UNDETERMINED'
        cat = (r.get('CATEGORY') or '').strip() or 'UNDETERMINED'

        key = decision  # aggregate by DECISION; can also include CATEGORY
        agg[key]['total_bytes'] += size
        agg[key]['total_files'] += 1
        moved_exists = (r.get('moved_exists') or '').strip().upper()
        moved_sha_match = (r.get('moved_sha_match') or '').strip().upper()
        if moved_exists == 'TRUE':
            agg[key]['moved_exists_bytes'] += size
            agg[key]['moved_exists_files'] += 1
        if moved_sha_match == 'TRUE':
            agg[key]['moved_sha_match_bytes'] += size
            agg[key]['moved_sha_match_files'] += 1

# write summary CSV
with open(summary_out, 'w', newline='', encoding='utf-8') as sout:
    w = csv.writer(sout)
    w.writerow(['DECISION','total_bytes','total_files','moved_exists_bytes','moved_exists_files','moved_sha_match_bytes','moved_sha_match_files'])
    for k,v in sorted(agg.items()):
        w.writerow([k, v['total_bytes'], v['total_files'], v['moved_exists_bytes'], v['moved_exists_files'], v['moved_sha_match_bytes'], v['moved_sha_match_files']])

print(f"Wrote decision-level summary with move verification to {summary_out}")
print(f"EFMC entries (file-level rows): {rows_count}")

# 3) Compute requested buckets sizes and print for quick reference
# i) EFMC filespace (UNDETERMINED) -> sum where CATEGORY == 'UNDETERMINED'
undetermined_bytes = 0
determined_keep_bytes = 0
undetermined_files = 0
determined_keep_files = 0
external_total_bytes = 0
external_files = 0

with open(ENRICHED, newline='', encoding='utf-8') as ef:
    reader = csv.DictReader(ef)
    for r in reader:
        size = int(r.get('SIZE_BYTES') or 0)
        cat = (r.get('CATEGORY') or '').strip()
        # categorize
        if cat.upper() == 'UNDETERMINED':
            undetermined_bytes += size
            undetermined_files += 1
        elif cat.upper() == 'DETERMINED':
            # need to inspect DECISION or CATEGORY further; if DECISION indicates KEEP
            dec = (r.get('DECISION') or '').lower()
            if 'keep' in dec:
                determined_keep_bytes += size
                determined_keep_files += 1
        # external: files that should not be deleted but do not belong in filespace
        # Heuristic: moved_path near GOV/TRASH? or flagged in a specific decision like 'external'
        dec = (r.get('DECISION') or '').lower()
        if 'external' in dec or 'external' in cat.lower():
            external_total_bytes += size
            external_files += 1

print('Computed requested buckets (printed below).')
print(f"UNDETERMINED: {undetermined_files} files, {undetermined_bytes} bytes")
print(f"DETERMINED KEEP: {determined_keep_files} files, {determined_keep_bytes} bytes")
print(f"EXTERNAL: {external_files} files, {external_total_bytes} bytes")

# write a simple JSON-like summary to out dir
import json
summary = {
    'efmc_entries': rows_count,
    'undetermined': {'files': undetermined_files, 'bytes': undetermined_bytes},
    'determined_keep': {'files': determined_keep_files, 'bytes': determined_keep_bytes},
    'external': {'files': external_files, 'bytes': external_total_bytes}
}
with open(OUT_DIR / 'final_summary.json', 'w', encoding='utf-8') as jf:
    json.dump(summary, jf, indent=2)

print(f"Wrote final summary to {OUT_DIR / 'final_summary.json'}")
