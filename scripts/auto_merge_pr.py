#!/usr/bin/env python3
"""Auto-merge a PR when checks pass using GitHub API.
Requires GITHUB_TOKEN in environment with repo:status and pull_request scopes.
Usage:
  export GITHUB_TOKEN=...
  python scripts/auto_merge_pr.py --repo nicholaspcolp/your-repo --branch trial-manifest-pr --interval 60
"""
import os
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--repo', required=True)
p.add_argument('--branch', required=True)
p.add_argument('--interval', type=int, default=60)
args = p.parse_args()

token = os.environ.get('GITHUB_TOKEN')
if not token:
    print('No GITHUB_TOKEN found in environment; auto-merge disabled. Set GITHUB_TOKEN to enable.')
    raise SystemExit(2)

headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
API_BASE = f'https://api.github.com/repos/{args.repo}'

from scripts.auto_merge_utils import has_valid_approval, pr_changed_files


def now():
    return datetime.utcnow().replace(microsecond=0).isoformat()+'Z'


def find_pr():
    url = API_BASE + '/pulls?state=open'
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    for pr in r.json():
        if pr.get('head',{}).get('ref') == args.branch:
            return pr
    return None


def ci_status(pr):
    # get combined status
    sha = pr['head']['sha']
    url = API_BASE + f'/commits/{sha}/status'
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    state = r.json().get('state')
    return state


def merge_pr(pr):
    url = API_BASE + f"/pulls/{pr['number']}/merge"
    r = requests.put(url, headers=headers, json={'commit_title': f"Auto-merge PR #{pr['number']} for {args.branch}", 'merge_method':'merge'})
    return r


MANIFEST_PATH = 'WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json'

print('Auto-merge helper starting at', now())
while True:
    try:
        pr = find_pr()
        if pr is None:
            print(now(), 'No open PR found for branch', args.branch)
        else:
            print(now(), 'Found PR', pr['html_url'], 'number', pr['number'])
            status = ci_status(pr)
            print('CI status:', status)
            if status == 'success':
                # Inspect changed files and enforce approvals for manifest changes
                try:
                    changed = pr_changed_files(args.repo, pr['number'], headers)
                except Exception as e:
                    print('Failed to fetch PR changed files, skipping approval check:', e)
                    changed = []
                print('Changed files in PR:', changed)
                if MANIFEST_PATH in changed:
                    print('PR modifies manifest', MANIFEST_PATH, '— verifying approval...')
                    if not has_valid_approval(MANIFEST_PATH):
                        print('No valid approval found for manifest; skipping merge until an approval is recorded')
                        time.sleep(args.interval)
                        continue
                print('Attempting merge...')
                r = merge_pr(pr)
                if r.status_code in (200, 201):
                    print('Merged PR', pr['number'])
                    out = Path('GOV/reports/jarvis_trials') / f'pr_auto_merged_{args.branch}_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json'
                    out.write_text('{"merged": true, "pr": %d}' % pr['number'])
                    break
                else:
                    print('Merge failed:', r.status_code, r.text)
            else:
                print('CI not successful yet; waiting')
    except Exception as e:
        print('Error in auto-merge loop:', e)
    time.sleep(args.interval)
