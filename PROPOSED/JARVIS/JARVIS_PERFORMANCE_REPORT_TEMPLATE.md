# JARVIS Performance Report Template

- run_id: <run id>
- manifest: <manifest path>
- dry_run: true|false
- tasks_count: N
- tasks: [list of tasks with id, status, owner, assigned_session]
- governance: { defection_capture: bool, dry_run: bool, max_changes: int, approvals: [], locks: [] }
- metrics:
  - tasks_started:
  - tasks_completed:
  - percent_overall_complete:
  - time_spent_seconds:
  - errors_encountered: [list of error references]
- notes: freeform summary

Use this template to produce a JSON/markdown performance report at the end of each trial run.