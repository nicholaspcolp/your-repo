import os
from pathlib import Path
from datetime import datetime, timedelta
from scripts.auto_merge_utils import has_valid_approval

APPROVALS = Path('GOV/jarvis/manifest_approvals.csv')


def ensure_approvals_dir():
    if not APPROVALS.parent.exists():
        APPROVALS.parent.mkdir(parents=True, exist_ok=True)


def test_no_approvals_returns_false(tmp_path):
    if APPROVALS.exists():
        APPROVALS.unlink()
    assert not has_valid_approval('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')


def test_valid_future_approval(tmp_path):
    ensure_approvals_dir()
    # create an approvals file with a future expiry
    expires = (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z'
    with APPROVALS.open('w', newline='', encoding='utf-8') as f:
        f.write('approval_id,timestamp,manifest,actor,reason,expires_at\n')
        f.write(f'abc123,2026-01-02T00:00:00Z,WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json,alice,ok,{expires}\n')
    assert has_valid_approval('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')


def test_expired_approval_returns_false(tmp_path):
    ensure_approvals_dir()
    expires = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    with APPROVALS.open('w', newline='', encoding='utf-8') as f:
        f.write('approval_id,timestamp,manifest,actor,reason,expires_at\n')
        f.write(f'abc123,2026-01-02T00:00:00Z,WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json,alice,ok,{expires}\n')
    assert not has_valid_approval('WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json')
