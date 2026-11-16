# Issue → Codex → CI → GitOps

1. In GitHub, create an issue using **New vulnerability briefing**. Include a CVE and primary advisory URL.
2. On the Kali machine, run `cd /home/kali/gitops-demo && scripts/agent-from-issue.sh NUMBER`. The script accepts issues authored by `joeaudio`, creates a branch, and invokes the locally authenticated Codex CLI.
3. Review the agent's sources, data changes, and test output. Commit, push the branch, and open a PR with `gh pr create --fill`.
4. GitHub Actions reruns unit and integration tests. Merge only after review and a green run.
5. The `main` workflow builds the immutable image, publishes it to GHCR, and commits its SHA to the Kustomize manifest. Argo CD sees the Git change and syncs k3s.

The issue worker does not fetch an issue from someone else or grant an agent GitHub write access. Keep exploit instructions and secrets out of issue bodies. For an unattended cloud agent later, use the official [Codex GitHub Action](https://github.com/openai/codex-action) with a scoped API key, an explicit owner-only trigger, a narrow permission profile, and human PR review.
