# Postflight Marker Template

Fields (JSON):
- run_id
- manifest_ref
- task_id (optional)
- agent_id
- timestamp
- outcome_summary: short string (e.g., 'dry-run:ok', 'applied:partial')
- errors: []
- defection_flag: bool
- artifacts: list of produced artifact paths (reports, audits)

Example:
{
  "run_id": "20260102T075048Z-60d8c25e",
  "manifest_ref": "WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json",
  "agent_id": "script",
  "timestamp": "2026-01-02T07:51:24Z",
  "outcome_summary": "dry-run:ok",
  "errors": [],
  "defection_flag": false,
  "artifacts": ["GOV/reports/jarvis_trials/report_20260102T075048Z-60d8c25e.json"]
}
