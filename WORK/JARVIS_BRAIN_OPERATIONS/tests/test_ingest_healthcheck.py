from pathlib import Path
from scripts.ingest_healthcheck import read_heartbeat, get_queue_depth, PROG
import json, datetime


def test_read_heartbeat(tmp_path):
    hb = {'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status':'ok', 'queue_depth':0}
    p = tmp_path / 'background_ingest_heartbeat.json'
    p.write_text(json.dumps(hb), encoding='utf-8')
    data = read_heartbeat(p)
    assert data['status'] == 'ok'


def test_get_queue_depth(tmp_path):
    # create a temporary db and ensure function returns an integer
    db = tmp_path / 'queue.db'
    from scripts.queue_db import enqueue
    assert enqueue(str(db), str(tmp_path / 'a.json'))
    d = get_queue_depth(str(db))
    assert isinstance(d, int)
