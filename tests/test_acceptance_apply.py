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

    # backup the real manifest and set dry_run to false temporarily
    orig_manifest = MANIFEST.with_suffix('.orig')
    if MANIFEST.exists():
        shutil.copy(MANIFEST, orig_manifest)
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    m['dry_run'] = False
    MANIFEST.write_text(json.dumps(m, indent=2), encoding='utf-8')

    # backup priority CSV if present
    if PRIORITY.exists():
        bak = PRIORITY.with_suffix('.bak')
        shutil.copy(PRIORITY, bak)
    else:
        bak = None

    try:
        # create an approval for the real manifest
        res = subprocess.run(['python','scripts/manifest_approval.py','approve','--manifest',str(MANIFEST),'--actor','tester','--reason','acceptance-test','--ttl-hours','1'], capture_output=True, text=True)
        assert res.returncode == 0

        # directly apply proposals using chat_to_tasks (simulate runner apply)
        res = subprocess.run(['python','scripts/chat_to_tasks.py','--run-id','ACCEPTANCE','--apply'], capture_output=True, text=True)
        assert res.returncode == 0

        # verify proposals were appended to priority CSV
        assert PRIORITY.exists()
        content = PRIORITY.read_text(encoding='utf-8')
        assert 'from_chat: true' in content
        assert 'message_id:am-1' in content

    finally:
        # restore manifest
        if orig_manifest.exists():
            orig_manifest.replace(MANIFEST)
        # restore priority csv
        if bak:
            bak.replace(PRIORITY)
        else:
            try:
                PRIORITY.unlink()
            except Exception:
                pass
