from scripts.task_api import create_task_draft
from pathlib import Path


def test_create_task_draft():
    p = create_task_draft('Test task', 'Do something', owner='tensh', severity='low')
    assert p.exists()
    data = p.read_text()
    assert 'Test task' in data
