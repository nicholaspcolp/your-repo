"""Scan recent chat for actionable user messages and convert them into draft tasks in priority CSV.

Usage:
  python scripts/chat_to_tasks.py --dry-run   # show proposed tasks
  python scripts/chat_to_tasks.py           # create tasks

New tasks are appended to WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv with id CHAT-<hex>
"""
import json
from pathlib import Path
import uuid
import csv
import argparse

ROOT = Path(__file__).resolve().parents[1]
CHAT_RECENT = ROOT / 'WORK' / 'CHAT' / 'RECENT' / 'RECENT_CHAT_HISTORY.jsonl'
PRIORITY_CSV = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'priority_tasks.csv'
KEYWORDS = ['please','please do','create','add','convert','assign','start','run','implement','align','ensure','confirm','proceed']


def load_existing_message_ids():
    if not PRIORITY_CSV.exists():
        return set()
    ids = set()
    with PRIORITY_CSV.open('r', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
        for r in rows:
            # check notes for a message_id marker
            if r.get('notes') and 'message_id:' in r['notes']:
                parts = r['notes'].split('message_id:')
                if len(parts) > 1:
                    ids.add(parts[1].strip())
    return ids


def is_actionable(msg):
    m = msg.lower()
    return any(k in m for k in KEYWORDS)


def propose_tasks(run_id=None, apply=False):
    if not CHAT_RECENT.exists():
        return []
    existing = load_existing_message_ids()
    proposals = []
    with CHAT_RECENT.open('r', encoding='utf-8') as fh:
        for line in fh:
            try:
                j = json.loads(line)
            except Exception:
                continue
            if j.get('sender') != 'user':
                continue
            msg = j.get('message','')
            mid = j.get('message_id','')
            if mid in existing:
                continue
            if is_actionable(msg):
                status = 'todo' if apply else 'proposed'
                notes = f"from_chat: true; message_id:{mid}; message: {msg}"
                if run_id:
                    notes += f"; proposed_by:{run_id}"
                prop = {'id': f'CHAT-{uuid.uuid4().hex[:8]}', 'title': msg[:120], 'owner': '', 'status': status,'priority':'medium','created_at':'', 'notes': notes, 'message_id': mid, 'estimated_percent': 0}
                proposals.append(prop)
    return proposals


def append_tasks(tasks):
    PRIORITY_CSV.parent.mkdir(parents=True, exist_ok=True)
    exists = PRIORITY_CSV.exists()
    fieldnames = ['id','title','owner','status','priority','created_at','updated_at','notes','assigned_session','message_id','estimated_percent','type']
    import datetime
    now = datetime.datetime.utcnow().isoformat()+'Z'
    with PRIORITY_CSV.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        for t in tasks:
            row = {fn: '' for fn in fieldnames}
            row.update(t)
            row['created_at'] = now
            row['updated_at'] = now
            row['type'] = 'task'
            w.writerow(row)
    return len(tasks)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--run-id', default=None)
    p.add_argument('--apply', action='store_true', help='Apply proposed tasks to priority CSV (requires manifest approval if gates present)')
    p.add_argument('--out-json', default=None, help='Write proposals JSON to given path')
    args = p.parse_args()
    proposals = propose_tasks(run_id=args.run_id, apply=args.apply)
    if not proposals:
        print('No actionable new user messages found')
    else:
        print('Proposed tasks:')
        for t in proposals:
            print('-', t['id'], t['title'])
        # write JSON proposals if requested
        if args.out_json:
            out = {
                'generated_at': __import__('datetime').datetime.utcnow().isoformat()+'Z',
                'run_id': args.run_id,
                'proposals_count': len(proposals),
                'proposals': proposals
            }
            Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out_json).write_text(json.dumps(out, indent=2), encoding='utf-8')
            print('Wrote proposals JSON to', args.out_json)
        if args.apply and not args.dry_run:
            # append tasks as active todos
            n = append_tasks(proposals)
            print(f'Appended {n} tasks to {PRIORITY_CSV}')
        else:
            print('Run with --apply to append proposed tasks (subject to manifest approval gates)')
