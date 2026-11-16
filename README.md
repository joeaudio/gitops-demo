# Vulnerability Drop: local GitOps showcase

A small, sourced vulnerability briefing site used to demonstrate an issue → agent → pull request → CI → container image → GitOps deployment loop.

**Site:** search and filter briefings in `app/`. Each briefing links to a primary advisory and gives defensive advice. This is an educational demo, not a live threat feed.

## What runs where

| Component | Location |
|---|---|
| Codex issue worker | This Kali desktop, started by you |
| Unit and integration tests | Locally and in GitHub Actions |
| Podman preview | This Kali desktop at `127.0.0.1:18080` |
| Container image | GitHub Container Registry (`ghcr.io`) |
| k3s and Argo CD | This Kali desktop, after setup |
| Source, issues, PRs, CI | `joeaudio/gitops-demo` on GitHub |

k3s uses its bundled containerd for pods. Podman builds and previews the same `Containerfile` locally. [k3s runtime documentation](https://docs.k3s.io/advanced)

## Quick start

```bash
cd /home/kali/gitops-demo
python3 -m unittest discover -s tests -v
podman build -t localhost/vulnerability-drop:dev .
podman run --rm --network=slirp4netns -p 127.0.0.1:18080:8080 localhost/vulnerability-drop:dev
```

Open <http://127.0.0.1:18080>. On this machine, rootless Podman requires `--network=slirp4netns` because `pasta` is not installed.

## Pipeline as code

The [GitHub Actions workflow](.github/workflows/ci.yml) runs unit and integration tests on pull requests. On a passing `main` push it builds an image tagged with the commit SHA, pushes it to GHCR, and updates the k3s Kustomize image tag in Git. Argo CD polls GitHub and reconciles the local cluster. CI never needs a kubeconfig.

See [setup](docs/SETUP.md), [pipeline decisions](docs/DECISIONS.md), and [Codex issue workflow](docs/ISSUE-WORKFLOW.md).

## Verified on this Kali machine

- Four unit and integration tests pass locally and in GitHub Actions.
- The Podman preview serves at `127.0.0.1:18080`.
- k3s and Argo CD are installed. The Application is **Synced** and **Healthy**.
- The k3s site returned HTTP 200 at `127.0.0.1:18081` through a localhost port-forward. Its JSON contains all four advisories, including the issue-driven OpenSSH briefing.
- [Issue #1](https://github.com/joeaudio/gitops-demo/issues/1) became [PR #2](https://github.com/joeaudio/gitops-demo/pull/2), passed CI, merged, published a new image, and updated the GitOps tag. The local Codex CLI hit account quota, so the active Codex session completed that sample issue.

After a reboot, k3s starts automatically. To view the deployed site again, run `sudo k3s kubectl -n vulnerability-drop port-forward --address 127.0.0.1 service/vulnerability-drop 18081:80` and open <http://127.0.0.1:18081>.
