#!/usr/bin/env python3
"""Check GitHub PAT validity and repo permissions."""
import os
import argparse
import requests

p = argparse.ArgumentParser()
p.add_argument('--repo', help='owner/repo', required=False)
args = p.parse_args()

TOKEN = os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    print('GITHUB_TOKEN not set; aborting')
    raise SystemExit(2)

headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github+json'}

# check token identity
r = requests.get('https://api.github.com/user', headers=headers, timeout=30)
if r.status_code == 200:
    u = r.json()
    print('Authenticated as', u.get('login'))
else:
    print('Failed to authenticate token:', r.status_code, r.text)
    raise SystemExit(1)

# show scopes if available (via root response)
root = requests.get('https://api.github.com/', headers=headers, timeout=30)
scopes = root.headers.get('X-OAuth-Scopes') or root.headers.get('X-Accepted-OAuth-Scopes')
print('Token scopes:', scopes)

if args.repo:
    repo_url = f'https://api.github.com/repos/{args.repo}'
    rr = requests.get(repo_url, headers=headers, timeout=30)
    if rr.status_code == 200:
        rj = rr.json()
        print('Repo found:', args.repo)
        perms = rj.get('permissions')
        print('Permissions for token on repo:', perms)
    else:
        print('Could not access repo', args.repo, 'status:', rr.status_code, rr.text)

print('Done')
