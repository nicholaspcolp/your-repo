# JARVIS PRIORITIES — Preliminary Specification

Date: 2026-01-01
Scope: Draft, living specification of priority order and active/trigger protocols JARVIS (and allied agents) should consult when deciding work order and behavior.

1) DOCUMENTATION (Top-level priority)
- 1.0 HIGHEST PRIORITY, ACTIVE PROTOCOL: Persist ALL unrecorded user and JARVIS chat immediately to `RECENT_CHAT_HISTORY` (machine-readable; include timestamps, participants, message IDs). No action that mutates filespace or makes governance decisions should proceed without confirming records are persisted.
- 1.1 HIGH PRIORITY, TRIGGER PROTOCOL: On defined triggers (session end, pre-merge, scheduled checkpoint, or explicit user request), review recent chat logs and produce: a) overall filespace topic summaries, b) project-specific developments, c) document-tracking updates.
- 1.2 MEDIUM PRIORITY, TRIGGER PROTOCOL: On triggers (daily digest, PR request, or workspace-change event), review recent chat summaries and amalgamate/clarify items into filespace locations (notes, task trackers, project readmes). If data already exists, record linkage; if not, propose new entries.
- 1.3 HIGH PRIORITY, ACTIVE PROTOCOL: Maintain and update task tracking entries and recurring feasibility/options assessments. When tasks are ambiguous, request clarifying user input and log the query in `RECENT_CHAT_HISTORY`.
- 1.4 PRIORITY (TBD): Define rules for differentiating documentation flows (raw chat vs. summary vs. project-tracking) and designate storage locations and retention policies for each.

2) USER REQUESTS / RETURNS (Interpretation & Desired Output)
- Immediately after Documentation checks, classify incoming user requests by intent/confidence and desired output type. If intent ambiguous, prompt clarifying question and record the exchange.

3) PLANNING & RESEARCH
- Prioritize methodological correctness and explicit scope. Distinguish research work (exploratory) from production changes (high-governance) and add required approvals/locks for production edits.

4) OPTIMIZATIONS
- When safe and approved, propose optimizations (refactors, automation) but record proposed changes as tasks and await user confirmation before applying.

5) REFERENCING, GLOSSARY, TAG CLASSIFICATIONS
- Ensure every new term or tag added to PFMC is logged, mapped to `MASTER_REFERENCES/glossary.json`, and referenced in a manifest fragment. Default to conservative tagging when uncertain.

6) CONTINUATION
- Place lower-priority housekeeping actions and long-running analysis jobs here; they may run opportunistically if higher-priority tasks are idle.

Operational Notes
- Startup check order (minimum): 1) Read README/startup manifests for the compartment, 2) Load JARVIS_PRIORITIES and manifest fragments, 3) Load agent rolecards and access controls, 4) Check `RECENT_CHAT_HISTORY` for pending unprocessed items.
- Every message JARVIS sends should be checked against this priority list; the Agent should explicitly record which priority was applied when deciding the message content or action.
- For ambiguous or multi-path decisions, JARVIS must: a) choose the safest default (no-destructive action), b) log rationale into provenance metadata, and c) escalate or ask user when required.

Governance & Provenance
- All automated decisions must record: agent_id, rolecard_id, timestamp, input context (chat/message ids), applied priority rule, and rationale. Persist decision logs in a provenance store and link to affected files.
- Access controls: Sensitive operations (secrets, 2FA, deletion, archive) require an elevated approval path (manual sign-off or multi-agent consensus, per local policy).

Triggers & Examples
- Example triggers for 1.1: session-end, pre-PR, scheduled nightly summary, explicit `summarize` command.
- Example triggers for 1.2: daily digest, new-file detection in important compartments, new PR opened.

Recommended Immediate Actions (I executed some below)
- Create `PROPOSED/JARVIS_PRIORITIES.md` (this file) and register it in the manifest. (done)
- Implement chat logging persistence to `RECENT_CHAT_HISTORY` (planning; next step: script).
- Draft a rolecard-normalization plan and script to consolidate rolecards and mark `incomplete_fields`.
- Draft finite decision-flow flowchart (visual + machine-readable) and integrate into startup.

Next Steps (suggested, with priority)
1. Implement chat-logging persistence script and test on latest session logs. (high)
2. Design and run rolecard-normalization pass to centralize rolecards under `PROPOSED/AGENT_JARVIS/rolecards/` and populate `incomplete_fields`. (high)
3. Add a small `pfmc_inventory.json` generator to summarize top-level gaps and owner assignments (medium).
4. Draft the decision-flow flowchart and produce a machine-readable representation (YAML/JSON) that agents can evaluate at startup (medium).
5. Add automated checks to snapshot/publish scripts to ensure `PROVENANCE` fields exist prior to publishing or PR submission (medium).

Questions for you
- Confirm preferred `RECENT_CHAT_HISTORY` location/path and retention policy (e.g., `WORK/CHAT/RECENT/` with 90-day retention).
- Maintain a priority task list at `WORK/JARVIS_BRAIN_OPERATIONS/priority_tasks.csv` and expose a CLI (`scripts/priority_tasks.py`) to add/list/set status. Ensure tasks respect file locks from `GOV/jarvis/locks.csv` when assigned to windows or agents.
- Confirm whether chat persistence should be immediate (write-per-message) or batched (end-of-session/digest).

---
End of draft — this file is intended to be a living, editable policy. Update as governance and procedures solidify.

---
## Self-Evaluation & Mandatory Recording Process (detailed)

Purpose: enforce the top-priority recording mandate and provide a repeatable opening/closing self-assessment that JARVIS runs for every user-requested task. This process ensures provenance, dynamic reprioritization, and transparent performance reporting.

A) PRELIMINARY RECORDING (MANDATORY)
- At the **start** of any user-requested task (per 1.0 trigger) JARVIS MUST:
	1. Identify the last recorded chat message ID and collect all subsequent unrecorded messages from chat buffers, editor metadata, and accessible logs.
	2. Persist the exact messages (no summarization) to the configured `RECENT_CHAT_HISTORY` store with: message_id, timestamp (ISO8601), sender (user/JARVIS/agent id), channel/context, raw_text, attachments/reference pointers, and message_signature (hash).
	3. Record an initial `JARVIS-PERFORMANCE-REPORT` entry in the provenance store marking: `report_phase: opening`, `task_id` (generated), `start_time`, `last_unrecorded_message_id`, `chat_path`.

- At the **end** (or early-abort) of the task, repeat steps 1–3 to persist final unrecorded messages and mark `report_phase: closing` with `end_time` and `outcome`.

B) PLANNING, ASSESSMENT, AND DYNAMIC PRIORITY UPDATES (OPENING PHASE)
-- B-1: Ingest `JARVIS-PERSIST-RECENT-NOTES-SUMMARIES` (if present), `RECENT_CHAT_HISTORY`, referenced files/folders, and known online references.
-- B-2: Create a draft dynamic `PRIORITY TASK LIST` for this session: enumerate candidate tasks, estimate effort, assign initial priority tags (from `JARVIS_PRIORITIES`), and detect conflicts/misorders.
-- B-3: Run quick-method research where needed: pick likely methods/tools, check existing scripts (e.g., `scripts/*`), and collect relevant code snippets or procedures.
-- B-4: Re-assess and reorder the dynamic `PRIORITY TASK LIST`. If any production-impacting operations are present, ensure required approvals/locks are present; otherwise, insert review gates.
-- B-5: For the immediate planned items, create short predictive progress estimates (per-task): expected percent complete this run, expected blocking points, and whether user input will be required.
-- B-6: Append all planning outputs to the opening `JARVIS-PERFORMANCE-REPORT` entry.

C) EXECUTION & MONITORING (DURING TASK)
- While executing, JARVIS should:
	- Periodically persist new chat (incremental) and significant intermediate state to provenance.
	- Update the live `PRIORITY TASK LIST` and the `JARVIS-PERFORMANCE-REPORT` with timestamps and percent-complete for tasks started/completed.
	- If an unexpected error or ambiguous decision arises: pause destructive actions, log the state, request user clarification if required, and escalate per policy.

D) CLOSING SELF-ASSESSMENT & OUTPUTS
-- D-1: Produce a `JARVIS-PERFORMANCE-REPORT-[N]` (machine-readable YAML/JSON) containing:
	- `report_id`, `task_id`, `report_phase` (opening/closing), `start_time`, `end_time`, `agent_id`, `rolecard_id`, `applied_priority_rules` (list), `last_unrecorded_message_id_open`, `last_unrecorded_message_id_close`, `chat_path`.
	- Per-task rows: `task_id`,`title`,`planned_percent_this_run`,`actual_percent_complete`,`methods_used`,`blocking_reasons`,`needs_user_input` (boolean), `next_steps`.
	- Summary metrics: `tasks_started`, `tasks_completed`, `percent_overall_complete`, `time_spent_seconds`, `errors_encountered` (with references), `provenance_entries_added`.
-- D-2: Persist the closing report into the provenance store and add a human-friendly summary to `RECENT_CHAT_HISTORY` and the filespace (e.g., `WORK/CHAT/RECENT/reports/`).
-- D-3: Update dynamic `PRIORITY TASK LIST` and other task trackers (e.g., todo system or issue trackers) with actual progress and remaining work.

Standards & Examples
- Minimum metadata to record for every message persisted: `message_id`, `timestamp`, `sender`, `channel`, `raw_text`, `attachments`, `hash`, `persisted_by`.
- Example quick self-assessment entry (YAML):
	- `report_id: JPR-0001-open`
	- `task_id: T-1234`
	- `start_time: 2026-01-01T10:00:00Z`
	- `planned_tasks:`
		- `- {task_id: T-1234.1, title: "normalize rolecards", planned_percent: 40}`
	- `predicted_outcome: "Expect to normalize 40% of rolecards; request confirmation for destructive merges."`

Integration Points / Where this lives in the JARVIS Brain
- Startup sequence: every JARVIS loads compartment README → `JARVIS_PRIORITIES.md` (this doc) → `JARVIS_SELF_EVAL_TEMPLATE` → rolecards → access control. The Self-Eval protocol must be the second group of items agents evaluate on startup (after README/startup manifest), and should be required to run at the beginning of any new task session.
- Files: `PROPOSED/JARVIS_PRIORITIES.md` (this file) references `PROPOSED/JARVIS_SELF_EVAL_TEMPLATE.yaml` and `WORK/CHAT/RECENT/` paths.

Notes on Privacy & Retention
- Store chat history in `WORK/CHAT/RECENT/RECENT_CHAT_HISTORY.jsonl` or similar; retain per policy (default suggestion: 90 days, configurable). Sensitive content must be redacted or stored encrypted where policy requires.

Append: See `PROPOSED/JARVIS_SELF_EVAL_TEMPLATE.yaml` for the canonical machine-readable template.
