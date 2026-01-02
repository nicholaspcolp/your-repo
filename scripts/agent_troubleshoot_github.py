#!/usr/bin/env python3
"""Agent-guided troubleshooting for GitHub PAT, repo access, remotes, and PR creation.
Produces structured JSON logs in GOV/reports/jarvis_trials/troubleshoot_<ts>.json
"""
import os
import sys
import json
import argparse
import requests
import subprocess
from datetime import datetime
from pathlib import Path

LOG_DIR = Path('GOV/reports/jarvis_trials')
LOG_DIR.mkdir(parents=True, exist_ok=True)


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def mask_token(t):
    if not t:
        return None
    return t[:8] + '...' if len(t) > 8 else '***'


def write_log(payload):
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out = LOG_DIR / f'troubleshoot_{ts}.json'
    out.write_text(json.dumps(payload, indent=2))
    print('Wrote log:', out)


def check_token(headers):
    r = requests.get('https://api.github.com/user', headers=headers, timeout=30)
    return r


def check_repo_access(repo, headers):
    url = f'https://api.github.com/repos/{repo}'
    r = requests.get(url, headers=headers, timeout=30)
    return r


def check_remotes():
    try:
        out = subprocess.check_output(['git', 'remote', '-v'], stderr=subprocess.STDOUT, text=True)
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stderr=subprocess.STDOUT, text=True).strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'], stderr=subprocess.STDOUT, text=True)
        return {'remote': out.strip(), 'branch': branch, 'status': status.splitlines()}
    except subprocess.CalledProcessError as e:
        return {'error': str(e), 'output': getattr(e, 'output', None)}


def attempt_create_pr(repo, head, base, headers):
    # Use GitHub REST create PR endpoint directly
    url = f'https://api.github.com/repos/{repo}/pulls'
    payload = {'title': f'PR: {head} -> {base}', 'head': head, 'base': base, 'body': 'Automated PR via agent_troubleshoot_github'}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', default='nicholaspcolp/your-repo')
    p.add_argument('--head', default=None)
    p.add_argument('--base', default='master')
    p.add_argument('--attempt-pr', action='store_true')
    args = p.parse_args()

    token = os.environ.get('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}

    log = {'checked_at': now_iso(), 'repo': args.repo, 'head': args.head, 'base': args.base, 'findings': []}
    log['token_mask'] = mask_token(token)

    # Step 1: Token validation
    if not token:
        log['findings'].append({'step': 'token', 'status': 'missing', 'note': 'GITHUB_TOKEN not set in environment'})
        write_log(log)
        print('GITHUB_TOKEN not set')
        sys.exit(2)

    try:
        r = check_token(headers)
        if r.status_code == 200:
            log['findings'].append({'step': 'token', 'status': 'ok', 'user': r.json().get('login')})
        else:
            log['findings'].append({'step': 'token', 'status': 'fail', 'http_status': r.status_code, 'text': r.text})
            write_log(log)
            print('Token authentication failed:', r.status_code)
            sys.exit(3)
    except Exception as e:
        log['findings'].append({'step': 'token', 'status': 'error', 'error': str(e)})
        write_log(log)
        print('Token check error:', e)
        sys.exit(4)

    # Step 2: Repo access
    rr = check_repo_access(args.repo, headers)
    if rr.status_code == 200:
        pj = rr.json()
        log['findings'].append({'step': 'repo', 'status': 'ok', 'visibility': pj.get('private'), 'permissions': pj.get('permissions')})
    else:
        log['findings'].append({'step': 'repo', 'status': 'fail', 'http_status': rr.status_code, 'text': rr.text})
        write_log(log)
        print('Repo access check failed:', rr.status_code)
        sys.exit(5)

    # Step 3: Remotes & branch
    rem = check_remotes()
    log['findings'].append({'step': 'git', 'result': rem})

    # Step 4: optional PR creation
    if args.attempt_pr:
        if not args.head:
            print('--attempt-pr requires --head')
            sys.exit(6)
        pr = attempt_create_pr(args.repo, args.head, args.base, headers)
        log['findings'].append({'step': 'create_pr', 'http_status': pr.status_code, 'resp': pr.text})
        if pr.status_code in (200, 201):
            log['findings'].append({'step': 'create_pr', 'status': 'created', 'pr_url': pr.json().get('html_url')})
        else:
            log['findings'].append({'step': 'create_pr', 'status': 'failed', 'http_status': pr.status_code})

    write_log(log)
    print('Troubleshoot complete')


if __name__ == '__main__':
    main()
