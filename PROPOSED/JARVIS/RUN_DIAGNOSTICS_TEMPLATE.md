# Run Diagnostics Template

Purpose: store preflight/postflight failures and key outputs to reproduce or triage a failed run.

Fields (JSON):
- run_id
- timestamp
- manifest_ref
- preflight_stdout
- preflight_stderr
- failing_checks: [strings]
- environment_snapshot: {ops_root, approvals_count, locks, active_sessions}
- suggested_actions: [strings]

Example:
{
  "run_id": "20260102T075048Z-abc123",
  "timestamp": "2026-01-02T07:50:48Z",
  "manifest_ref": "...",
  "preflight_stdout": "...",
  "preflight_stderr": "...",
  "failing_checks": ["defection_capture not set"],
  "environment_snapshot": {"approvals_count":0, "locks":[], "active_sessions":[]},
  "suggested_actions": ["Set defection_capture: true in manifest", "Create approval using scripts/manifest_approval.py"]
}
