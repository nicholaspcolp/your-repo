#!/usr/bin/env python3
"""Simple scheduler to run the agent troubleshoot script on an interval.
Usage:
  python scripts/troubleshoot_runner.py --once
  python scripts/troubleshoot_runner.py --interval-minutes 60
"""
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path('GOV/reports/jarvis_trials')
LOG_DIR.mkdir(parents=True, exist_ok=True)


def now_ts():
    return datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def run_once(repo=None, head=None):
    cmd = ['python', 'scripts/agent_troubleshoot_github.py']
    if repo:
        cmd += ['--repo', repo]
    if head:
        cmd += ['--head', head]
    # always run and capture output
    start = now_ts()
    try:
        r = subprocess.run(cmd, check=False, capture_output=True, text=True)
        out = {'started_at': start, 'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
    except Exception as e:
        out = {'started_at': start, 'error': str(e)}
    path = LOG_DIR / f'runner_{now_ts()}.json'
    import json
    path.write_text(json.dumps(out))
    print('Wrote runner log:', path)
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--interval-minutes', type=int, default=60)
    p.add_argument('--once', action='store_true')
    p.add_argument('--repo', default='nicholaspcolp/your-repo')
    p.add_argument('--head', default='trial-manifest-pr')
    args = p.parse_args()

    if args.once:
        run_once(repo=args.repo, head=args.head)
        return

    print('Starting scheduled runner, interval (min):', args.interval_minutes)
    while True:
        run_once(repo=args.repo, head=args.head)
        time.sleep(args.interval_minutes * 60)


if __name__ == '__main__':
    main()
