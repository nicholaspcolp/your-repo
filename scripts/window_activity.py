"""Compute active agent windows (sessions) from recent chat history.
Writes `GOV/reports/active_windows.json` and prints a short list to stdout.
Usage: python scripts/window_activity.py --recent WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl --out GOV/reports/active_windows.json --window-minutes 30
"""
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

p = argparse.ArgumentParser()
p.add_argument('--recent', default='WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
p.add_argument('--out', default='GOV/reports/active_windows.json')
p.add_argument('--window-minutes', type=int, default=30)
args = p.parse_args()

recent = Path(args.recent)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
window_delta = timedelta(minutes=args.window_minutes)

sessions = {}
if recent.exists():
    with recent.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ts = obj.get('timestamp') or obj.get('created_at') or obj.get('time')
            sender = obj.get('sender') or obj.get('actor')
            session_id = obj.get('session_id') or obj.get('run_id') or obj.get('session')
            if not session_id:
                # construct session fingerprint by hour-sliced timestamp and sender
                session_id = f"session:{sender}:{ts}" if sender and ts else 'session:unknown'
            try:
                dt = datetime.fromisoformat(ts.replace('Z','+00:00'))
            except Exception:
                dt = None
            if session_id not in sessions:
                sessions[session_id] = {'last_timestamp': ts, 'last_dt': dt, 'message_count': 0, 'participants': set()}
            s = sessions[session_id]
            s['message_count'] = s.get('message_count',0) + 1
            if sender:
                s['participants'].add(sender)
            if dt and (s.get('last_dt') is None or dt > s.get('last_dt')):
                s['last_dt'] = dt
                s['last_timestamp'] = ts

# filter by activity window
from datetime import timezone
now = datetime.now(timezone.utc)
active = []
for sid, info in sessions.items():
    last_dt = info.get('last_dt')
    if last_dt:
        # ensure both are timezone-aware
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=datetime.timezone.utc)
        if (now - last_dt) <= window_delta:
            active.append({'session_id': sid, 'last_timestamp': info.get('last_timestamp'), 'message_count': info.get('message_count'), 'participants': sorted(list(info.get('participants')))})

out.write_text(json.dumps({'generated_at': now.isoformat()+'Z', 'window_minutes': args.window_minutes, 'active_sessions': active}, indent=2), encoding='utf-8')
print(f'Wrote active sessions ({len(active)}) to {out}')
for a in active:
    print(a['session_id'], a['last_timestamp'], a['message_count'], a['participants'])