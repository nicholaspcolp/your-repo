"""File locker helper: records simple locks in GOV/jarvis/locks.csv to prevent concurrent edits.
Usage:
  python scripts/file_locker.py lock --file path/to/file --owner alice
  python scripts/file_locker.py unlock --file path/to/file --owner alice
  python scripts/file_locker.py status --file path/to/file
"""
import argparse
import csv
from pathlib import Path
from datetime import datetime

LOCKS = Path('GOV/jarvis/locks.csv')
if not LOCKS.parent.exists():
    LOCKS.parent.mkdir(parents=True, exist_ok=True)
if not LOCKS.exists():
    with LOCKS.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['file','owner','locked_at','note'])

p = argparse.ArgumentParser()
sp = p.add_subparsers(dest='cmd')

l = sp.add_parser('lock')
l.add_argument('--file', required=True)
l.add_argument('--owner', required=True)
l.add_argument('--note', default='')

u = sp.add_parser('unlock')
u.add_argument('--file', required=True)
u.add_argument('--owner', required=True)

s = sp.add_parser('status')
s.add_argument('--file', required=True)

args = p.parse_args()

def read():
    rows = []
    with LOCKS.open(newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def write(rows):
    with LOCKS.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['file','owner','locked_at','note'])
        for r in rows:
            w.writerow([r.get('file',''),r.get('owner',''),r.get('locked_at',''),r.get('note','')])

if args.cmd == 'lock':
    rows = read()
    for r in rows:
        if r['file']==args.file:
            print('already locked by', r['owner'])
            exit(1)
    rows.append({'file':args.file,'owner':args.owner,'locked_at':datetime.utcnow().isoformat()+'Z','note':args.note})
    write(rows)
    print('locked')
elif args.cmd == 'unlock':
    rows = read()
    rows = [r for r in rows if not (r['file']==args.file and r['owner']==args.owner)]
    write(rows)
    print('unlocked')
elif args.cmd == 'status':
    rows = read()
    for r in rows:
        if r['file']==args.file:
            print('locked by', r['owner'], 'since', r['locked_at'])
            break
    else:
        print('unlocked')
else:
    p.print_help()