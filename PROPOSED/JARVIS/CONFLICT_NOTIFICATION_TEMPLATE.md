# Conflict Notification Template

Subject: [JARVIS] Session Conflict Detected — {session_id}

Body:
A conflict was detected where session `{session_id}` has assignments for both `task` and `documentation` work.

Details:
- session_id: {session_id}
- assigned_types: {types}
- detected_at: {timestamp}
- suggested_action: "Review assigned tasks; move documentation work to another session or mark task as documentation; avoid simultaneous edit on shared files."

To triage:
- Run `python scripts/check_session_task_doc_conflict.py` to list conflicts and write `GOV/JARVIS/defections.csv` entries.
- Convert a defection into a priority task or reassign sessions using `scripts/priority_tasks.py`.
