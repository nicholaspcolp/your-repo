"""Produce a manifest governance status report based on the trial manifest and approvals.
Writes GOV/reports/manifest_governance_status.json
Usage: python scripts/manifest_governance_status.py --manifest WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json --out GOV/reports/manifest_governance_status.json
"""
import argparse
import json
from pathlib import Path
from datetime import datetime

p = argparse.ArgumentParser()
p.add_argument('--manifest', default='WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
p.add_argument('--out', default='GOV/reports/manifest_governance_status.json')
args = p.parse_args()

manifest = Path(args.manifest)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

if not manifest.exists():
    print('Manifest not found:', manifest)
    raise SystemExit(2)

m = json.loads(manifest.read_text(encoding='utf-8'))
# approvals
approvals = []
appr = Path('GOV/jarvis/manifest_approvals.csv')
if appr.exists():
    import csv
    with appr.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            approvals.append(r)
# locks
locks = []
locks_csv = Path('GOV/jarvis/locks.csv')
if locks_csv.exists():
    import csv
    with locks_csv.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            locks.append(r)

report = {
    'generated_at': datetime.utcnow().isoformat()+'Z',
    'manifest': str(manifest),
    'defection_capture': m.get('defection_capture', False),
    'dry_run': m.get('dry_run', True),
    'max_changes': m.get('max_changes'),
    'approval_gates': m.get('approval_gates', []),
    'approvals_count': len(approvals),
    'approvals': approvals,
    'locks': locks
}
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Wrote governance status to', out)