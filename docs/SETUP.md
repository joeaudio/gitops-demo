# Set up the local GitOps demo

1. Clone the public [GitHub repository](https://github.com/joeaudio/gitops-demo). The workflow uses GitHub Actions and GHCR. The image package is anonymously pullable; a private fork needs an image pull secret.
2. Run `python3 -m unittest discover -s tests -v` and build a local preview with Podman as shown in the README.
3. Install a local single-node [k3s](https://docs.k3s.io/quick-start) cluster. k3s installs as a systemd service and writes its admin kubeconfig under `/etc/rancher/k3s/k3s.yaml`. Keep that file private. Do not commit it.
4. Install [Argo CD](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/) in the cluster. On this machine, the large ApplicationSet CRD required server-side apply: `sudo k3s kubectl create namespace argocd`, then `sudo k3s kubectl apply --server-side -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`. A private Git fork needs read-only repository access.
5. Once GHCR contains the first image and `k8s/k3s/kustomization.yaml` names its SHA, apply `k8s/k3s/application.yaml` to Argo CD. Inspect sync state and port-forward the service for a browser demonstration.
6. Create a GitHub issue with the advisory template. Run the local Codex issue worker, review its branch, open a PR, and merge after CI passes. The next `main` run publishes the image and changes the desired tag. Watch Argo CD sync it.

Commands after k3s and Argo CD are installed:

```bash
sudo k3s kubectl get nodes
sudo k3s kubectl -n argocd apply -f k8s/k3s/application.yaml
sudo k3s kubectl -n vulnerability-drop get deployment,pods,service
sudo k3s kubectl -n vulnerability-drop port-forward service/vulnerability-drop 18081:80
```

Open <http://127.0.0.1:18081>. The GitHub Actions pipeline does **not** connect to the Kali machine; Argo CD makes outbound GitHub requests from the cluster.

## Current machine

- k3s `v1.37.2+k3s1` is installed as a systemd service on this Kali host. Argo CD `v3.6.1` is installed in `argocd`; the Application reached `Synced` and `Healthy`.
- GitHub Actions passed the initial build and the sample issue PR. GHCR's exact SHA image returned HTTP 200 to an anonymous pull token.
- The local Codex CLI returned `Quota exceeded` on sample issue #1. The active Codex session completed PR #2 instead. Once CLI quota is available, `scripts/agent-from-issue.sh NUMBER` can run the same process locally.
- The deployed page returned HTTP 200 through localhost port 18081, and `/advisories.json` contained all four briefings. Restart the port-forward after reboot or terminal closure.
- If branch protection later prevents the workflow's manifest commit, switch to a bot PR for image updates.
- If branch protection later prevents the workflow's manifest commit, switch to a bot PR for image updates.
