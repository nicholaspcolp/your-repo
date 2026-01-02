# Manifest-Specified User Output Format

This document records the output format and operational references the `TRIAL_MANIFEST.json` requires agents and users to follow.

1) Manifest field specifying this document
- `TRIAL_MANIFEST.json` -> `manifest_instructions.output_formats` points to this file. Agents must consult this file for canonical output expectations.

2) Canonical output formats (summary)
- Human-facing documentation: Markdown files under `PROPOSED/` or `PROPOSED/JARVIS/` (e.g., rolecards, policies, changelogs).
- Runtime artifacts: JSON files under `WORK/JARVIS_BRAIN_OPERATIONS/` subfolders:
  - `PROGRESS/` — preflight/postflight/progress marker JSON files following the schema in `PROPOSED/JARVIS/DEFECTION_OUTPUT_FORMAT.md`.
  - `PROGRESS/task_proposals_<run>.json` — machine-readable proposals generated during dry-run; schema described in `PROPOSED/JARVIS/CHAT_TASKS_PROCESS.md`.
  - `PROGRESS/window_comm_<ts>.json` — inter-window communication aggregates.
  - `PROGRESS/task_inventory_<ts>.json` — consolidated task inventory used by the manifest runner and metrics generator.
  - `WINDOW_MANIFESTS/` — per-window manifest snapshots (`<window_id>.json`).
  - `merge_report_*.json` — merge reports created by `scripts/jbrain_sync.py`.
- Chat logs and summaries: `WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl`, `WORK/CHAT/SUMMARIES/`, `WORK/CHAT/chat_index.json`.

3) Dynamic task list source
- The authoritative dynamic priority/task list is `TRIAL_MANIFEST.json`'s `dynamic_priority_list` field. It is updated by `scripts/priority_recalculator.py` and can be merged/updated by `scripts/jbrain_sync.py` when per-window manifests are merged.
- For human consumption, `WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv` may be used as an export of the current tasks and ordering.

Recommended additions/edits to OUTPUT TEMPLATE:
- Include `docs_ref` in `task_progress` and `window_manifest` (implemented in templates). This allows referencing human-readable docs in `PROPOSED/`.
- Add `agent_version` and `executor_id` to `provenance` for stronger auditability.
- Consider a short `progress_summary` (1-2 lines) in progress entries for quick review in UI/CSV exports.

Manifest implementation objectives (tracked and referenced):
- See `WORK/JARVIS_BRAIN_OPERATIONS/PERSISTENT_QUESTIONS.md` for open governance and enforcement questions.
- Agents should append answers to persistent questions and reference them from merge reports when relevant.

4) Manifest implementation objectives (tracked)
- `WORK/JARVIS_BRAIN_OPERATIONS/DEV_PLAN.md` — development milestones and conflict resolution policy.
- `WORK/JARVIS_BRAIN_OPERATIONS/CHANGELOG.md` — recorded manifest version history and changes.
- `WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json` — canonical manifest and templates sections.
- `WORK/JARVIS_BRAIN_OPERATIONS/TEMPLATES/` — `window_manifest_template.json` and `task_progress_template.json`.
- `scripts/` helpers: `progress_writer.py`, `jbrain_sync.py`, `priority_recalculator.py`, `ci_check.py`.

5) Agent requirements
- Agents must emit preflight and postflight markers via `scripts/progress_writer.py` and may emit per-window manifests via the `--window` flag.
- Agents must not write long-form documentation into runtime folders; use `PROPOSED/` and include `docs_ref` in progress entries when needed.

6) How we will track progress
- Implementation steps and status are tracked in `WORK/JARVIS_BRAIN_OPERATIONS/DEV_PLAN.md` and the todo list managed by the assistant.
- Each jbrain_sync merge appends a changelog entry and writes a `merge_report` with details of changes.

If you want additional fields or a machine-readable schema here, tell me which fields to include and I will add them and update `TRIAL_MANIFEST.json` accordingly.
