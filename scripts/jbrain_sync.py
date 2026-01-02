"""
Utilities to sync chat_index and summaries into the trial manifest and to write preflight/postflight markers.
"""
from pathlib import Path
import json
from datetime import datetime, timezone
import glob
import subprocess
import sys


ROOT = Path.cwd()
CHAT_RECENT = ROOT.joinpath('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
CHAT_INDEX = ROOT.joinpath('WORK/CHAT/chat_index.json')
TRIAL_MANIFEST = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
PROGRESS_DIR = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS')
WINDOW_MANIFESTS = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/WINDOW_MANIFESTS')
CHANGELOG = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/CHANGELOG.md')

PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
WINDOW_MANIFESTS.mkdir(parents=True, exist_ok=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def write_marker(kind: str, operation: str, agent: str = 'jarvis', session_id: str = '', details: dict = None):
    """Write a preflight or postflight marker into RECENT chat.
    kind: 'preflight'|'postflight'
    operation: textual operation id/name
    """
    rec = {
        'timestamp': _now_iso(),
        'sender': agent,
        'message': f'MARKER:{kind}:{operation}',
        'message_id': f'marker-{agent}-{_now_iso()}',
        'session_id': session_id,
        'metadata': {'marker': kind, 'operation': operation, 'details': details or {}}
    }
    with open(CHAT_RECENT, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return rec


def merge_index_into_manifest():
    """Read chat_index.json and update TRIAL_MANIFEST.json with latest agent activity."""
    if not CHAT_INDEX.exists() or not TRIAL_MANIFEST.exists():
        return None
    idx = json.loads(CHAT_INDEX.read_text(encoding='utf-8'))
    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))
    # annotate top-level
    manifest['last_indexed_at'] = idx.get('generated_at')
    manifest['agent_activity'] = idx.get('agents')
    manifest['active_jarvis_windows'] = idx.get('active_jarvis_windows')
    TRIAL_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def _parse_iso(ts: str):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f%z')
        except Exception:
            return None


def _bump_version_string(v: str) -> str:
    parts = v.split('.')
    if len(parts) == 1:
        return v + '.1'
    major = int(parts[0])
    minor = int(parts[1]) + 1
    return f"{major}.{minor}"


def _append_changelog_entry(new_version: str, summary: str, details: list):
    ts = _now_iso()
    entry = [f"## {new_version} - {ts}", f"- {summary}"]
    for d in details:
        entry.append(f"- {d}")
    entry_text = '\n'.join(entry) + '\n\n'
    with open(CHANGELOG, 'a', encoding='utf-8') as f:
        f.write(entry_text)


def merge_window_manifests():
    """Merge per-window manifests from WINDOW_MANIFESTS into TRIAL_MANIFEST.json.
    Conflict policy: newer `last_updated` wins; if same timestamp and conflicting owners, mark defection.
    """
    wm_files = list(WINDOW_MANIFESTS.glob('*.json'))
    if not wm_files or not TRIAL_MANIFEST.exists():
        return None

    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))
    existing_tasks = {t['id']: t for t in manifest.get('tasks', [])}
    changes = []

    for p in wm_files:
        try:
            wm = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        window_id = p.stem
        for t in wm.get('tasks', []):
            tid = t.get('id')
            if not tid:
                continue
            t_last = _parse_iso(t.get('last_updated'))
            if tid not in existing_tasks:
                manifest.setdefault('tasks', []).append(t)
                changes.append(f"added {tid} from {window_id}")
            else:
                ex = existing_tasks[tid]
                ex_last = _parse_iso(ex.get('last_updated'))
                if t_last and (not ex_last or t_last > ex_last):
                    # adopt newer fields
                    ex.update({k: v for k, v in t.items() if k != 'id'})
                    changes.append(f"updated {tid} from {window_id}")
                elif t_last and ex_last and t_last == ex_last and ex.get('owner') != t.get('owner'):
                    # defection: conflicting owners at same timestamp
                    ex.setdefault('defection_flag', True)
                    detail = f"defection on {tid}: owners {ex.get('owner')} vs {t.get('owner')} from {window_id}"
                    ex.setdefault('defection_details', detail)
                    changes.append(detail)

    if changes:
        # bump manifest_version
        cur_v = manifest.get('manifest_version', '0.1')
        new_v = _bump_version_string(cur_v)
        manifest['manifest_version'] = new_v
        manifest['last_merged_at'] = _now_iso()
        TRIAL_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        # append changelog entry
        _append_changelog_entry(new_v, 'Merged per-window manifests', changes)
        # write merge report
        report = {'merged_at': _now_iso(), 'changes': changes, 'merged_files': [str(p.name) for p in wm_files]}
        rep_path = PROGRESS_DIR.joinpath(f'merge_report_{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.json')
        rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        return manifest
    return None


def write_progress(task_id: str, owner: str, status: str, note: str):
    p = {
        'task_id': task_id,
        'owner': owner,
        'status': status,
        'note': note,
        'timestamp': _now_iso()
    }
    path = PROGRESS_DIR.joinpath(f'progress_{task_id}_{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.json')
    path.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding='utf-8')
    return p


if __name__ == '__main__':
    print('Merging index into manifest...')
    m = merge_index_into_manifest()
    print('Index merge done.' if m else 'Index or manifest missing.')
    print('Merging window manifests...')
    mm = merge_window_manifests()
    print('Window merge done.' if mm else 'No window manifests to merge or no changes.')
    # After merges, compute progress stats
    try:
        prog = str(Path.cwd().joinpath('scripts','progress_stats.py'))
        subprocess.run([sys.executable, prog], check=True)
        print('Progress stats computed.')
    except Exception:
        print('Progress stats computation failed or script missing.')
