"""Simple chat-recording CLI for JARVIS preliminary recording.
Usage:
  python scripts/jarvis_record.py start --task TASK_ID --actor USER
  python scripts/jarvis_record.py record --run RUN_ID --actor AGENT --message "..."
  python scripts/jarvis_record.py end --run RUN_ID --actor AGENT
  python scripts/jarvis_record.py status --run RUN_ID

Behavior:
- Messages are written to GOV/JARVIS/chats/<run_id>.jsonl (newline-delimited JSON).
- When ending a run, the script computes and writes a SHA256 sidecar (<run_id>.sha256) and records size/sha256 in the index.
- Messages are redacted using regex patterns in GOV/JARVIS/redact_patterns.txt (if present) before storage.
- Old runs are pruned when the number of chat files exceeds the retention limit (MAX_CHAT_KEEP).
"""
import argparse
import csv
import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
import uuid

BASE = Path('GOV/JARVIS')
CHATS = BASE / 'chats'
CHATS.mkdir(parents=True, exist_ok=True)
INDEX = BASE / 'chat_index.csv'
REDACT_PATTERNS = BASE / 'redact_patterns.txt'
MAX_CHAT_KEEP = 200  # prune older chat runs beyond this count


def load_redact_patterns():
    pats = []
    if REDACT_PATTERNS.exists():
        with REDACT_PATTERNS.open('r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith('#'):
                    pats.append(re.compile(s, re.IGNORECASE))
    return pats

REDACT_COMPILED = load_redact_patterns()

# Defection capture: small-format or meta-discussion items that do not fit normal task outputs
DEFECTS_CSV = BASE / 'defections.csv'
if not DEFECTS_CSV.exists():
    with DEFECTS_CSV.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['timestamp','run_id','actor','summary','details','tags'])


def record_defection(run_id, actor, summary, details='', tags=''):
    ts = datetime.utcnow().isoformat() + 'Z'
    with DEFECTS_CSV.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([ts, run_id or '', actor, summary, details, tags])
    # also write a chat message for audit if run_id provided
    if run_id:
        payload = {'run_id':run_id,'phase':'defection','timestamp':ts,'actor':actor,'message':f"DEFECT: {summary}", 'details': details, 'tags': tags}
        append_chat(run_id, payload)


def redact_text(text):
    if not REDACT_COMPILED or not isinstance(text, str):
        return text
    out = text
    for pat in REDACT_COMPILED:
        out = pat.sub('<REDACTED>', out)
    return out


def compute_file_sha(path, chunk_size=8*1024*1024):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                b = f.read(chunk_size)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return ''


def prune_old_runs(max_keep=MAX_CHAT_KEEP):
    files = sorted([p for p in CHATS.glob('*.jsonl')], key=lambda p: p.stat().st_mtime, reverse=True)
    if len(files) <= max_keep:
        return
    to_remove = files[max_keep:]
    for f in to_remove:
        try:
            f.unlink()
        except Exception:
            pass

p = argparse.ArgumentParser()
sp = p.add_subparsers(dest='cmd')

s = sp.add_parser('start')
s.add_argument('--task', required=True)
s.add_argument('--actor', default='user')

r = sp.add_parser('record')
r.add_argument('--run', required=True)
r.add_argument('--actor', required=True)
r.add_argument('--message', required=True)

# capture defection items (meta-discussion, format issues, small open queries)
d = sp.add_parser('defection')
d.add_argument('--run', default=None, help='Optional run id to associate')
d.add_argument('--actor', required=True, help='Who observed / reported the defection')
d.add_argument('--summary', required=True, help='Short summary/title for the defection')
d.add_argument('--details', default='', help='Optional longer details or notes')
d.add_argument('--tags', default='', help='Comma-separated tags, e.g., format,procedures,glossary')

e = sp.add_parser('end')
e.add_argument('--run', required=True)
e.add_argument('--actor', default='agent')

st = sp.add_parser('status')
st.add_argument('--run', required=True)

args = p.parse_args()

def write_index_row(run_id, task, start_ts=None, end_ts=None, size_bytes=None, sha256=None):
    header = ['run_id','task','start_timestamp','end_timestamp','size_bytes','sha256']
    if not INDEX.exists():
        with INDEX.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(header)
    # append or update
    rows = []
    with INDEX.open(newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    found=False
    for row in rows:
        if row['run_id']==run_id:
            if start_ts:
                row['start_timestamp']=start_ts
            if end_ts:
                row['end_timestamp']=end_ts
            if size_bytes is not None:
                row['size_bytes']=str(size_bytes)
            if sha256 is not None:
                row['sha256']=sha256
            found=True
    if not found:
        rows.append({'run_id':run_id,'task':task,'start_timestamp':start_ts or '','end_timestamp':end_ts or '','size_bytes':str(size_bytes or ''),'sha256':sha256 or ''})
    with INDEX.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow([row.get('run_id',''),row.get('task',''),row.get('start_timestamp',''),row.get('end_timestamp',''),row.get('size_bytes',''),row.get('sha256','')])


def append_chat(run_id, payload):
    # redact message content if present
    if 'message' in payload and isinstance(payload['message'], str):
        payload['message'] = redact_text(payload['message'])
    out = CHATS / f"{run_id}.jsonl"
    with out.open('a', encoding='utf-8') as f:
        f.write(json.dumps(payload, default=str)+"\n")

if args.cmd == 'start':
    run_id = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    ts = datetime.utcnow().isoformat()+'Z'
    payload = {'run_id':run_id,'phase':'start','timestamp':ts,'task':args.task,'actor':args.actor}
    append_chat(run_id, payload)
    write_index_row(run_id, args.task, start_ts=ts)
    print(run_id)
elif args.cmd == 'record':
    ts = datetime.utcnow().isoformat()+'Z'
    payload = {'run_id':args.run,'phase':'record','timestamp':ts,'actor':args.actor,'message':args.message}
    append_chat(args.run, payload)
    print('recorded')
elif args.cmd == 'end':
    ts = datetime.utcnow().isoformat()+'Z'
    payload = {'run_id':args.run,'phase':'end','timestamp':ts,'actor':args.actor}
    append_chat(args.run, payload)
    # compute file integrity and size
    chatfile = CHATS / f"{args.run}.jsonl"
    size = None
    sha = None
    if chatfile.exists():
        try:
            size = chatfile.stat().st_size
            sha = compute_file_sha(chatfile)
            # write sidecar sha file
            try:
                (CHATS / f"{args.run}.sha256").write_text(sha, encoding='utf-8')
            except Exception:
                pass
        except Exception:
            pass
    # update index
    write_index_row(args.run, task='', end_ts=ts, size_bytes=size, sha256=sha)
    # prune old chat files beyond retention
    prune_old_runs()
    print('ended')

elif args.cmd == 'defection':
    # record a defection; optionally attach to a run
    run_id = args.run
    record_defection(run_id, args.actor, args.summary, args.details, args.tags)
    print('defection recorded')
elif args.cmd == 'status':
    idx = INDEX
    if not idx.exists():
        print('no index')
    else:
        with idx.open(newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['run_id']==args.run:
                    print(json.dumps(row))
                    break
    
else:
    p.print_help()
