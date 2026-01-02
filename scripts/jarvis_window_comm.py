"""Simple inter-window communication helper for JARVIS.

Usage:
  python scripts/jarvis_window_comm.py aggregate   # aggregate recent progress/preflight/postflight/chat into a single JSON
  python scripts/jarvis_window_comm.py add --session <session_id> --author <author> --note "text"  # add a local note
  python scripts/jarvis_window_comm.py list [--limit N]  # list recent notes

Writes:
  - WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/window_comm_<ts>.json (aggregate)
  - WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/window_comm_log.csv (append notes)

"""
import argparse
import json
from pathlib import Path
from datetime import datetime
import csv

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'PROGRESS'
CHAT_RECENT = ROOT / 'WORK' / 'CHAT' / 'RECENT' / 'RECENT_CHAT_HISTORY.jsonl'
LOG_CSV = PROGRESS / 'window_comm_log.csv'


def iso_now():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def aggregate():
    out = {'generated_at': iso_now(), 'progress_files': [], 'recent_chat': []}
    # collect progress-related JSON files
    for p in sorted(PROGRESS.glob('*.json')):
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            out['progress_files'].append({'path': str(p.name), 'data': data})
        except Exception as e:
            out['progress_files'].append({'path': str(p.name), 'error': str(e)})
    # tail recent chat
    if CHAT_RECENT.exists():
        try:
            with CHAT_RECENT.open('r', encoding='utf-8') as fh:
                lines = fh.readlines()[-200:]
                out['recent_chat'] = [json.loads(l) for l in lines]
        except Exception as e:
            out['recent_chat'] = {'error': str(e)}
    # compute overall progress percent if available
    try:
        prog = subprocess.run(['python','scripts/compute_overall_progress.py'], capture_output=True, text=True)
        if prog.returncode == 0 and prog.stdout:
            out['overall_progress'] = json.loads(prog.stdout)
    except Exception:
        out['overall_progress'] = {'error': 'failed to compute'}
    # write aggregate
    out_path = PROGRESS / f'window_comm_{iso_now()}.json'
    out_path.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(str(out_path))


def delegate(task_id=None, file=None, window=None, owner='jarvis', rolecard='rc-default', priority='high'):
    """Delegate a task or file to a window. If task_id provided, attempt to resolve file target in manifest."""
    if not window:
        print('window required')
        return 2
    if task_id and not file:
        # try to find target file from manifest tasks
        MANIFEST = Path('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
        if MANIFEST.exists():
            m = json.loads(MANIFEST.read_text(encoding='utf-8'))
            for t in m.get('tasks', []):
                if t.get('id') == task_id and t.get('target_file'):
                    file = t.get('target_file')
                    break
    if not file:
        print('file not provided and could not be resolved from task_id')
        return 2
    # call assign_task_to_window
    cmd = ['python','scripts/assign_task_to_window.py','--file',str(file),'--window',str(window),'--owner',owner,'--rolecard',rolecard,'--priority',priority]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print('delegate failed:', res.stderr)
        return res.returncode
    # record a note in the window_comm_log
    add_note(window, owner, f'delegate: task from {file} -> {window}; via delegate command')
    # refresh task inventory
    subprocess.run(['python','scripts/generate_task_inventory.py'], check=False)
    print(res.stdout.strip())
    return 0


def add_note(session, author, note):
    now = datetime.utcnow().isoformat() + 'Z'
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    exists = LOG_CSV.exists()
    with LOG_CSV.open('a', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        if not exists:
            w.writerow(['timestamp', 'session_id', 'author', 'note'])
        w.writerow([now, session or '', author or '', note or ''])
    print(f'WROTE_NOTE {now}')


def list_notes(limit=50):
    if not LOG_CSV.exists():
        print('No notes found')
        return
    with LOG_CSV.open('r', encoding='utf-8') as fh:
        rows = list(csv.reader(fh))
    hdr = rows[0] if rows else []
    for r in rows[-limit:]:
        print('|'.join(r))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('aggregate')
    add = sub.add_parser('add')
    add.add_argument('--session', default='')
    add.add_argument('--author', default='')
    add.add_argument('--note', required=True)
    lst = sub.add_parser('list')
    lst.add_argument('--limit', type=int, default=50)
    # delegate command: assign a file or task to a window
    dlg = sub.add_parser('delegate')
    dlg.add_argument('--task', help='Task ID (T-XXX)')
    dlg.add_argument('--file', help='Source file to assign')
    dlg.add_argument('--window', required=True, help='Window id to delegate to')
    dlg.add_argument('--owner', default='jarvis')
    dlg.add_argument('--rolecard', default='rc-default')
    dlg.add_argument('--priority', default='high')
    args = p.parse_args()
    if args.cmd == 'aggregate':
        aggregate()
    elif args.cmd == 'add':
        add_note(args.session, args.author, args.note)
    elif args.cmd == 'list':
        list_notes(args.limit)
    elif args.cmd == 'delegate':
        rc = delegate(task_id=args.task, file=args.file, window=args.window, owner=args.owner, rolecard=args.rolecard, priority=args.priority)
        raise SystemExit(rc)
    else:
        p.print_help()
