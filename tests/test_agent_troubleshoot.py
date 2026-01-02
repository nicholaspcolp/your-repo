import json
from pathlib import Path
from scripts.agent_troubleshoot_github import mask_token, write_log, LOG_DIR


def test_mask_token():
    assert mask_token('ghp_abcdefghijk') == 'ghp_abcd...'
    assert mask_token('short') == '***'


def test_write_log(tmp_path):
    payload = {'checked_at': '2026-01-02T00:00:00Z', 'test': True}
    # write a log and assert it appears in the log dir
    write_log(payload)
    files = sorted(LOG_DIR.glob('troubleshoot_*.json'))
    assert files, 'No troubleshoot logs found'
    # read the latest and confirm content
    latest = files[-1]
    data = json.loads(latest.read_text(encoding='utf-8'))
    assert data.get('test') is True
