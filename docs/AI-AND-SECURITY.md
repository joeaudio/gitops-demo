# AI and security controls

## What is enforced

- Issues are task input, not trusted instructions. The local worker accepts only `joeaudio`-authored issues, works on a branch, and does not push or deploy. A person reviews the PR.
- Each advisory records a primary source URL. The test suite checks a reviewed set of source domains, minimum useful content, uniqueness, and a valid CVE identifier. A reviewer must still verify the actual claim and current remediation.
- Unit and HTTP integration tests, a privacy and secure-defaults test, and an image vulnerability scan run on PRs and main. The image job depends on both test jobs.
- The site uses `textContent` for advisory data, a restrictive Content Security Policy, no external client scripts, a non-root container, and a read-only pod filesystem.
- CI has no kubeconfig. GitHub token rights are limited per job. Argo CD reads the public repository and reconciles Git state.
- Generated slide assets contain no passwords. Argo CD credentials remain only in the local cluster and in the user's private login session.

## Limits and review duties

The checks cannot prove that software has no vulnerabilities, that an AI answer is factually correct, or that no personal data exists in every possible file. Trivy checks known CVEs in its database at scan time; the fast secret and PII tests use patterns and can miss other formats. A reviewer checks the advisory against its source, considers privacy, and inspects the PR diff before merge. New source domains require explicit test updates and review.

For a production ROSA rollout, add organization-specific threat modelling, SSO/RBAC, signed image policy, secret management, network policy, monitoring and incident response. This local demo does not claim those controls are deployed.
