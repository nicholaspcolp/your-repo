# GitHub Permissions & Automation Plan

Purpose: document recommended immediate and long-term approaches for enabling PR creation and CI automation with least privilege.

Immediate (short-term): use a fine-grained Personal Access Token (PAT)
- Create a **fine-grained PAT** and select **Only select repositories** → choose `nicholaspcolp/your-repo`.
- Set repository permissions:
  - **Contents**: Read & Write
  - **Pull requests**: Read & Write
  - (Optional) **Workflows**: Read & Write if you need to manage Actions
- Set a short expiration (30–90 days) and copy the token immediately.
- Authorize the token for SAML SSO if your org requires it.
- Store token securely (use `scripts/store_github_token.ps1`) and verify with `scripts/check_github_token.py`.

Validation checklist (run locally):
- curl -I -H "Authorization: token $PAT" https://api.github.com/ should return 200 OK
- curl -H "Authorization: token $PAT" https://api.github.com/user should return your user
- python scripts/check_github_token.py --repo nicholaspcolp/your-repo will report whether the token can access the repository and the permissions it sees

Long-term (recommended): GitHub App or Action-based automation
- For production automation, create a **GitHub App** and install it on the repo(s) you manage. Benefits:
  - Granular per-repo permissions
  - Short-lived installation tokens
  - Better auditability and least-privilege model
- Alternatively, embed auto-merge and apply logic in a GitHub Action using `GITHUB_TOKEN` (ephemeral) and repository secrets for additional steps.

Operational steps to migrate:
1. Create minimal PAT now to unblock PR creation.
2. Design a GitHub App with required permissions (pull requests: write, checks: read/write, contents: read/write) and a small service to mint installation tokens (or use an Action). 
3. Update `scripts/auto_merge_pr.py` to support GitHub App authentication (or move auto-merge logic into Actions).

Notes about SSO & orgs
- If your organization enforces SAML SSO, newly created PATs must be authorized for the org via the SSO page.
- If you're a fork or your repo is in an organization, ensure the token is scoped to the correct repository or authorized by the organization.

Next steps (I will do):
- Provide `scripts/check_github_token.py` to validate token access and permissions. ✅
- Attempt to create PR via API once a valid token is stored and verified. ✅
- If API creation is still blocked, document required devops/owner actions and propose a GitHub App scaffold. ✅
