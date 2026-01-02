#!/usr/bin/env python3
"""Assign a focused single-source-file task to a JARVIS window.

Creates a task in TRIAL_MANIFEST.json (next numeric id), writes a preflight marker via `scripts/progress_writer.py`,
writes a per-window manifest snapshot, creates a simple lock entry, and triggers `scripts/jbrain_sync.py`.

Usage:
  python scripts/assign_task_to_window.py --file analyze_pdf_text.py --window win-2 --owner jarvis --priority high
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess


ROOT = Path.cwd()
TRIAL_MANIFEST = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'TRIAL_MANIFEST.json'
PROGRESS_WRITER = ROOT / 'scripts' / 'progress_writer.py'
WINDOW_MANIFESTS = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'WINDOW_MANIFESTS'
LOCKS_DIR = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'LOCKS'


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_manifest():
    if not TRIAL_MANIFEST.exists():
        return None
    return json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))


def save_manifest(m):
    TRIAL_MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')


def next_task_id(manifest):
    existing = manifest.get('tasks', [])
    nums = []
    for t in existing:
        tid = t.get('id', '')
        if tid.startswith('T-'):
            try:
                nums.append(int(tid.split('-')[1]))
            except Exception:
                continue
    n = max(nums) + 1 if nums else 1
    return f'T-{n:03d}'


def add_task_for_file(manifest, task_id, file_path, owner, priority, note):
    title = f'Work on source file {Path(file_path).name}'
    task = {
        'id': task_id,
        'title': title,
        'owner': owner,
        'status': 'in-progress',
        'priority': priority,
        'origin': 'assistant:assign_task_to_window',
        'last_updated': _now_iso(),
        'notes': note,
        'target_file': str(file_path)
    }
    manifest.setdefault('tasks', []).append(task)
    return task


def write_lock(file_path, owner, window_id):
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    lock = {
        'file': str(file_path),
        'owner': owner,
        'window_id': window_id,
        'locked_at': _now_iso()
    }
    p = LOCKS_DIR / (Path(file_path).name + '.lock.json')
    p.write_text(json.dumps(lock, ensure_ascii=False, indent=2), encoding='utf-8')
    return p


def run_progress_writer_python(mode, task_id, agent, rolecard, note, window=None):
    cmd = [sys.executable, str(PROGRESS_WRITER), '--task', task_id, '--agent', agent, '--rolecard', rolecard, '--mode', mode, '--note', note]
    if window:
        cmd += ['--window', window]
    subprocess.run(cmd, check=True)


def trigger_sync():
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'jbrain_sync.py')], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True)
    p.add_argument('--window', required=True)
    p.add_argument('--owner', default='jarvis')
    p.add_argument('--rolecard', default='rc-default')
    p.add_argument('--priority', default='high')
    args = p.parse_args()

    manifest = load_manifest()
    if manifest is None:
        print('Manifest missing')
        sys.exit(2)

    task_id = next_task_id(manifest)
    note = f'Assigned to {args.window} to work on {args.file}'
    task = add_task_for_file(manifest, task_id, args.file, args.owner, args.priority, note)
    save_manifest(manifest)
    # write preflight and window manifest snapshot via progress_writer
    run_progress_writer_python('preflight', task_id, args.owner, args.rolecard, f'preflight for {args.file}', window=args.window)
    # create lock
    lock_path = write_lock(args.file, args.owner, args.window)
    print('Lock created at', lock_path)
    # write post-window snapshot (progress_writer will create window manifest)
    run_progress_writer_python('progress', task_id, args.owner, args.rolecard, f'started work on {args.file}', window=args.window)
    # trigger sync
    trigger_sync()
    print('Assigned', task_id, 'to', args.window)


if __name__ == '__main__':
    main()
