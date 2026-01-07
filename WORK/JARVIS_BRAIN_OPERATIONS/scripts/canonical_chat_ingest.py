#!/usr/bin/env python3
"""canonical_chat_ingest.py
Normalize a chat export (workspace/session) into a canonical chat entry and persist.
Writes out a canonical file in PROVENANCE and registers it in the EFMC-inprogress canonical_index.json.
"""
from pathlib import Path
import argparse, json, hashlib, datetime


def checksum(obj):
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(s).hexdigest()


def normalize_chat(doc, source_path):
    # doc may be any schema; try to extract messages and basic metadata
    meta = {}
    meta['source_path'] = str(source_path)
    meta['ingested_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta['id'] = doc.get('id') or doc.get('session_id') or f"chat_{checksum(doc)[:12]}"
    meta['window_id'] = doc.get('window_id') or doc.get('window') or doc.get('pane') or None
    meta['session_id'] = doc.get('session_id') or meta['id']
    # messages: unify list of {ts, role, text}
    msgs = []
    if isinstance(doc.get('messages'), list):
        for m in doc.get('messages'):
            msgs.append({'ts': m.get('ts') or m.get('timestamp'), 'role': m.get('role') or m.get('sender'), 'text': m.get('text') or m.get('content')})
    else:
        # try to detect simple forms
        if 'chat' in doc:
            for m in doc.get('chat', []):
                msgs.append({'ts': m.get('ts'), 'role': m.get('role'), 'text': m.get('text')})
    meta['messages_count'] = len(msgs)
    meta['messages_preview'] = [m['text'][:200] for m in msgs[:8]]
    meta['tags'] = doc.get('tags') or []
    body = {'meta': meta, 'messages': msgs}
    body['checksum'] = checksum(body)
    return body


def persist_canonical(canonical, dest_dir: str = 'PROVENANCE'):
    p = Path(dest_dir)
    p.mkdir(parents=True, exist_ok=True)
    fname = f"canonical_chat_{canonical['meta']['id']}.json"
    outp = p / fname
    outp.write_text(json.dumps(canonical, indent=2, ensure_ascii=False), encoding='utf-8')
    return outp


def register_in_index(path_to_canonical: Path):
    # register in EFMC-inprogress canonical_index.json
    cpath = Path(r'C:/Users/Tensh/PANDORASBOX/EFMC-inprogress-newdocs/canonical_index.json')
    try:
        idx = json.loads(cpath.read_text(encoding='utf-8')) if cpath.exists() else {'canonical_sessions': [], 'gov_docs': [], 'startup_manifest': {}}
    except Exception:
        idx = {'canonical_sessions': [], 'gov_docs': [], 'startup_manifest': {}}
    entry = {
        'id': path_to_canonical.stem,
        'title': f'canonical_chat ({path_to_canonical.name})',
        'path': str(path_to_canonical),
        'lastModified': path_to_canonical.stat().st_mtime,
        'note': 'auto-registered by canonical_chat_ingest'
    }
    idx.setdefault('canonical_sessions', []).insert(0, entry)
    cpath.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
    return cpath


def main():
    p = argparse.ArgumentParser()
    p.add_argument('path', help='Path to chat export JSON')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    path = Path(args.path)
    if not path.exists():
        raise SystemExit('not found')
    try:
        doc = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        raise
    canon = normalize_chat(doc, path)
    if args.dry_run:
        print('Would normalize:', canon['meta']['id'], 'msgs=', canon['meta']['messages_count'])
        return
    outp = persist_canonical(canon)
    register_in_index(outp)
    print('Wrote canonical chat to', outp)


if __name__ == '__main__':
    main()
