"""Extract messages referencing 'manifest' or explicit manifest filenames from recent chats and per-run chats.
Writes WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/manifest_chat_summary_<ts>.json
"""
import json
from pathlib import Path
from datetime import datetime

RECENT = Path('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
JARVIS_CHATS = Path('GOV/JARVIS/chats')
OUTDIR = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS')
OUTDIR.mkdir(parents=True, exist_ok=True)

def matches_manifest(text):
    if not text:
        return False
    s = text.lower()
    if 'manifest' in s:
        return True
    # detect common manifest filenames
    if 'safe_exclude_move_manifest' in s or 'efmc' in s:
        return True
    return False

matches = []
if RECENT.exists():
    with RECENT.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if matches_manifest(obj.get('message') or obj.get('message','')):
                matches.append(obj)

# scan per-run jarvis chats
if JARVIS_CHATS.exists():
    for p in JARVIS_CHATS.glob('*.jsonl'):
        with p.open('r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if matches_manifest(obj.get('message') or ''):
                    matches.append(obj)

out = OUTDIR / f'manifest_chat_summary_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json'
out.write_text(json.dumps({'generated_at': datetime.utcnow().isoformat()+'Z', 'matches_count': len(matches), 'matches': matches}, indent=2), encoding='utf-8')
print('Wrote manifest chat summary to', out)