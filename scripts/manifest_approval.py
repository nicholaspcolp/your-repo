"""Simple CLI to create and list human approvals for manifest changes.
Usage:
  python scripts/manifest_approval.py approve --manifest WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json --actor alice --reason "approved for test"
  python scripts/manifest_approval.py list
  python scripts/manifest_approval.py revoke --id APPROVAL_ID
"""
import argparse
import csv
import uuid
from datetime import datetime, timedelta
from pathlib import Path

APPROVALS = Path('GOV/jarvis/manifest_approvals.csv')
if not APPROVALS.parent.exists():
    APPROVALS.parent.mkdir(parents=True, exist_ok=True)
if not APPROVALS.exists():
    with APPROVALS.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['approval_id','timestamp','manifest','actor','reason','expires_at'])

p = argparse.ArgumentParser()
sp = p.add_subparsers(dest='cmd')

ap = sp.add_parser('approve')
ap.add_argument('--manifest', required=True)
ap.add_argument('--actor', required=True)
ap.add_argument('--reason', required=True)
ap.add_argument('--ttl-hours', type=int, default=24, help='How long the approval is valid')

ls = sp.add_parser('list')

rv = sp.add_parser('revoke')
rv.add_argument('--id', required=True)

args = p.parse_args()

if args.cmd == 'approve':
    aid = uuid.uuid4().hex[:8]
    ts = datetime.utcnow().isoformat() + 'Z'
    exp = (datetime.utcnow() + timedelta(hours=args.ttl_hours)).isoformat() + 'Z'
    with APPROVALS.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([aid, ts, args.manifest, args.actor, args.reason, exp])
    # write a notification row for alerting humans / audit
    try:
        notif = Path('GOV/jarvis/approval_notifications.csv')
        with notif.open('a', newline='', encoding='utf-8') as nf:
            nw = csv.writer(nf)
            nw.writerow([ts, aid, args.manifest, args.actor, args.reason, exp, datetime.utcnow().isoformat()+'Z'])
    except Exception:
        pass
    print('approval_id', aid)
elif args.cmd == 'list':
    with APPROVALS.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            print(row)
elif args.cmd == 'revoke':
    rows = []
    with APPROVALS.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(row)
    rows = [r for r in rows if r.get('approval_id') != args.id]
    with APPROVALS.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['approval_id','timestamp','manifest','actor','reason','expires_at'])
        for r in rows:
            w.writerow([r.get('approval_id'), r.get('timestamp'), r.get('manifest'), r.get('actor'), r.get('reason'), r.get('expires_at')])
    print('revoked', args.id)
else:
    p.print_help()