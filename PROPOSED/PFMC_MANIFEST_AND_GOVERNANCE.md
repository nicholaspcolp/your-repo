# PFMC Manifest and Governance Document

---
## Research/Planning Notes (Autonomous Expansion)
- **Provenance & Agent Decision-Making Topics:**
	- The PFMC manifest currently references at least 2 explicit topics: 'provenance' and 'agent decision-making' (see topics.json: provenance, manifest_management, automation_ci, governance, qa_validation, backup_and_eject, etc.).
	- topics.json (version 2025-12-30) includes ~6+ agent decision-making topics and 1+ provenance topic, with additional related topics (e.g., governance, QA, automation_ci).
- **Most Recent PFMC Version:**
	- The latest PFMC CSV is PROPOSED FILESPACE MASTER CSV 4.1.csv (see workspace).
- **Glossary Coverage:**
	- The PFMC contains a glossary.json with core terms, equivalencies, and tag schema/examples. Not all workspace terms may be covered; ongoing expansion is recommended.
- **Tag Coverage:**
	- Tag schema and examples are present in glossary.json and master_refs_fragment.json (fields: owner, sensitivity, function, lifecycle, reviewStatus, project, appendixLabel, dualReference, externalLocation, derived, qa, assigned).
	- PFMC planning should ensure tags are used consistently for filtering, provenance, and agent navigation.
- **Manifest Fragments:**
	- Manifest fragments (e.g., master_refs_fragment.json) summarize key files, owners, rationale, and recommended tag fields for a folder. They provide machine-readable context for agents and humans, supporting navigation, provenance, and policy enforcement.
	- Fragments include: id, pfmc_path, level, children, rationale, contents, tags_schema_ref, tags_recommended_fields, child_owners, owner, last_updated, manifest_version.
	- Example: master_refs_fragment.json covers glossary, function_refs, data_sources, schemas, stable_ids, reference_index, secrets_index.

---
## Research Notes & Ongoing Topics
- **AI Agent Governance:**
	- Provenance & traceability: All files/actions traceable to agent (human or AI), with logs of changes and rationale.
	- Explainability: Documentation supports explainable AI; rationale/context/decision logs included.
	- Access control: Compartmentalize sensitive files; least-privilege access; audit trails.
	- Versioning & rollback: All files versioned, rollback possible if agent/human error.
	- Ethics & compliance: Guidelines for ethical use, bias mitigation, legal/regulatory compliance.
	- Agent roles/capabilities: Registry of agent types, roles, permissions, scope, and limitations.
	- Continuous monitoring: Automated checks for file integrity, unauthorized changes, and compliance.
- **Planned Research:**
	- Automated conflict resolution between agent/human edits.
	- Dynamic access control based on agent trust scores or recent behavior.
	- Integration of explainability frameworks (e.g., XAI) into documentation.
	- AI-driven suggestions for file organization and manifest updates.

---

## 1. Introduction & Purpose
This document defines the structure, navigation, governance, and operational standards for the PFMC (Proposed Filespace Master Catalog). It is a living reference for both AI agents and human users to ensure optimal workflow, traceability, and scalability.

## 2. Filespace Structure & Navigation
- **Folder Map:** (Insert or link to current folder structure)
- **Navigation Cues:** Each folder contains a README or pointer file with summary, glossary links, and cross-references.
- **Glossary:** Centralized glossary file, referenced throughout.

## 3. Decision-Making Flowcharts
- **File Sorting:** Flowcharts for accepting, archiving, or discarding files.
- **Document Lifecycle:** Diagrams for document status (draft, in review, accepted, superseded, archived).

## 4. Governance & Standards
- **Metadata Standards:** Every file/folder should have a metadata block (YAML front matter or JSON) with author, creation date, last modified, status, tags, and references.
- **Access Control & Permissions:** Define roles (admin, contributor, reviewer, guest) and permissions for each compartment. Document how access is managed.
- **Automated Validation & Linting:** Specify tools/scripts to check compliance with naming, metadata, and structure standards. Mandate pre-merge checks.
- **Change Management & Audit Trails:** Require significant changes to be logged in a CHANGELOG or via commit messages referencing the manifest. Consider a decision log for major governance/process changes.
- **Reference Integrity:** Regularly validate all cross-references, glossary links, and document pointers. Automate this check if possible.
- **Archival & Deprecation Policy:** Define criteria/process for archiving or deprecating files/folders/procedures. Maintain an "archive" compartment.
- **Onboarding & Training:** Include a "Getting Started" section for new users/agents, with links to key docs, standards, and procedures. Provide example workflows.
- **Feedback & Continuous Improvement:** Add a section for users/agents to propose improvements to the manifest or filespace structure. Schedule regular reviews.
- **Integration with JARVIS/AGENT Systems:** Document how PFMC structure/metadata are consumed by JARVIS/AGENT systems. Specify required hooks/APIs/data formats.
- **Disaster Recovery & Backups:** Outline backup procedures and recovery plans for critical files and metadata.
- **Naming Conventions:** Standardized file/folder naming.
- **Compartmentalization:** Rules for referencing and linking between compartments.
- **Referencing:** All files reference relevant procedures, standards, and JARVIS/AGENT documentation.

## 5. Workflow Optimization
- **Document Tracking:** Each file/folder has a tracking log (manual or automated).
- **Task/Progress Tracking:** Integration with project management tools or markdown logs.
- **Automation Triggers:** E.g., chat log summaries, document review reminders.

## 6. Scalability & Expansion
- **Adding Projects/Components:** Procedures for onboarding new content.
- **Versioning:** Supersession and archival processes.

## 7. Mandated Processes
- **Chat Logging:** All user/agent chats are logged and summarized regularly.
- **Summaries/Amalgamations:** Regular review and update of documentation from chat logs and project activity.
- **Documentation Updates:** Mandated review cycles and update triggers.

## 8. References
- **Local/Project-Specific Considerations:**
	- JARVIS/AGENT integration: Manifest and file structure are machine-readable (YAML/JSON front matter, standardized folder names) for JARVIS/AGENT parsing.
	- Reference pointers: Use manifest "pointer" files to direct agents/humans to relevant procedures, standards, and glossary entries.
	- Procedural embedding: Each compartment/folder should have a README or manifest fragment with local procedures, agent roles, and escalation paths.
	- Chat & action logging: Mandate logging of all agent/human interactions, with regular automated summarization and integration into documentation.
	- Task & progress tracking: Integrate with JARVIS/AGENT task management—files should reference related tasks, tickets, or project milestones.
	- Compartmentalization: Use folder-level .gitignore and access metadata to enforce boundaries between PFMC, EFMC, and other spaces.
	- Change proposals: Agents and humans should submit change proposals via manifest-linked forms or PR templates, with automated review triggers.
- **JARVIS/AGENT Systems:** Links to operational docs, procedures, and standards.
- **Related Documentation:** Cross-references to EFMC, project, and research files.


---

## Critical Questions & Answers (Living Section)
### (Recent User/Agent Q&A)
1. **Which metadata fields are essential for every agent rolecard and why?**
	- A) Name, version, permissions, last updated, description, linked policies (best for robust governance, but may be incomplete for preliminary rolecards; mark incomplete fields for future review).
2. **How should the PFMC handle cases where automated EFMC→PFMC mapping produces low-confidence or ambiguous results?**
	- To be addressed after further mapping and EFMC audit.
3. **Describe manifest fragments in detail:**
	- Manifest fragments are machine-readable JSON files summarizing the contents, rationale, ownership, and recommended tags for a folder. They support agent/human navigation, provenance, and policy enforcement. Fragments include references to key files (e.g., glossary.json, functions_catalog.json), recommended tag fields, and child ownership. They are updated as the filespace evolves and are critical for scalable, auditable PFMC management.
4. **Does the PFMC contain details on all relevant glossary terms?**
	- Glossary.json covers core terms and equivalencies, but ongoing review/expansion is needed to ensure full coverage.
5. **Have we included tags (of various types) in our PFMC manifest/planning?**
	- Yes; tags are present in glossary.json, master_refs_fragment.json, and CSVs. Consistent use and expansion are recommended.
1. **Which of the following is the most important reason for maintaining detailed provenance and traceability in the PFMC?**
	- D) To increase navigability for agents. The smaller our finalized PFMC, the more relevant context an agent can consider when making a decision, and less effort is spent on local search and organization/documentation/procedural processes. Secondary choices: C) To support explainability and accountability for both human and AI agent actions.

2. **How should the PFMC manifest balance the need for strict governance (to prevent errors or misuse by agents) with the flexibility required for rapid research, prototyping, and collaboration?**
	- We should categorize jarvis/user interaction states and enable action classifications in the background. We should ALWAYS identify to the user when an ambiguous path is encountered—even if in the midst of an operation, so that we can hone in on and refine the details in the governance. We want strict governance, but have defaults to user for unclear decisions.
	- Research: mostly autonomous, triggered or suggested by action items that require development planning, methodology planning, troubleshooting, etc.
	- Prototyping: flexible protocols by case. Early prototypes may start multiple methodologies/options; complex prototypes should solidify methodology before time-consuming development. Extra caution to communicate/confirm optimal methodology to user and confirm agreement with downstream plans.
	- Collaboration: AGENT, SUBJARVIS, ORGSTRUCT collaboration is under preliminary development. For user collaboration, processes and verifications should occur with maximum reasonable autonomy. Protocols for user interactions, required inputs/approvals, autonomous operation, output templates/variants, etc., should be refined as more context and outcomes are observed.

3. **Which of the following best describes the role of “pointer” files in the PFMC structure?**
	- B) They provide navigation, context, and cross-references for agents and users.

---

## Areas for Future Research & Weaknesses
- Standardize agent rolecards with best template analysis; mark incomplete fields for review.
- Expand glossary coverage and tag schema as new terms/processes are adopted.
- Continue mapping EFMC to PFMC and flag ambiguous/low-confidence cases for human review.
- Document existence of all relevant files, even if relevance is uncertain, for future audit.
- Track sources/context for all manifest/planning updates.
- Automated conflict resolution between agent and human edits
- Dynamic access control based on agent trust scores or recent behavior
- Integration of explainability frameworks (e.g., XAI) into documentation
- AI-driven suggestions for file organization and manifest updates
- Mapping EFMC to PFMC: Identify gaps, redundancies, and opportunities for improved workflow
- Protocols for user/agent collaboration and ambiguous decision handling
- Regular review and update of governance and manifest as project evolves

> **Note:** This is a living document. Update as new standards, procedures, or filespace changes are adopted.

---

## Audit: Recent Verification (2026-01-01)
- `PROPOSED/PFMC_MANIFEST_AND_GOVERNANCE.md`: verified — contains research notes, planned research, critical questions, and manifest fragment descriptions.
- `PROPOSED/AGENT_JARVIS/rolecards/rolecard_template.yaml`: present — best-practice rolecard template created and saved.
- `PROPOSED/github_2fa_recovery_codes_pointer.md`: expected pointer file not found during verification; manifest fragments reference `secrets_index_github_2fa_recovery.json`. If pointer is required, recreate at `PROPOSED/github_2fa_recovery_codes_pointer.md` or update `master_refs_fragment.json` to reference the correct secrets index.
- `WORK/ui_prototype/2d_viewer/data/PROPOSED/PROPOSED FILESPACE MASTER CSV 4.1.csv`: present — listed as the latest PFMC CSV.

Notes:
- The manifest fragments (`WORK/ui_prototype/2d_viewer/data/PROPOSED/fragments/master_refs_fragment.json`) include `secrets_index_github_2fa_recovery.json` in `contents` — consider aligning pointer filenames and indices for clarity.
- Tagging, glossary, and topics files were located and referenced (see `MASTER_REFERENCES/glossary.json`, `topics.json`, `functions_catalog.json`).

Action Items (recommended):
- If you want the 2FA pointer persisted in PFMC, confirm preferred filename and I will recreate it and register it in `master_refs_fragment.json`.
- I can bulk-scan PFMC for missing/incomplete rolecards and mark `incomplete_fields` for each agent.
- Continue autonomous research additions into the manifest; I can append new source notes as I find them.

- **New resources:**
	- `PROPOSED/JARVIS_PRIORITIES.md`: preliminary JARVIS priority specification (documentation, chat-logging, summaries, decision flow). See file for immediate recommendations and next steps.

- **Operational hub:**
	- `WORK/JARVIS_BRAIN_OPERATIONS/`: canonical operations folder. Contains `TRIAL_MANIFEST.json`, `task_analysis.md`, and progress artifacts. Agents MUST consult this folder for trial task assignments and progress.
	- External (user-approved) operations folder: `C:\Users\Tensh\JARVISBRAINSURGERY(OPERATIONS GOVERNANCE TRIALS)` — note: this folder is intentionally external to EFMC; use only for local trial artifacts and sensitive operations per user policy.

---
## Inventory & Findings (scan summary — 2026-01-01)

- **Core manifest/fragments discovered:**
	- `WORK/ui_prototype/2d_viewer/data/PROPOSED/fragments/master_refs_fragment.json` — lists canonical references including `glossary.json`, `functions_catalog.json`, `topics.json`, `stable_ids.json`, `data_sources_index.json`, and `secrets_index_github_2fa_recovery.json` (also references `github_2fa_recovery_codes_pointer.md`).
	- `WORK/ui_prototype/2d_viewer/data/PROPOSED/PROPOSED FILESPACE MASTER CSV 4.1.csv` — latest PFMC CSV rows reference `provenance` and `AGENT JARVIS` folders.

- **Glossary / Topics / Functions:**
	- `WORK/ui_prototype/2d_viewer/data/PROPOSED/MASTER_REFERENCES/glossary.json` (contains `agent` entries and tag schema examples).
	- `WORK/ui_prototype/2d_viewer/data/PROPOSED/MASTER_REFERENCES/topics.json` (maps `provenance` and agent-related topics to functions/tags).
	- `WORK/ui_prototype/2d_viewer/data/PROPOSED/MASTER_REFERENCES/functions_catalog.json` (has `apply_rolecard`, `create_fragment`, and other helper signatures).

- **Scripts & automation referencing provenance/agents:**
	- `WORK/ui_prototype/2d_viewer/scripts/map_efmc_to_pfmc.py` — emits `provenance` tags during EFMC→PFMC mapping.
	- `scripts/publish_snapshot.py`, `scripts/score_snapshot.py`, `scripts/export_workbook.py` — expect/validate `PROVENANCE` fields and append provenance notes.
	- `WORK/PROCEDURES/visualizations/proposed_tree.json` — large index containing many agent rolecard artifacts and agent-related docs (numerous `AGENT_ROLE_CARD_*` and `rolecard_*` entries).

- **Rolecards:**
	- `PROPOSED/AGENT_JARVIS/rolecards/rolecard_template.yaml` — present and registered in manifest (template for standardization).
	- Many rolecard-like artifacts exist under `WORK/PROCEDURES/*` (see proposed_tree visualization); consolidation recommended.

- **Secrets / 2FA pointer mismatch:**
	- `master_refs_fragment.json` includes `secrets_index_github_2fa_recovery.json` in `contents` and also lists `github_2fa_recovery_codes_pointer.md`.
	- Manifest audit earlier noted an expected pointer file; confirm desired pointer filename and whether `secrets_index_*` should be present (metadata-only) or removed if not used.

---
## Immediate Recommendations (next steps)

- Align pointer/index names: choose a canonical pointer filename (e.g., `PROPOSED/github_2fa_recovery_codes_pointer.md`) and update `WORK/ui_prototype/2d_viewer/data/PROPOSED/fragments/master_refs_fragment.json` `contents` to match.
- Consolidate rolecards: create a short script to normalize rolecards into `PROPOSED/AGENT_JARVIS/rolecards/` and mark `incomplete_fields` where metadata is missing.
- Add automated checks: extend existing `scripts/*` to validate `PROVENANCE` fields in CSVs and manifest fragments during snapshot/publish steps.
- Expand glossary/topics: add any missing agent/provenance terms found during scans to `MASTER_REFERENCES/glossary.json` and update `topics.json` mappings.
- Create an index report: generate a machine-readable `pfmc_inventory.json` (fragment) summarizing found files, owners, and gaps for automated monitoring.

---
*I will continue appending relevant notes and consolidating findings in this manifest as I scan more files and normalize rolecards. Next action (with your permission): run a rolecard-normalization pass to collect `incomplete_fields` and produce `pfmc_inventory.json`.*
