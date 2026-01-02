Policy: Chat-derived task proposals and application

Purpose
- Ensure every task generated from user chat follows the TRIAL manifest governance procedures.

Procedure
1) Detection
- `scripts/chat_to_tasks.py` scans `WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl` for actionable user messages and proposes tasks.
- Proposed tasks are written with `status=proposed` and `notes` containing `message_id` and `proposed_by:<run_id>` when run from a trial/runner.

2) Dry-run behavior
- During dry-run (`run_trial --dry-run` or `autonomous_manifest_runner --dry-run`), proposals are written to:
  - `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/task_proposals_<run>.txt` (human-readable short text)
  - `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/task_proposals_<run>.json` (machine-readable canonical JSON schema: see "Proposals JSON Schema" below)

Proposals JSON Schema (canonical)
```
{
  "generated_at": "2026-01-02T10:00:00Z",
  "run_id": "20260102T100000Z-abcdef12",
  "proposals_count": 2,
  "proposals": [
    {"id":"CHAT-abc123","title":"...","message_id":"...","notes":"...","priority":"medium"},
    {...}
  ]
}
```

3) Applying proposals
- To apply proposals (append to `WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv` as active `todo` rows), the manifest's `approval_gates` are consulted.
- If `human_approval_before_manifest_change` is present, the runner will only apply proposals if a valid approval exists in `GOV/jarvis/manifest_approvals.csv` for the manifest being changed.
- If no approval is present, the runner writes proposals only and records a defection in `GOV/JARVIS/defections.csv` indicating missing approval.

4) Provenance & notes
- Every proposed or applied task includes a `notes` value linking to the source message (`message_id`), the run id that proposed it (`proposed_by`), and the raw message text for audit.

5) Manifest cross-references
- `WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json` should include:
  - `auto_propose_tasks_from_chat`: boolean
  - `window_comm_log`: path to the inter-window notes CSV
  - `governance_rules_doc`: pointer to `PROPOSED/JARVIS_PRIORITIES.md`

6) Operator action
- To manually apply proposals, an operator may:
  - Create an approval for the manifest using `scripts/manifest_approval.py approve --manifest <manifest> --actor <who> --reason "approve chat-derived tasks"`
  - Re-run `run_trial` or run `scripts/chat_to_tasks.py --run-id <run> --apply`

Notes
- This process preserves a conservative default (propose-only) when approvals are required by policy, while supporting automated application when no approval gate is present or when approval has been granted.
