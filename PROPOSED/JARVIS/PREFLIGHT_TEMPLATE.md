# Preflight Marker Template

Fields (JSON):
- run_id: <run id>
- manifest_ref: <manifest path>
- task_id: <optional task id>
- agent_id: <agent or service id>
- timestamp: <ISO8601 UTC>
- intent_summary: <short summary of intent>
- checks_performed: [list of check descriptions]
- checks_passed: bool
- failures: [detailed failure messages if any]

Example:
{
  "run_id": "20260102T075048Z-60d8c25e",
  "manifest_ref": "WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json",
  "agent_id": "script",
  "timestamp": "2026-01-02T07:50:48Z",
  "intent_summary": "Dry-run trial preflight",
  "checks_performed": ["defection_capture","artifact_paths","ops_root"],
  "checks_passed": true,
  "failures": []
}
