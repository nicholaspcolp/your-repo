"""Simple CLI to manage priority tasks in WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv
Usage:
  python scripts/priority_tasks.py add --title "Title" --owner assistant --priority high --notes "..."
  python scripts/priority_tasks.py list
  python scripts/priority_tasks.py set-status --id T-001 --status completed
"""
import argparse
import csv
from pathlib import Path
from datetime import datetime

PRIORITY_CSV = Path('WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv')

p = argparse.ArgumentParser()
sp = p.add_subparsers(dest='cmd')

add = sp.add_parser('add')
add.add_argument('--title', required=True)
add.add_argument('--owner', default='assistant')
add.add_argument('--priority', default='medium')
add.add_argument('--notes', default='')
add.add_argument('--assign-session', default='', help='Optional session_id to assign this task to a window')
add.add_argument('--type', default='task', choices=['task','documentation'], help='Type: task (work) or documentation (docs)')

listp = sp.add_parser('list')
listp.add_argument('--status', default=None)

setstat = sp.add_parser('set-status')
setstat.add_argument('--id', required=True)
setstat.add_argument('--status', required=True)

args = p.parse_args()

def read_rows():
    rows = []
    if PRIORITY_CSV.exists():
        with PRIORITY_CSV.open(newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)
    return rows


def write_rows(rows):
    with PRIORITY_CSV.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id','title','owner','status','priority','created_at','updated_at','notes','assigned_session','type'])
        for r in rows:
            w.writerow([r.get('id',''), r.get('title',''), r.get('owner',''), r.get('status',''), r.get('priority',''), r.get('created_at',''), r.get('updated_at',''), r.get('notes',''), r.get('assigned_session',''), r.get('type','task')])

if args.cmd == 'add':
    rows = read_rows()
    # generate id
    idx = len(rows) + 1
    tid = f'T-{idx:03d}'
    ts = datetime.utcnow().isoformat()+'Z'
    sess = args.assign_session or ''
    ttype = args.type or 'task'
    rows.append({'id':tid,'title':args.title,'owner':args.owner,'status':'todo','priority':args.priority,'created_at':ts,'updated_at':ts,'notes':args.notes,'assigned_session':sess,'type':ttype})
    write_rows(rows)
    print(f'Added {tid}')
elif args.cmd == 'list':
    rows = read_rows()
    if args.status:
        rows = [r for r in rows if r.get('status')==args.status]
    for r in rows:
        print(r['id'], r['title'], r['status'], r['priority'], r['owner'])
elif args.cmd == 'set-status':
    rows = read_rows()
    found = False
    for r in rows:
        if r.get('id')==args.id:
            r['status']=args.status
            r['updated_at']=datetime.utcnow().isoformat()+'Z'
            found = True
    write_rows(rows)
    if found:
        print('updated')
    else:
        print('not found')
else:
    p.print_help()