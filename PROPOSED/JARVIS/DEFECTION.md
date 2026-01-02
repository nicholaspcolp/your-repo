# DEFECTION (glossary entry)

Definition
- DEFECTION: A small-format, often informal or ongoing item that does not fit neatly into standard task outputs, KPIs, or manifest entries. Examples: format/format-procedure deviations, small discussion threads, ad-hoc queries, or procedure-edge cases that should be tracked but not necessarily converted into formal tasks immediately.

Purpose
- Ensure these items are captured systematically so they are not lost and can be triaged later.
- Provide traceability: link each defection back to a run_id or task where relevant.

Storage & Format
- Primary CSV: `GOV/JARVIS/defections.csv` (columns: timestamp, run_id, actor, summary, details, tags)
- Each defection optionally writes a `phase:'defection'` message into `GOV/JARVIS/chats/<run_id>.jsonl` when a run is specified
- Entries should be short and tagged; longer items may be converted to tasks with a task id.

Procedures & Standards
- Any participant (user or agent) may log a defection via the CLI:
  - `python scripts/jarvis_record.py defection --actor <who> --summary "Short summary" --details "Optional details" --tags "format,procedures" [--run <run_id>]`
- The TRIAL_AUTONOMY_MANIFEST must include a `defection_capture: true` field to ensure the trial enforces defection logging as a precondition for autonomous actions.

Triage & Workflow
- Periodically (weekly or per-trial), review `GOV/JARVIS/defections.csv` and convert high-priority items into `priority_tasks.csv` or add to manifests as required.
- Use a tag-based filter to quickly find defect categories (e.g., `format`, `procedures`, `glossary`).

Rationale
- Captures the creative and edge-case discussions that are otherwise hard to quantify, ensuring better provenance and auditability of decisions.
