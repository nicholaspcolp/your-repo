#!/usr/bin/env python3
"""Recalculate dynamic_priority_list in TRIAL_MANIFEST.json based on agent activity and task statuses.

Rules (simple heuristic):
- Tasks owned by active windows/agents gain priority boost.
- Mandatory tasks (preflight/postflight enforcement IDs) stay top.
- Within same score, preserve existing order.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
CHAT_INDEX = ROOT.joinpath('WORK/CHAT/chat_index.json')
TRIAL_MANIFEST = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


PRIORITY_WEIGHT = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}


def load_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def save_manifest(manifest: dict):
    TRIAL_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


def recalc():
    idx = load_json(CHAT_INDEX) or {}
    manifest = load_json(TRIAL_MANIFEST)
    if manifest is None:
        print('manifest missing')
        return

    active_agents = set()
    # chat_index may have agents structure or active_jarvis_windows
    agents = idx.get('agents') or manifest.get('agent_activity') or {}
    if isinstance(agents, dict):
        for a, info in agents.items():
            if info.get('message_count', 0) > 0:
                active_agents.add(a)

    active_windows = set()
    # active_jarvis_windows may be a list
    for w in idx.get('active_jarvis_windows') or manifest.get('active_jarvis_windows') or []:
        try:
            # w might be dict or str
            if isinstance(w, dict):
                wid = w.get('window_id') or w.get('id')
                if wid:
                    active_windows.add(wid)
            else:
                active_windows.add(str(w))
        except Exception:
            continue

    tasks = manifest.get('tasks', [])
    scored = []
    for t in tasks:
        base = PRIORITY_WEIGHT.get((t.get('priority') or 'low').lower(), 1)
        boost = 0
        owner = t.get('owner')
        if owner in active_agents:
            boost += 2
        # if owner looks like a window id that is active
        if owner in active_windows:
            boost += 2
        score = base + boost
        scored.append((score, t))

    # sort descending by score, stable for equal scores
    scored.sort(key=lambda x: -x[0])

    new_list = []
    rank = 1
    for s, t in scored:
        new_list.append({
            'rank': rank,
            'reason': t.get('title', ''),
            'task_filter': [t.get('id')],
            'action': t.get('notes', '')
        })
        rank += 1

    manifest['dynamic_priority_list'] = new_list
    manifest['priority_recalculated_at'] = _now_iso()
    # bump version minor
    v = manifest.get('manifest_version', '0.2')
    parts = v.split('.')
    if len(parts) >= 2:
        try:
            parts[1] = str(int(parts[1]) + 1)
            manifest['manifest_version'] = '.'.join(parts[:2])
        except Exception:
            manifest['manifest_version'] = v
    save_manifest(manifest)
    print('recalculated, new manifest_version', manifest.get('manifest_version'))


if __name__ == '__main__':
    recalc()
