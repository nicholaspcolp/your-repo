
# Output Formats and File Conventions

NOTE: This file was originally created after a misinterpretation of a user note referencing a "defection" (assistant deviation). The naming caused confusion; the document below is intended to define canonical output formats and file conventions (the "OUTPUT_FORMATS" specification). The manifest's `output_formats` reference should point to this document. The assistant acknowledges the mistake and has corrected behavior to follow these formats.

Purpose: define canonical output formats and where different artifact types must be written so that documentation and task artifacts are not conflated across agent windows.

1) File classes and canonical locations
- Documentation (human-readable policy, design, changelogs): write to `PROPOSED/` or `PROPOSED/JARVIS/` as Markdown or YAML. Examples: `PROPOSED/JARVIS/DEFECTION_OUTPUT_FORMAT.md`, `PROPOSED/JARVIS/rolecard_template.yaml`.
- Operational artifacts (per-window manifests, progress markers, merge reports): write to `WORK/JARVIS_BRAIN_OPERATIONS/` subfolders: `PROGRESS/`, `WINDOW_MANIFESTS/`, `PROGRESS/merge_report_*.json`.
- Raw logs and indices: `WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl`, `WORK/CHAT/SUMMARIES/`, `WORK/CHAT/chat_index.json`.

2) JSON schema summaries (informal)
- Preflight marker (path: `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/preflight_<task>_<agent>_<ts>.json`)
  - fields: `marker`, `task_id`, `agent_id`, `rolecard_id`, `timestamp`, `intent_summary`, `manifest_ref`

- Postflight marker (path: `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/postflight_<task>_<agent>_<ts>.json`)
  - fields: `marker`, `task_id`, `agent_id`, `rolecard_id`, `timestamp`, `outcome_summary`, `defection_flag`, `defection_details`, `manifest_ref`

- Progress entry (path: `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/progress_<task>_<ts>.json`)
  - fields: `task_id`, `owner`, `status`, `percent_complete`, `last_updated`, `notes`, `defection_flag`, `provenance` (with `agent_id`, `rolecard_id`, `applied_rule`)

- Window manifest (path: `WORK/JARVIS_BRAIN_OPERATIONS/WINDOW_MANIFESTS/<window_id>.json`)
  - fields: `window_id`, `generated_at`, `tasks` (array of task objects with `id`, `title`, `owner`, `status`, `last_updated`, `notes`)

3) Naming and atomicity
- Filenames MUST follow the templates above. Agents must write to temporary files then rename (atomic write) when possible to avoid partial reads.

4) Separation policy (enforced)
- Documentation must NOT be written into `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/` or `WINDOW_MANIFESTS/`. If an agent needs to produce a human-readable decision explanation, write it to `PROPOSED/` and reference it from progress entries via `manifest_ref` or `docs_ref`.
- Per-window manifests and progress files are authoritative runtime artifacts and must not be used as long-term documentation. Copy relevant summaries into `PROPOSED/` explicitly when preparing durable documentation.

5) Change process
- Changes to these formats must be recorded in `WORK/JARVIS_BRAIN_OPERATIONS/CHANGELOG.md` and reflected in `TRIAL_MANIFEST.json` `manifest_instructions.output_formats`.
# DEFECTION Output Format (DEFECTION[type])

Purpose
- Standardize how DEFECTION items are recorded, exchanged, and triaged across JARVIS and related tooling.

Primary CSV (GOV/JARVIS/defections.csv) - columns
- timestamp: ISO8601 UTC timestamp (string)
- run_id: optional run id to which this defection is attached (string or empty)
- actor: who observed or recorded the defection (string)
- summary: short one-line summary/title (string)
- details: optional long-form details or context (string)
- tags: comma-separated tags for quick filtering (string)
- severity: OPTIONAL (low|medium|high) — for triage priority
- status: OPTIONAL (open|triaged|closed) — lifecycle status

Example CSV row
2026-01-02T07:00:00Z,20260102T064124Z-938c10ab,alice,"Output format mismatch in trial manifest","Observed missing `defection_capture` enforcement","format,manifest",medium,open

JSON-in-chat representation (appended to run JSONL if run_id given)
{
  "run_id": "20260102T064124Z-938c10ab",
  "phase": "defection",
  "timestamp": "2026-01-02T07:00:00Z",
  "actor": "alice",
  "message": "DEFECT: Output format mismatch in trial manifest",
  "details": "Observed missing `defection_capture` enforcement",
  "tags": "format,manifest",
  "severity": "medium"
}

Schema (DEFECTION[type])
- type: "defection"
- required fields: timestamp, summary, actor
- optional: run_id, details, tags, severity, status

Triage & Workflow Notes
- All defections should be reviewed during trial post-mortem or weekly governance review.
- If a defection requires action, convert it into a priority task and reference the original defection row id (timestamp+actor) in the task notes.
- `TRIAL_AUTONOMY_MANIFEST` should include `defection_capture: true` to enforce capture as a precondition for automated trials.
