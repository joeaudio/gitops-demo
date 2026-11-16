# Workflow and presentation notes

The [HTML](slides/gitops-security-briefing.html), [PDF](slides/gitops-security-briefing.pdf), and [editable PowerPoint](slides/gitops-security-briefing.pptx) share one source: `scripts/build_slides.py`.

```mermaid
flowchart LR
  I[GitHub issue] --> A[Local Codex branch]
  A --> P[Human-reviewed PR]
  P --> T[Unit + integration tests]
  P --> S[Privacy checks + image CVE scan]
  T --> B[Publish SHA image]
  S --> B
  B --> G[Commit image tag to Git]
  G --> C[Argo CD reads Git]
  C --> K[k3s now / ROSA later]
```

```mermaid
flowchart TB
  subgraph GitHub
    PR[Reviewed PR] --> CI[Scoped CI token]
    CI --> GHCR[Container registry]
    CI --> DESIRED[Desired state in Git]
  end
  subgraph Cluster
    ARGO[Argo CD] --> APP[Application namespace]
  end
  DESIRED -->|outbound Git read| ARGO
  GHCR -->|image pull| APP
```

## ROSA adoption path

The local cluster is k3s; ROSA is a proposed next environment. Install the supported Red Hat OpenShift GitOps Operator, create a ROSA-specific Kustomize overlay and Route, and validate namespace permissions, SCC admission, image access, identity, and monitoring before a pilot. Keep the issue → review → CI → immutable image → Git desired state loop. [Red Hat OpenShift GitOps installation](https://docs.redhat.com/en/documentation/red_hat_openshift_gitops/1.21/html/installing_gitops/installing-openshift-gitops).

## Rebuild slides

Use Python 3.12+ and a virtual environment. `pip install -r requirements-slides.txt`, then `python scripts/build_slides.py`. The generated files are self-contained for viewing offline. No credential is embedded in the deck.
