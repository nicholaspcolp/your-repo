# JARVIS Autonomy Manifest (Draft)

Purpose
- Provide conventions, APIs, and artifacts for trial autonomy runs. Record start/end of tasks, capture chat transcripts, log search runs, and record manifest changes and performance reports.

Entry points
- `scripts/jarvis_record.py` — chat recording start/record/end/status
- `scripts/generate_performance_report.py` — create a JARVIS performance report for a run
- `scripts/generate_recovery_packet.py` — create recovery packet zip for escalation

Storage locations
- `GOV/JARVIS/chats/` — JSONL chat runs
- `GOV/JARVIS/chat_index.csv` — index of run_id -> start/end timestamps
- `GOV/JARVIS/priority_tasks.csv` — dynamic priority task list (TBD)
- `GOV/reconciliation/fix_missing_results/search_runs.csv` — search run audit log
- `GOV/reports/jarvis_performance/` — performance reports

Safety & Autonomy
- Configurable via `TRIAL_AUTONOMY_MANIFEST.json` (dry-run, whitelist, approval gates)
- All automated destructive actions require recorded approvals and are gated by configured limits.

Report structure example
- START TASK PROGRESS
- ACTUALIZED PROGRESS
- PREDICTED PROGRESS AND REFLECTIVE ASSESSMENT
- JARVIS CREATIVITY AND CRITICAL THINKING
- USER ACTION REQUIRED

Notes
- This document is a living draft and will expand as trial runs produce feedback.
