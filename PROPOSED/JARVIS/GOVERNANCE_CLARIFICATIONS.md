Governance clarifications provided by user (2026-01-02)

Summary of decisions to apply to PROPOSED manifest and CI enforcement:

- Human approval gates:
  - Manifest schema changes require human approval (any JARVIS window may propose, but changes are not applied without human approval).
  - File deletion operations require explicit human approval.
  - Umbrella methodology changes (high-level changes to task workflows or handoff methods) require human approval.

- Autonomous percent thresholds & workflow:
  - Percent and completion judgments are collaborative: Jarvis windows must PLAN, PREDICT, TRACK PROGRESS, SELF-ASSESS, and REPORT.
  - Decisions to mark >=50% or to mark COMPLETE must be accompanied by predictive breakdowns, verification steps, and corroborating self-evals from involved windows; task-tracker must record these artifacts.

- Rolecards and window IDs:
  - All JARVIS instances share the same `rolecard_id` (global Jarvis rolecard).
  - Each chat/window is assigned an automatic `window_id` unique per session; manifests and progress entries must reference this id to differentiate sources.

- Defection handling and peer review:
  - Jarvis instances must review each other's work for manifest protocol adherence, output formats, and task-tracking completeness.
  - User-facing outputs should emphasize task-tracking statistics, plans, and self-evaluations.

- Handoff methods and Method 1 correction:
  - User asked for review/share of methods and indicated Method 1 was misunderstood; request clarification from user on the intended Method 1 semantics before implementing automation.

- Acceptance criteria requirement:
  - Every user request should aim for 100% assessment coverage: provenance, critical-thinking methodology, planned tasks, statistics reporting, and self-evaluation must be provided for new user messages.

Next actions (recommended):

- Update `PROPOSED/JARVIS/TRIAL_AUTONOMY_MANIFEST.json` to include these governance entries (human approval gates, file-deletion rules, rolecard/window_id rules, acceptance criteria fields).
- Update `scripts/ci_check.py` to enforce the above at CI time (fail on disallowed schema changes or missing required fields; require a `human_approval` token for deletions or schema modifications).
- Add `WORK/JARVIS_BRAIN_OPERATIONS/TEMPLATES/ACCEPTANCE_CRITERIA.md` documenting the 100% assessment checklist and machine-checkable checks for CI.

If you'd like, I will draft the manifest patch and a CI stub to enforce these rules next — or, please provide your corrected description of Method 1 and I'll incorporate it before patching.
