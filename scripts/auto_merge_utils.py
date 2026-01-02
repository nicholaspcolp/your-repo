#!/usr/bin/env python3
"""Utilities for auto-merge: approval checks and PR file inspection."""
from pathlib import Path
import csv
from datetime import datetime
import requests


def has_valid_approval(manifest_path, approvals_path=Path('GOV/jarvis/manifest_approvals.csv')):
    """Return True if there is a non-expired approval row for the given manifest path."""
    p = Path(approvals_path)
    if not p.exists():
        return False
    now = datetime.utcnow()
    with p.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('manifest') == manifest_path:
                exp = row.get('expires_at')
                if not exp:
                    continue
                try:
                    # expected ISO 8601 with optional trailing Z
                    exp_dt = datetime.fromisoformat(exp.replace('Z', ''))
                except Exception:
                    continue
                if exp_dt > now:
                    return True
    return False


def pr_changed_files(repo, pr_number, headers):
    """Return list of filenames changed in the PR via GitHub API."""
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/files'
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return [f.get('filename') for f in r.json()]
