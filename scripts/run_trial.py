"""Run a guarded, non-destructive trial run according to the TRIAL manifest.
Behavior:
- Validate preconditions using `scripts/check_trial_preconditions.py`.
- Acquire a trial lock via `scripts/file_locker.py` on the manifest path.
- Write a preflight entry to WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl.
- Collect candidate tasks from manifest and write a dry-run report under GOV/reports/jarvis_trials/report_<run_id>.json.
- Release the trial lock and write a postflight entry.

Usage:
  python scripts/run_trial.py --manifest WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json
"""
import argparse
import datetime
import json
import subprocess
import uuid
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--manifest', default='WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
p.add_argument('--ops-root', default=r'C:\Users\Tensh\JARVISBRAINSURGERY(OPERATIONS GOVERNANCE TRIALS)')
p.add_argument('--dry-run', action='store_true', default=True)
args = p.parse_args()

manifest_path = Path(args.manifest)
if not manifest_path.exists():
    print('Manifest not found:', manifest_path)
    raise SystemExit(2)

run_id = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]

# 1) check preconditions
print('Checking preconditions...')
proc = subprocess.run(['python','scripts/check_trial_preconditions.py','--manifest',str(manifest_path),'--ops-root',args.ops_root], capture_output=True, text=True)
if proc.returncode != 0:
    # write diagnostics and defection for triage
    ts = datetime.datetime.utcnow().isoformat()+'Z'
    diag = {
        'run_id': run_id,
        'timestamp': ts,
        'manifest': str(manifest_path),
        'preflight_stdout': proc.stdout,
        'preflight_stderr': proc.stderr,
        'failing_checks': proc.stdout.splitlines(),
        'suggested_actions': ['Check manifest for required fields (defection_capture, artifact_paths)', 'Ensure operations root exists and approvals present']
    }
    outdir = Path('GOV/reports/jarvis_trials')
    outdir.mkdir(parents=True, exist_ok=True)
    diag_path = outdir / f'diagnostics_{run_id}.json'
    diag_path.write_text(json.dumps(diag, indent=2), encoding='utf-8')
    # record defection
    try:
        defs = Path('GOV/JARVIS/defections.csv')
        if not defs.exists():
            defs.write_text('timestamp,run_id,actor,summary,details,tags\n', encoding='utf-8')
        with defs.open('a', encoding='utf-8') as df:
            df.write(f"{ts},{run_id},script,preflight-failure,{proc.stdout.replace('\n',' | ')},preflight-fail\n")
    except Exception:
        pass
    # write preflight_fail to recent chat
    recent = Path('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
    recent.parent.mkdir(parents=True, exist_ok=True)
    pf_fail = {'timestamp':ts,'sender':'script','message':f'preflight_fail: run_id={run_id} reason={proc.stdout.strip().splitlines()[:3]}','run_id':run_id,'phase':'preflight_fail'}
    with recent.open('a', encoding='utf-8') as f:
        f.write(json.dumps(pf_fail)+"\n")
    print('Precondition check failed; aborting; diagnostics written to', diag_path)
    raise SystemExit(3)
print('Preconditions OK')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

# 2) acquire lock on the manifest to indicate a running trial
print('Acquiring trial lock...')
res = subprocess.run(['python','scripts/file_locker.py','lock','--file',str(manifest_path),'--owner',run_id,'--note','trial-run'])
if res.returncode != 0:
    print('Failed to acquire lock; aborting')
    raise SystemExit(4)
print('Lock acquired')

try:
    # aggregate inter-window communications and propose/apply chat-derived tasks
    print('Aggregating window communications...')
    agg = subprocess.run(['python','scripts/jarvis_window_comm.py','aggregate'], capture_output=True, text=True)
    if agg.returncode == 0:
        agg_path = agg.stdout.strip().splitlines()[-1] if agg.stdout else None
        print('Window communication aggregate created:', agg_path)

    # convert chat to tasks (propose if dry_run else append & refresh inventory)
    if manifest.get('dry_run'):
        print('Dry-run: proposing tasks from chat...')
        proposals = subprocess.run(['python','scripts/chat_to_tasks.py','--dry-run'], capture_output=True, text=True)
        proposals_out = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.txt'
        proposals_out.write_text(proposals.stdout or proposals.stderr or 'No proposals', encoding='utf-8')
        print('Proposals written to', proposals_out)
    else:
        # check approval gates before applying chat-derived tasks
        gov = {}
        try:
            gov = json.loads((Path('GOV/reports/manifest_governance_status.json')).read_text(encoding='utf-8'))
        except Exception:
            gov = {}
        approval_gates = manifest.get('approval_gates', [])
        need_approval = 'human_approval_before_manifest_change' in approval_gates
        approved = False
        if not need_approval:
            approved = True
        else:
            # look for an approval row that matches this manifest
            appr = Path('GOV/jarvis/manifest_approvals.csv')
            if appr.exists():
                import csv, datetime
                with appr.open(newline='', encoding='utf-8') as f:
                    for r in csv.DictReader(f):
                        if r.get('manifest') == str(manifest_path):
                            exp = r.get('expires_at')
                            try:
                                if exp and datetime.datetime.fromisoformat(exp.replace('Z','+00:00')) > datetime.datetime.utcnow():
                                    approved = True
                                    approval_id = r.get('approval_id')
                                    break
                            except Exception:
                                continue
        if not approved:
            # write proposals only and record a defection for missing approval
            print('Manifest requires approval and none found for this manifest; writing proposals only')
            # write both human-readable proposals and a machine-readable JSON proposals file
            proposals = subprocess.run(['python','scripts/chat_to_tasks.py','--dry-run','--run-id',run_id,'--out-json',str(Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.json')], capture_output=True, text=True)
            proposals_out = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.txt'
            proposals_out.write_text(proposals.stdout or proposals.stderr or 'No proposals', encoding='utf-8')
            # record defection noting missing approval
            defection_csv = Path('GOV/JARVIS/defections.csv')
            defection_csv.parent.mkdir(parents=True, exist_ok=True)
            if not defection_csv.exists():
                defection_csv.write_text('timestamp,run_id,actor,summary,details,tags\n', encoding='utf-8')
            ts = datetime.datetime.utcnow().isoformat()+'Z'
            with defection_csv.open('a', encoding='utf-8') as df:
                df.write(f"{ts},{run_id},script,missing-approval,manifest_change requires human approval,misc\n")
        else:
            print('Applying tasks from chat to priority CSV (approved)')
            subprocess.run(['python','scripts/chat_to_tasks.py','--run-id',run_id,'--apply'], check=False)
            print('Regenerating task inventory...')
            subprocess.run(['python','scripts/generate_task_inventory.py'], check=False)

    # 3) write preflight to recent chat history (include overall progress percent)
    recent = Path('WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl')
    recent.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat() + 'Z'
    # compute overall progress percent if available
    overall = {'percent_complete': None}
    try:
        cp = subprocess.run(['python','scripts/compute_overall_progress.py'], capture_output=True, text=True)
        if cp.returncode == 0 and cp.stdout:
            overall = json.loads(cp.stdout)
    except Exception:
        overall = {'percent_complete': None}
    percent_str = f" progress={overall.get('percent_complete',0)}%" if overall.get('percent_complete') is not None else ''
    preflight = {'timestamp':ts,'sender':'script','message':f'preflight: run_id={run_id} manifest={manifest_path}{percent_str}','run_id':run_id,'phase':'preflight','overall_progress':overall}
    with recent.open('a', encoding='utf-8') as f:
        f.write(json.dumps(preflight)+"\n")

    # 4) collect tasks
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    tasks = manifest.get('tasks', [])
    todo = [t for t in tasks if t.get('status') in ('todo','in-progress')]

    # 5) write a dry-run report
    outdir = Path('GOV/reports/jarvis_trials')
    outdir.mkdir(parents=True, exist_ok=True)
    # include governance status in report
    import subprocess, json
    gov_out = outdir.parent.parent / 'reports' / 'manifest_governance_status.json'
    # generate fresh governance status
    subprocess.run(['python','scripts/manifest_governance_status.py'], check=False)
    gov = {}
    try:
        gov = json.loads((Path('GOV/reports/manifest_governance_status.json')).read_text(encoding='utf-8'))
    except Exception:
        gov = {'error': 'failed to read governance status'}

    report = {
        'run_id': run_id,
        'manifest': str(manifest_path),
        'dry_run': args.dry_run,
        'tasks_count': len(todo),
        'tasks': todo,
        'governance': gov,
        'timestamp': ts,
        'preflight': 'ok'
    }
    outpath = outdir / f'report_{run_id}.json'
    outpath.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Dry-run report written to', outpath)

    # 6) write an entry to GOV/JARVIS/defections.csv if defection_capture true and none recorded
    if manifest.get('defection_capture'):
        # lightweight check: record a note that preflight observed
        defection_csv = Path('GOV/JARVIS/defections.csv')
        if defection_csv.exists():
            with defection_csv.open('a', newline='', encoding='utf-8') as f:
                f.write(f"{ts},{run_id},script,preflight-observed,manifest and preflight completed,automation-preflight\n")

    # 7) postflight summary in recent chat (include updated overall progress)
    overall = {'percent_complete': None}
    try:
        cp = subprocess.run(['python','scripts/compute_overall_progress.py'], capture_output=True, text=True)
        if cp.returncode == 0 and cp.stdout:
            overall = json.loads(cp.stdout)
    except Exception:
        overall = {'percent_complete': None}
    percent_str = f" progress={overall.get('percent_complete',0)}%" if overall.get('percent_complete') is not None else ''
    post = {'timestamp':datetime.datetime.utcnow().isoformat()+'Z','sender':'script','message':f'postflight: run_id={run_id} report={outpath}{percent_str}','run_id':run_id,'phase':'postflight','overall_progress':overall}
    with recent.open('a', encoding='utf-8') as f:
        f.write(json.dumps(post)+"\n")

finally:
    # release lock
    print('Releasing trial lock...')
    subprocess.run(['python','scripts/file_locker.py','unlock','--file',str(manifest_path),'--owner',run_id])

print('Run complete:', run_id)
