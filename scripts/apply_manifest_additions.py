#!/usr/bin/env python3
"""Apply candidate manifest additions to the main manifest (non-destructive).

- Backs up original manifest to .bak.<tag>
- Writes patched manifest: <manifest>.patched.<tag>
- Produces determination actions CSV (SAFE_EXCLUDE) for added rows
- Appends artifacts to latest reviewer package
- Appends a decision note to `communication/shared/decisions-log.md`

Requires: run manually after reviewer approval.
"""
from pathlib import Path
from datetime import datetime
import csv
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / 'GOV'
MANIFEST = GOV / 'EFMC 5.2 - VS_TRASH - SAFE_EXCLUDE_MOVE_MANIFEST_v0.4_retry.csv'
RECON_DIR = GOV / 'reconciliation'
CAND = sorted(RECON_DIR.glob('manifest_additions_*.csv'))
if not CAND:
    print('No candidate manifest additions found in', RECON_DIR)
    # write audit row and defection so silent no-op is recorded
    try:
        audit = Path('GOV/jarvis/audit_manifest_changes.csv')
        with audit.open('a', newline='', encoding='utf-8') as af:
            aw = csv.writer(af)
            aw.writerow([datetime.utcnow().isoformat()+'Z', str(MANIFEST), '', 'SYSTEM', False, 0, '', '', 'No candidate manifest additions found in reconciliation dir'])
    except Exception:
        pass
    try:
        defs = Path('GOV/JARVIS/defections.csv')
        with defs.open('a', newline='', encoding='utf-8') as df:
            df.write(f"{datetime.utcnow().isoformat()}Z,,script,No candidate manifest additions found in reconciliation dir,Manual followup may be needed,manifest,open\n")
    except Exception:
        pass
    sys.exit(2)
cand = CAND[-1]

if not MANIFEST.exists():
    print('Manifest not found:', MANIFEST)
    sys.exit(2)

# acquire manifest lock before modify
import subprocess
lock_res = subprocess.run(['python','scripts/file_locker.py','lock','--file',str(MANIFEST),'--owner','apply_manifest_additions','--note','apply-manifest'])
if lock_res.returncode != 0:
    print('ERROR: Failed to acquire lock on manifest; aborting apply')
    sys.exit(4)
# backup original manifest
tag = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
bak = MANIFEST.with_suffix(MANIFEST.suffix + f'.bak.{tag}')
shutil.copy2(MANIFEST, bak)
print('Backed up manifest to', bak)

# Read existing SHAs to avoid duplicates
existing_shas = set()
with MANIFEST.open('r', encoding='utf-8', newline='') as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        sha = (r.get('sha256') or r.get('sha') or r.get('sha_expected') or r.get('sha256_expected') or '').strip()
        if sha:
            existing_shas.add(sha)

# Read candidate rows and filter out any already-present
candidates = []
with cand.open('r', encoding='utf-8', newline='') as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        sha = (r.get('sha256') or r.get('sha') or '').strip()
        if sha in existing_shas:
            print('Skipping already-present sha:', sha)
            continue
        candidates.append(r)

if not candidates:
    print('No new candidates to apply after deduplication')
    # release manifest lock (we acquired earlier)
    try:
        subprocess.run(['python','scripts/file_locker.py','unlock','--file',str(MANIFEST),'--owner','apply_manifest_additions'])
    except Exception:
        pass
    # write audit row noting no-op for traceability
    audit = RECON_DIR.parent.joinpath('jarvis').joinpath('audit_manifest_changes.csv')
    try:
        with audit.open('a', newline='', encoding='utf-8') as af:
            aw = csv.writer(af)
            aw.writerow([datetime.utcnow().isoformat()+'Z', str(MANIFEST), str(cand), 'SYSTEM', False, 0, '', '', 'No candidates to apply; no-op'])
    except Exception:
        pass
    sys.exit(0)

# Require approval before applying manifest additions
import json, datetime as _dt
approval_needed = True
# Attempt to find a valid approval for this manifest
approvals_csv = Path('GOV/jarvis/manifest_approvals.csv')
approval_id = None
if approvals_csv.exists():
    with approvals_csv.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('manifest')==str(MANIFEST):
                # simple TTL check
                try:
                    exp = _dt.datetime.fromisoformat(r.get('expires_at').replace('Z','+00:00'))
                    if exp > _dt.datetime.now(_dt.timezone.utc):
                        approval_id = r.get('approval_id')
                        approval_needed = False
                        break
                except Exception:
                    continue

if approval_needed:
    print('ERROR: No valid approval found for manifest. Use scripts/manifest_approval.py to approve. Aborting apply.')
    sys.exit(5)

# Create patched manifest by appending candidates
patched = MANIFEST.with_name(MANIFEST.stem + f'.patched.{tag}' + MANIFEST.suffix)
with MANIFEST.open('r', encoding='utf-8', newline='') as fin, patched.open('w', encoding='utf-8', newline='') as fout:
    # copy original contents
    data = fin.read()
    fout.write(data)
    # ensure the file ends with a newline
    if not data.endswith('\n'):
        fout.write('\n')
    # append candidates (preserve header columns of MANIFEST)
    manifest_fieldnames = ['version','timestamp','sha256','original_path','size_bytes','canonical_path','moved_path','move_status','error','relocation_status']
    writer = csv.DictWriter(fout, fieldnames=manifest_fieldnames)
    for c in candidates:
        # normalize keys
        out_row = {
            'version': c.get('version','v0.4-reconcile'),
            'timestamp': c.get('timestamp', datetime.utcnow().isoformat()+'Z'),
            'sha256': c.get('sha256') or c.get('sha') or '',
            'original_path': c.get('original_path',''),
            'size_bytes': c.get('size_bytes',''),
            'canonical_path': c.get('canonical_path', c.get('original_path','')),
            'moved_path': c.get('moved_path',''),
            'move_status': c.get('move_status','MOVED'),
            'error': c.get('error',''),
            'relocation_status': c.get('relocation_status','RELOCATED'),
        }
        writer.writerow(out_row)

print('Wrote patched manifest:', patched)

# Write determination actions (mark SAFE_EXCLUDE for each candidate sha)
det_csv = RECON_DIR / f'determination_actions_{tag}.csv'
with det_csv.open('w', encoding='utf-8', newline='') as fh:
    fieldnames = ['sha256','moved_path','decision','notes','applied_at']
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()
    for c in candidates:
        writer.writerow({'sha256': c.get('sha256') or c.get('sha') or '',
                         'moved_path': c.get('moved_path',''),
                         'decision': 'SAFE_EXCLUDE',
                         'notes': 'Added via reconciliation after reviewer approval; canonical present in external trash',
                         'applied_at': datetime.utcnow().isoformat()+'Z'})
print('Wrote determination actions:', det_csv)

# Append artifacts to reviewer package
pkg_dir = GOV / 'reviewer_packages'
pkgs = sorted(pkg_dir.glob('MOVE_RETRY_v0.4_reviewer_package_*.zip'))
if pkgs:
    latest = pkgs[-1]
    import zipfile
    with zipfile.ZipFile(latest, 'a', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(str(patched), arcname=patched.name)
        z.write(str(det_csv), arcname=det_csv.name)
    print('Appended patched manifest and determination to reviewer package:', latest)
else:
    print('No reviewer package found to append to')

# write provenance JSON for this apply
try:
    prov_dir = RECON_DIR / 'provenance'
    prov_dir.mkdir(parents=True, exist_ok=True)
    prov = prov_dir / f'manifest_apply_provenance_{tag}.json'
    prov_obj = {
        'applied_at': datetime.utcnow().isoformat()+'Z',
        'patched_manifest': str(patched),
        'backup': str(bak),
        'candidates_count': len(candidates),
        'determinaton_file': str(det_csv),
        'approval_id': approval_id or '',
        'applier': 'USER (apply_manifest_additions.py)',
    }
    prov.write_text(json.dumps(prov_obj, indent=2), encoding='utf-8')
    print('Wrote provenance JSON to', prov)
except Exception:
    pass

# release manifest lock
subprocess.run(['python','scripts/file_locker.py','unlock','--file',str(MANIFEST),'--owner','apply_manifest_additions'])

# Append a decision note to communications log
decisions_log = ROOT / 'communication' / 'shared' / 'decisions-log.md'
decisions_log.parent.mkdir(parents=True, exist_ok=True)
with decisions_log.open('a', encoding='utf-8') as fh:
    now = datetime.utcnow().isoformat()+'Z'
    fh.write(f'{now} | Decision: APPLY_MANIFEST_RECONCILE | Applied {len(candidates)} candidate row(s) from {cand.name} to manifest {MANIFEST.name} (patched: {patched.name}). Reviewer: USER APPROVED.\n')
print('Appended decision entry to', decisions_log)

# Append an audit record for the manifest change
from pathlib import Path as __P
audit = __P('GOV/jarvis/audit_manifest_changes.csv')
if audit.exists():
    with audit.open('a', newline='', encoding='utf-8') as af:
        aw = csv.writer(af)
        aw.writerow([datetime.utcnow().isoformat()+'Z', str(MANIFEST), str(cand), 'USER', False, len(candidates), str(bak), approval_id or '', 'Applied manifest additions via apply_manifest_additions.py'])

# Print a short summary
print('SUMMARY: applied', len(candidates), 'rows; patched manifest at', patched.name)
