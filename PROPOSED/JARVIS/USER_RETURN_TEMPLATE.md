# User Return Template

This template describes the required structure and human-facing summary that agents must provide when returning results to the user after completing or pausing a task.

Fields (human-readable guidance):

- `task_id`: Task identifier (e.g., T-006)
- `status`: `completed` | `in-progress` | `blocked` | `deferred`
- `percent_complete`: integer 0-100
- `summary`: 1-3 line user-facing summary of actions taken and current state
- `actions_taken`: short bullet list of key actions performed (1-5 lines)
- `next_steps`: short list of recommended next steps and who should take them
- `artifacts`: list of produced artifact paths (point to `PROPOSED/` or `WORK/` as appropriate)
- `provenance`: object with keys `agent_id`, `rolecard_id`, `agent_version`, `executor_id`, `timestamp`
- `docs_ref`: optional pointer to human docs under `PROPOSED/`

Example:

```
{
  "task_id": "T-006",
  "status": "in-progress",
  "percent_complete": 20,
  "summary": "Started analysis of `analyze_pdf_text.py`; extracted text from 3/12 PDFs and logged progress.",
  "actions_taken": [
    "Persisted chat and wrote preflight marker",
    "Locked analyze_pdf_text.py",
    "Extracted text from 3 PDFs and saved to WORK/ARTIFACTS/text_extraction/"
  ],
  "next_steps": ["Continue extraction until 12 PDFs complete (jarvis)", "Run QA checks on extracted text (assistant)"] ,
  "artifacts": ["WORK/ARTIFACTS/text_extraction/page_text_001.json"],
  "provenance": {
    "agent_id": "jarvis",
    "rolecard_id": "rc-trial",
    "agent_version": "0.1",
    "executor_id": "win-2",
    "timestamp": "2026-01-02T08:47:45.875159+00:00"
  },
  "docs_ref": "PROPOSED/JARVIS/EXTRACTION_NOTES.md"
}
```

Agents must include a brief `summary` and structured `provenance` whenever they update `PROGRESS/` or `WINDOW_MANIFESTS/` so the assistant can aggregate these into `PROGRESS_STATS.json` and `TRIAL_MANIFEST.json`.
