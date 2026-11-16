# Set up the local GitOps demo

1. Create the GitHub repository `joeaudio/gitops-demo` and push this folder. The workflow uses GitHub Actions and GHCR. The image package must be **public** for the simplest local k3s pull; check the package visibility after the first successful build. If kept private, create an image pull secret in the k3s namespace instead.
2. Run `python3 -m unittest discover -s tests -v` and build a local preview with Podman as shown in the README.
3. Install a local single-node [k3s](https://docs.k3s.io/quick-start) cluster. k3s installs as a systemd service and writes its admin kubeconfig under `/etc/rancher/k3s/k3s.yaml`. Keep that file private. Do not commit it.
4. Install [Argo CD](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/) in the cluster. The GitHub repository must be readable by Argo CD. A public repository needs no repository credential; a private repository needs a read-only deploy credential.
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

## Known gates

- `k3s` and Argo CD are not yet installed.
- GitHub Actions must be enabled for the new repo.
- The GHCR package must be public, or the cluster needs a pull secret.
- If the repository remains private, Argo CD needs read-only repository access.
- If branch protection later prevents the workflow's manifest commit, switch to a bot PR for image updates.
