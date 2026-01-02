"""Autonomous runner (dry-run by default) that orchestrates manifest indexing, chat extraction, governance check, metrics generation and report aggregation.
Usage: python scripts/autonomous_manifest_runner.py --dry-run
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

p = argparse = __import__('argparse').ArgumentParser()
p.add_argument('--dry-run', action='store_true', default=True)
p.add_argument('--manifest', default='WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
args = p.parse_args()

run_id = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + '-' + __import__('uuid').uuid4().hex[:8]
report = {'run_id': run_id, 'dry_run': args.dry_run, 'steps': [], 'timestamp': datetime.utcnow().isoformat()+'Z'}

# 1) index manifests
res = subprocess.run(['python','scripts/index_manifests.py'], capture_output=True, text=True)
report['steps'].append({'name':'index_manifests','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# 2) extract manifest chat summary
res = subprocess.run(['python','scripts/extract_manifest_chat_summary.py'], capture_output=True, text=True)
report['steps'].append({'name':'extract_manifest_chat_summary','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# 3) governance status
res = subprocess.run(['python','scripts/manifest_governance_status.py'], capture_output=True, text=True)
report['steps'].append({'name':'manifest_governance_status','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# 4) window activity
res = subprocess.run(['python','scripts/window_activity.py'], capture_output=True, text=True)
report['steps'].append({'name':'window_activity','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# 4.1) aggregate inter-window communication
res = subprocess.run(['python','scripts/jarvis_window_comm.py','aggregate'], capture_output=True, text=True)
report['steps'].append({'name':'jarvis_window_comm.aggregate','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# 4.2) propose or apply tasks from recent chat (respect dry-run)
if args.dry_run:
    res = subprocess.run(['python','scripts/chat_to_tasks.py','--dry-run','--run-id',run_id,'--out-json',str(Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.json')], capture_output=True, text=True)
    # write plain text proposals to PROGRESS for quick reading
    prop_path = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.txt'
    prop_path.parent.mkdir(parents=True, exist_ok=True)
    prop_path.write_text(res.stdout or res.stderr or 'No proposals', encoding='utf-8')
    report['steps'].append({'name':'chat_to_tasks.propose','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip(),'proposals_file_json':str(Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.json'),'proposals_file_txt':str(prop_path)})
else:
    # check approvals similar to run_trial
    try:
        gov = json.loads((Path('GOV/reports/manifest_governance_status.json')).read_text(encoding='utf-8'))
    except Exception:
        gov = {}
    manifest_path = args.manifest
    approval_gates = json.loads(Path(manifest_path).read_text(encoding='utf-8')).get('approval_gates', []) if Path(manifest_path).exists() else []
    need_approval = 'human_approval_before_manifest_change' in approval_gates
    approved = False
    if not need_approval:
        approved = True
    else:
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
                                break
                        except Exception:
                            continue
    if not approved:
        # write proposals and note lack of approval
        res = subprocess.run(['python','scripts/chat_to_tasks.py','--dry-run','--run-id',run_id], capture_output=True, text=True)
        prop_path = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS') / f'task_proposals_{run_id}.txt'
        prop_path.write_text(res.stdout or res.stderr or 'No proposals', encoding='utf-8')
        report['steps'].append({'name':'chat_to_tasks.propose','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip(),'proposals_file':str(prop_path),'note':'approval_missing'})
    else:
        res = subprocess.run(['python','scripts/chat_to_tasks.py','--run-id',run_id,'--apply'], capture_output=True, text=True)
        gen = subprocess.run(['python','scripts/generate_task_inventory.py'], capture_output=True, text=True)
        report['steps'].append({'name':'chat_to_tasks.apply','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})
        report['steps'].append({'name':'generate_task_inventory','rc':gen.returncode,'stdout':gen.stdout.strip(),'stderr':gen.stderr.strip()})

# 5) generate metrics
res = subprocess.run(['python','scripts/generate_manifest_stats.py'], capture_output=True, text=True)
report['steps'].append({'name':'generate_manifest_stats','rc':res.returncode,'stdout':res.stdout.strip(),'stderr':res.stderr.strip()})

# write aggregate report
out = Path('GOV/reports/jarvis_trials')
out.mkdir(parents=True, exist_ok=True)
outfile = out / f'autonomous_manifest_run_report_{run_id}.json'
outfile.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Wrote autonomous run report to', outfile)
