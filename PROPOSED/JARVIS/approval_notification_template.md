# Approval Notification Template

Subject: [JARVIS] Manifest Approval Required — {manifest_name}

Body:
Hello {approver},

A request to approve changes to the manifest `{manifest_name}` has been created by `{requester}` with reason:

"{reason}"

Approval ID: `{approval_id}`
Expires at: {expires_at}

To approve, run:

python scripts/manifest_approval.py approve --manifest "{manifest_name}" --actor "{approver}" --reason "{reason}" --ttl-hours 24

Or to review the request, inspect `GOV/jarvis/manifest_approvals.csv` and `GOV/jarvis/audit_manifest_changes.csv`.

Please respond at your earliest convenience.

Regards,
JARVIS Automation