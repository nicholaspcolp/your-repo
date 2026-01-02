import json
import subprocess
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RECENT = ROOT / 'WORK' / 'CHAT' / 'RECENT' / 'RECENT_CHAT_HISTORY.jsonl'
PRIORITY = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'priority_tasks.csv'
MANIFEST = ROOT / 'WORK' / 'JARVIS_BRAIN_OPERATIONS' / 'TRIAL_MANIFEST.json'

sample = [
    {"timestamp": "2026-01-02T00:00:00Z", "sender": "user", "message": "Please convert defection to task: consolidate chat logs", "message_id": "am-1"},
]


def test_acceptance_apply(tmp_path):
    # prepare recent chat
    RECENT.parent.mkdir(parents=True, exist_ok=True)
    with RECENT.open('w', encoding='utf-8') as f:
        for s in sample:
            f.write(json.dumps(s) + "\n")

    # copy manifest and set dry_run to false
    tmp_manifest = tmp_path / 'TRIAL_MANIFEST.json'
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    m['dry_run'] = False
    tmp_manifest.write_text(json.dumps(m, indent=2), encoding='utf-8')

    # ensure no CHAT tasks with this message exist
    if PRIORITY.exists():
        # backup
        bak = PRIORITY.with_suffix('.bak')
        shutil.copy(PRIORITY, bak)
    else:
        bak = None

    # create an approval for this temp manifest
    res = subprocess.run(['python','scripts/manifest_approval.py','approve','--manifest',str(tmp_manifest),'--actor','tester','--reason','acceptance-test','--ttl-hours','1'], capture_output=True, text=True)
    assert res.returncode == 0

    # run non-dry-run trial pointing at tmp manifest
    res = subprocess.run(['python','scripts/run_trial.py','--manifest',str(tmp_manifest)], capture_output=True, text=True)
    assert res.returncode == 0

    # verify proposals were appended to priority CSV
    assert PRIORITY.exists()
    content = PRIORITY.read_text(encoding='utf-8')
    assert 'from_chat: true' in content
    assert 'message_id:am-1' in content

    # cleanup: restore priority csv
    if bak:
        bak.replace(PRIORITY)
    else:
        try:
            PRIORITY.unlink()
        except Exception:
            pass
