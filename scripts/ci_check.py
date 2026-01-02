#!/usr/bin/env python3
"""Simple CI/lint to enforce manifest output formats and docs/runtime separation.

Checks performed:
- No Markdown files under WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/ or WINDOW_MANIFESTS/
- The manifest's `manifest_instructions.output_formats` must reference an existing file under PROPOSED/JARVIS/
- Reports violations and exits non-zero if any found.
"""
import sys
from pathlib import Path
import json

ROOT = Path.cwd()
WORK_OPS = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS'
PROGRESS = WORK_OPS / 'PROGRESS'
WINDOW_MANIFESTS = WORK_OPS / 'WINDOW_MANIFESTS'
TRIAL_MANIFEST = WORK_OPS / 'TRIAL_MANIFEST.json'

errors = []


def check_md_in_runtime():
    for d in (PROGRESS, WINDOW_MANIFESTS):
        if not d.exists():
            continue
        for p in d.rglob('*.md'):
            errors.append(f'Markdown file in runtime folder: {p.relative_to(ROOT)}')


def check_manifest_output_ref():
    if not TRIAL_MANIFEST.exists():
        errors.append('TRIAL_MANIFEST.json missing')
        return
    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))
    instr = manifest.get('manifest_instructions', {})
    outref = instr.get('output_formats')
    if not outref:
        errors.append('manifest_instructions.output_formats not set')
        return
    outpath = ROOT / outref
    if not outpath.exists():
        errors.append(f'output_formats file referenced by manifest not found: {outref}')
    else:
        # ensure it's under PROPOSED/JARVIS
        try:
            rel = outpath.relative_to(ROOT / 'PROPOSED' / 'JARVIS')
        except Exception:
            errors.append(f'output_formats file must live under PROPOSED/JARVIS/: {outref}')


def check_manifest_required_fields():
    if not TRIAL_MANIFEST.exists():
        errors.append('TRIAL_MANIFEST.json missing')
        return
    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8'))
    # required top-level fields
    required_toplevel = ['manifest_version', 'tasks', 'mandatory_procedures', 'save_locations']
    for f in required_toplevel:
        if f not in manifest:
            errors.append(f'manifest missing top-level field: {f}')

    # verify task_tracker required fields presence for each task
    tracker_required = manifest.get('task_tracker', {}).get('required_fields', [])
    for t in manifest.get('tasks', []):
        for rf in tracker_required:
            if rf not in t:
                errors.append(f"task {t.get('id')} missing required tracker field: {rf}")


def check_progress_percent_enforcement():
    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8')) if TRIAL_MANIFEST.exists() else {}
    enforce = manifest.get('enforce_percent_in_user_messages', False)
    PROGRESS = WORK_OPS / 'PROGRESS'
    if not enforce:
        return
    if not PROGRESS.exists():
        return
    for p in PROGRESS.glob('*.json'):
        try:
            obj = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        # consider postflight or progress entries
        marker = obj.get('marker') or obj.get('status')
        if marker and (marker == 'postflight' or marker == 'progress' or marker == 'in-progress'):
            # check percent in either top-level or user_return
            if 'percent_complete' in obj:
                continue
            ur = obj.get('user_return')
            if ur and isinstance(ur, dict) and 'percent_complete' in ur:
                continue
            errors.append(f'Progress/postflight marker missing percent in {p.relative_to(ROOT)}')


def check_window_manifests():
    WM = WORK_OPS / 'WINDOW_MANIFESTS'
    if not WM.exists():
        return
    for p in WM.glob('*.json'):
        try:
            wm = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            errors.append(f'Invalid JSON in window manifest: {p.relative_to(ROOT)}')
            continue
        for key in ('manifest_ref', 'manifest_version', 'preferred_save_locations'):
            if key not in wm:
                errors.append(f'Window manifest {p.name} missing {key}')
        # tasks should include id and last_updated
        for t in wm.get('tasks', []):
            if 'id' not in t or 'last_updated' not in t:
                errors.append(f'Window manifest {p.name} has task missing id/last_updated: {t}')


def check_self_evals_for_completed_tasks():
    manifest = json.loads(TRIAL_MANIFEST.read_text(encoding='utf-8')) if TRIAL_MANIFEST.exists() else {}
    storage = manifest.get('self_evaluations', {}).get('storage')
    if not storage:
        return
    storage_path = ROOT.joinpath(storage)
    for t in manifest.get('tasks', []):
        if t.get('status') == 'completed':
            tid = t.get('id')
            # look for any self eval file containing task_id
            found = False
            if storage_path.exists():
                for p in storage_path.glob('*.json'):
                    try:
                        s = json.loads(p.read_text(encoding='utf-8'))
                    except Exception:
                        continue
                    if s.get('task_id') == tid:
                        found = True
                        break
            if not found:
                errors.append(f'Completed task {tid} missing self-evaluation in {storage}')


def main():
    check_md_in_runtime()
    check_manifest_output_ref()
    check_manifest_required_fields()
    check_progress_percent_enforcement()
    check_window_manifests()
    check_self_evals_for_completed_tasks()
    if errors:
        print('CI_CHECK: violations found:')
        for e in errors:
            print(' -', e)
        sys.exit(2)
    print('CI_CHECK: ok')


if __name__ == '__main__':
    main()
