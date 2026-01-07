import json
from pathlib import Path
from scripts.summary_to_tasks import process_summary


def test_summary_to_tasks_append_csv(tmp_path):
    # create sample summary
    s = {'session_id':'s2','window_id':'W2','summary':{'actions':['Do A','Do B']}}
    p = tmp_path / 'sum.json'
    p.write_text(json.dumps(s), encoding='utf-8')

    csvp = Path('priority_tasks_m8_candidates.csv')
    # ensure test starts clean
    if csvp.exists():
        csvp.unlink()

    out = process_summary(p, append_to_csv=True)
    assert out.exists()

    # CSV should exist and contain two AUTO rows
    txt = csvp.read_text(encoding='utf-8')
    assert 'AUTO-s2-0' in txt
    assert 'AUTO-s2-1' in txt

    # clean up
    csvp.unlink()
