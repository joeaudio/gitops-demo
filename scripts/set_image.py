import pathlib
import re
import sys

if len(sys.argv) != 2 or not re.fullmatch(r"ghcr\.io/[a-z0-9_.-]+/[a-z0-9_.-]+:[0-9a-f]{40}", sys.argv[1]):
    raise SystemExit("Expected GHCR image tagged with a 40-character Git SHA")

path = pathlib.Path(__file__).resolve().parents[1] / "k8s/k3s/kustomization.yaml"
content = path.read_text()
content, count = re.subn(r"(?m)^(\s*newTag:) .+$", lambda match: match.group(1) + " " + sys.argv[1].rsplit(":", 1)[1], content)
if count != 1:
    raise SystemExit("Expected exactly one newTag")
path.write_text(content)
