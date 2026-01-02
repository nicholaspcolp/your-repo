# PR: Inter-window comms & chat→task proposals; manifest approval gating

This PR implements:
- Inter-window communication aggregation (`scripts/jarvis_window_comm.py`) and progress aggregation
- Chat→task proposal pipeline (`scripts/chat_to_tasks.py`) including dry-run JSON proposals and human-readable text
- Manifest approval gating and defection capture handling (preflight/postflight)
- Progress & metrics reporting (`scripts/generate_manifest_stats.py`, `scripts/compute_overall_progress.py`)
- Unit tests including acceptance test for approval-gated apply (`tests/test_acceptance_apply.py`)
- CI workflow to run `pytest` on PR (`.github/workflows/jarvis-ci.yml`)

Operator notes:
- Approve proposals using `python scripts/manifest_approval.py approve --manifest WORK/JARVIS_BRAIN_OPERATIONS/TRIAL_MANIFEST.json --actor <who> --reason "approve chat-derived tasks"`
- After approval, apply proposals by re-running `scripts/run_trial.py` with manifest `dry_run:false` or by running `python scripts/chat_to_tasks.py --apply`.

Testing:
- Unit + acceptance tests included; CI workflow will run `pytest` on PR to validate changes.
