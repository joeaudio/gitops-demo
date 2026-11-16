# Design decisions

Checked 2026-11-17 against official documentation.

- **GitHub replaces GitLab.** The user asked for GitHub issues and GitHub-triggered CI. One repository carries code, issue templates, tests, and desired state.
- **k3s replaces OpenShift for this small local test.** k3s is a single-node Kubernetes cluster with a straightforward local install. It uses containerd for pods; Podman remains the local image builder and preview. [k3s quick start](https://docs.k3s.io/quick-start), [runtime](https://docs.k3s.io/advanced)
- **Argo CD performs CD.** The CI workflow publishes a versioned image and commits the desired image SHA. Argo CD reads Git and applies it. CI has no local cluster credentials. [Argo CD install](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/)
- **Tests precede publishing.** Python standard-library unit tests check advisory data; integration tests start the site and fetch its page and JSON. No third-party test dependency.
- **Issue-driven local Codex.** A joeaudio-authored issue is input to `scripts/agent-from-issue.sh`. Codex works on a branch, runs tests, and stops before publishing; a human reviews the PR. No cloud API key or unattended issue-to-code token is needed. Untrusted issue text is treated as data.
- **Minimal GitHub Action permissions.** Tests use read access; image publishing uses `packages: write`; the GitOps tag job uses `contents: write`. [GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- **Primary sources for security claims.** Advisory cards link to vendor or project advisories. Current patch levels must be checked there, not copied from a stale static summary.
