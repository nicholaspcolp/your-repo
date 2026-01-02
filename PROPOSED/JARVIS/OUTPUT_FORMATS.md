# Output Formats & Separation of Concerns (Tasks vs Documentation)

Purpose
- Ensure tasks (work that mutates files or changes state) and documentation activities (notes, docs edits, formatting, non-mutating summaries) are tracked separately and not performed synonymously in the same agent window without explicit coordination.

Key rules
- Task records (work items) must be stored in `WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv` with `type=task`.
- Documentation-only items should be stored with `type=documentation` in the same CSV or as files under `WORK/PROCEDURES`/`PROPOSED` with clear linkage to task IDs as needed.
- Active windows/sessions must not be assigned both `task` and `documentation` types at the same time. Conflicts are detected by `scripts/check_session_task_doc_conflict.py` and recorded as defections.
- When dividing work across windows, ensure file locks (`GOV/jarvis/locks.csv`) are acquired for any files to be mutated to prevent concurrent edits.

Templates & tooling
- Use `scripts/priority_tasks.py` with `--type` to create tasks or documentation entries.
- Run `scripts/window_activity.py` to list active sessions and `scripts/check_session_task_doc_conflict.py` to detect and record conflicts.

Example
- Add a documentation entry:
  python scripts/priority_tasks.py add --title "Update README_AUTONOMY_MANIFEST" --owner alice --priority medium --type documentation

- Add a work task and assign to a session:
  python scripts/priority_tasks.py add --title "Apply manifest additions" --owner assistant --priority high --type task --assign-session session:2026-01-02T07:50:48.563805Z

Rationale
- Separating types reduces the risk of accidental simultaneous editing and keeps provenance clear for decisions and artifacts.
