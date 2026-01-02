#!/usr/bin/env python3
"""Generate progress reports (JSON + Markdown) from PROGRESS_STATS.json.

Writes to WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS_REPORTS/ using the template in TEMPLATES.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
STATS = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS_STATS.json')
TEMPLATE = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/TEMPLATES/PROGRESS_REPORT_TEMPLATE.json')
OUTDIR = ROOT.joinpath('WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS_REPORTS')


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding='utf-8'))


def build_report(stats):
    tasks = stats.get('tasks', {})
    total = 0
    count = 0
    breakdown = []
    for tid, t in tasks.items():
        pct = t.get('percent_complete') or 0
        total += pct
        count += 1
        breakdown.append({
            'task_id': tid,
            'owner': t.get('owner'),
            'status': t.get('latest_status'),
            'percent_complete': pct,
            'last_updated': t.get('last_updated'),
            'provenance_sample': t.get('provenance_sample'),
            'events_count': t.get('events_count'),
            'progress_summary': t.get('progress_summary')
        })

    overall = int(total / count) if count else 0

    report = {
        'report_type': 'progress_report',
        'generated_at': _now_iso(),
        'summary': f'{count} tasks tracked; overall {overall}% complete',
        'overall_percent_complete': overall,
        'task_breakdown': breakdown,
        'stats_ref': str(STATS),
        'manifest_ref': 'WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json'
    }
    return report


def write_outputs(report):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%dT%H%M%SZ')
    jpath = OUTDIR.joinpath(f'progress_report_{ts}.json')
    mdpath = OUTDIR.joinpath(f'progress_report_{ts}.md')
    jpath.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    # simple markdown render
    lines = [f"# Progress Report — {report['generated_at']}", '', report['summary'], '', f"**Overall percent complete:** {report['overall_percent_complete']}%", '', '## Task breakdown', '']
    for t in report['task_breakdown']:
        lines.append(f"- **{t['task_id']}**: {t['status']} — {t['percent_complete']}% — {t.get('progress_summary') or ''}")

    mdpath.write_text('\n'.join(lines), encoding='utf-8')
    return jpath, mdpath


def main():
    stats = load_json(STATS)
    if stats is None:
        print('No PROGRESS_STATS.json found; run progress_stats.py first')
        return 2
    report = build_report(stats)
    j, m = write_outputs(report)
    print('Wrote', j, m)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
