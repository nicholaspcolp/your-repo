"""
Builds and updates a chat index summarizing recent chat logs and summaries.
Produces `WORK/CHAT/chat_index.json` with per-agent last message id/timestamp,
summary counts, and active window/session counts for JARVIS agents.
"""
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta

ROOT = Path.cwd()
RECENT = ROOT.joinpath('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
SUMMARIES_DIR = ROOT.joinpath('WORK/CHAT/SUMMARIES')
INDEX_PATH = ROOT.joinpath('WORK/CHAT/chat_index.json')


def parse_iso(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        # fallback
        return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f%z')


def build_index(window_hours: int = 24) -> dict:
    index = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'agents': {},
        'summaries': {},
        'active_jarvis_windows': {
            'count': 0,
            'session_ids': []
        }
    }

    # Read recent chat history
    if RECENT.exists():
        with open(RECENT, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                sender = rec.get('sender') or 'unknown'
                msg_id = rec.get('message_id')
                ts = rec.get('timestamp')
                session_id = rec.get('session_id') or ''
                # update agent entry
                a = index['agents'].setdefault(sender, {
                    'last_message_id': None,
                    'last_timestamp': None,
                    'message_count': 0,
                    'session_ids': set()
                })
                a['last_message_id'] = msg_id
                a['last_timestamp'] = ts
                a['message_count'] = a.get('message_count', 0) + 1
                if session_id:
                    a['session_ids'].add(session_id)

    # finalize session id lists
    for k, v in index['agents'].items():
        v['session_ids'] = list(v['session_ids'])

    # Scan summaries
    if SUMMARIES_DIR.exists():
        files = sorted([p for p in SUMMARIES_DIR.iterdir() if p.name.startswith('summary_')])
        for p in files:
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
            except Exception:
                continue
            participants = data.get('participants', [])
            gen = data.get('generated_at')
            for agent in participants:
                s = index['summaries'].setdefault(agent, {'count': 0, 'last_summary': None, 'last_generated_at': None})
                s['count'] += 1
                s['last_summary'] = p.name
                s['last_generated_at'] = gen

    # Determine active jarvis windows based on RECENT session ids within window_hours
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    jarvis_sessions = set()
    if RECENT.exists():
        with open(RECENT, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get('sender') != 'jarvis':
                    continue
                ts = rec.get('timestamp')
                try:
                    t = parse_iso(ts)
                except Exception:
                    continue
                if t >= cutoff:
                    sid = rec.get('session_id') or f"session:{t.isoformat()}"
                    jarvis_sessions.add(sid)
    index['active_jarvis_windows']['count'] = len(jarvis_sessions)
    index['active_jarvis_windows']['session_ids'] = list(jarvis_sessions)

    # write index
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


if __name__ == '__main__':
    idx = build_index()
    print(json.dumps(idx, indent=2))
