import os
from pathlib import Path
from scripts.troubleshoot_runner import run_once, LOG_DIR


def test_run_once_creates_runner_log(tmp_path, monkeypatch):
    # run once and assert a runner log exists
    p = run_once(repo='nicholaspcolp/your-repo', head='trial-manifest-pr')
    assert p.exists()
    data = p.read_text()
    assert 'started_at' in data


def test_parse_creates_followups(tmp_path):
    # create a fake troubleshoot log
    logdir = LOG_DIR
    logdir.mkdir(parents=True, exist_ok=True)
    sample = logdir / 'troubleshoot_test.json'
    sample.write_text('{"findings":[{"step":"token","status":"fail","text":"Bad credentials"}]}')
    # run parser
    from scripts.parse_troubleshoot_logs import parse_and_suggest
    outp = parse_and_suggest()
    assert outp and outp.exists()
    oj = outp.read_text()
    assert 'Rotate or fix PAT' in oj or 'suggestions' in oj
