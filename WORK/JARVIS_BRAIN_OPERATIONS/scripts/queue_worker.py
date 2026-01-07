#!/usr/bin/env python3
"""queue_worker.py
Drain the ingest queue and process chat exports by normalizing them into canonical chats.
"""
import argparse, time, json, datetime
from pathlib import Path
from scripts.queue_db import claim_next, mark_done, get_conn
from scripts.canonical_chat_ingest import normalize_chat, persist_canonical, register_in_index       

ROOT = Path(__file__).resolve().parents[1]
PROG = ROOT / 'PROGRESS'
PROG.mkdir(parents=True, exist_ok=True)

# Maximum attempts before marking an item as error and creating an ingest_issue
MAX_ATTEMPTS = 5

def write_ingest_issue(error: str, qid: int, path: str, details: dict = None):
    payload = {
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'qid': qid,
        'path': path,
        'error': str(error),
        'details': details or {}
    }
    p = PROG / f'ingest_issue_{payload["ts"].replace(":","-").replace("+","-")}.json'
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return p


def process_one(db):
    item = claim_next(db)
    if not item:
        return None
    qid = item['id']
    path = item['path']
    # get current attempt count from DB (claim_next increments it)
    try:
        conn = get_conn(db)
        cur = conn.cursor()
        attempts = cur.execute('SELECT attempt_count FROM queue WHERE id = ?', (qid,)).fetchone()[0]
    except Exception:
        attempts = 0

    # If attempts already exceed or reach MAX_ATTEMPTS, mark as error and record issue
    if attempts and attempts >= MAX_ATTEMPTS:
        mark_done(db, qid, status='error')
        p = write_ingest_issue('max_attempts_exceeded', qid, path, {'attempts': attempts})
        return {'id': qid, 'path': path, 'status': 'error', 'reason': 'max_attempts_exceeded', 'issue': str(p)}

    try:
        doc = json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception as e:
        # transient read error: retry unless attempts exceeded
        if attempts >= MAX_ATTEMPTS:
            mark_done(db, qid, status='error')
            p = write_ingest_issue(str(e), qid, path, {'attempts': attempts})
            return {'id': qid, 'path': path, 'status': 'error', 'error': str(e), 'issue': str(p)}
        else:
            # revert to pending for retry
            mark_done(db, qid, status='pending')
            return {'id': qid, 'path': path, 'status': 'retry', 'error': str(e), 'attempts': attempts}

    try:
        canon = normalize_chat(doc, path)
        outp = persist_canonical(canon)
        register_in_index(outp)
        mark_done(db, qid, status='done')
        return {'id': qid, 'path': path, 'status': 'done', 'out': str(outp)}
    except Exception as e:
        # processing error, decide retry or error
        if attempts >= MAX_ATTEMPTS:
            mark_done(db, qid, status='error')
            p = write_ingest_issue(str(e), qid, path, {'attempts': attempts})
            return {'id': qid, 'path': path, 'status': 'error', 'error': str(e), 'issue': str(p)}
        else:
            mark_done(db, qid, status='pending')
            return {'id': qid, 'path': path, 'status': 'retry', 'error': str(e), 'attempts': attempts}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='WORK/queue.db')
    p.add_argument('--poll', type=float, default=1.0)
    p.add_argument('--run-once', action='store_true')
    args = p.parse_args()
    while True:
        r = process_one(args.db)
        if r is None:
            if args.run_once:
                break
            time.sleep(args.poll)
            continue
        print('Processed:', r)
        if args.run_once:
            break

if __name__ == '__main__':
    main()
