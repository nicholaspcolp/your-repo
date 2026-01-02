import json
from pathlib import Path

PROGRESS_DIR = Path('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS')

REQUIRED_KEYS = ['generated_at','percent_complete','task_inventory','metrics','window_comm','provenance']


def test_progress_stats_exists():
    files = sorted(PROGRESS_DIR.glob('progress_stats_*.json'))
    assert files, 'No progress_stats_*.json files found in PROGRESS dir'


def test_progress_stats_schema():
    files = sorted(PROGRESS_DIR.glob('progress_stats_*.json'))
    assert files, 'No progress_stats_*.json files found in PROGRESS dir'
    latest = files[-1]
    data = json.loads(latest.read_text(encoding='utf-8'))
    for k in REQUIRED_KEYS:
        assert k in data, f'Missing key {k} in {latest}'
    # type checks
    assert isinstance(data['percent_complete'], (int, float)), 'percent_complete must be numeric'
    assert isinstance(data['task_inventory'], str), 'task_inventory must be a path string'
    assert isinstance(data['metrics'], str), 'metrics must be a path string'
    assert isinstance(data['window_comm'], str), 'window_comm must be a path string'
    prov = data['provenance']
    assert isinstance(prov, dict) and 'agent_id' in prov and 'timestamp' in prov, 'provenance must include agent_id and timestamp'