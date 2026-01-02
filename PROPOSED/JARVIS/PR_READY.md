PR Ready: Inter-window comm + Chat→Task proposals + Governance enforcement

Summary
- This PR implements inter-window communication aggregation, chat→task proposals (with provenance), overall progress percent reporting, manifest approval gating for applying proposals, and basic unit tests.

Files changed
- Added: `scripts/jarvis_window_comm.py`, `scripts/chat_to_tasks.py` (new flags), `scripts/compute_overall_progress.py`, `scripts/generate_task_inventory.py`, `tests/*`.
- Modified: `scripts/run_trial.py`, `scripts/autonomous_manifest_runner.py`, `scripts/progress_writer.py`, `WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json`, `WORK/JARVIS_BRAIN_OPERATIONS/README.md`, `CHANGELOG.md`.

Tests & CI
- Unit tests added: `tests/test_chat_to_tasks.py`, `tests/test_compute_overall_progress.py`, `tests/test_jarvis_window_comm.py` (all pass locally).
- Recommend adding a quick CI job to run `pytest -q` on PR; include `--fail-on-warnings` optional.

Migration notes
- New artifacts produced during runs:
  - `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/window_comm_<ts>.json` (includes `overall_progress`)
  - `WORK/JARVIS_BRAIN_OPERATIONS/PROGRESS/task_proposals_<run>.json` and `.txt` (dry-run proposals)
  - `GOV/reports/jarvis_trials/performance_report_<ts>.json`
- Operators should review proposals JSON and approve the manifest using `scripts/manifest_approval.py approve --manifest <manifest> --actor <who> --reason "approve chat-derived tasks"` prior to applying proposals.

Suggested PR title & description
- Title: "Inter-window comms & chat→task proposals; manifest approval gating; percent metrics (6.67% current)"
- Description: include summary, files changed, test results, migration notes, and operator steps to approve proposals.

Next steps (post-merge)
- Add CI workflow to run tests and verify recorded artifacts exist after a dry-run.
- Improve `estimated_percent` heuristics using historical durations and per-task timing traces.
- Add acceptance tests for approval-gated apply behavior.
