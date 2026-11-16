"""Fast, dependency-free security and privacy regression checks."""

import json
import pathlib
import re
import subprocess
import unittest
from urllib.parse import urlsplit


ROOT = pathlib.Path(__file__).resolve().parents[1]


class SecurityChecks(unittest.TestCase):
    def test_no_obvious_credentials_in_tracked_files(self):
        paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        patterns = [
            re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            re.compile(rb"ghp_[A-Za-z0-9]{36}"),
            re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
            re.compile(rb"AKIA[0-9A-Z]{16}"),
        ]
        for path in filter(None, paths):
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                for pattern in patterns:
                    self.assertIsNone(pattern.search(data))

    def test_public_site_has_no_personal_email_or_unsafe_dom_sinks(self):
        for path in (ROOT / "app").glob("*"):
            if not path.is_file():
                continue
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I))
                self.assertNotIn("innerHTML", text)
                self.assertNotIn("eval(", text)
        self.assertIn("textContent", (ROOT / "app/app.js").read_text())

    def test_advisories_use_reviewed_primary_domains(self):
        data = json.loads((ROOT / "app/advisories.json").read_text())
        allowed = {"security.paloaltonetworks.com", "logging.apache.org", "access.redhat.com", "ubuntu.com"}
        for advisory in data["advisories"]:
            with self.subTest(cve=advisory["cve"]):
                self.assertIn(urlsplit(advisory["source"]).hostname, allowed)

    def test_non_root_container_and_restricted_pod(self):
        container = (ROOT / "Containerfile").read_text()
        deployment = (ROOT / "k8s/k3s/deployment.yaml").read_text()
        self.assertRegex(container, r"(?m)^USER [1-9][0-9]*$")
        self.assertIn("allowPrivilegeEscalation: false", deployment)
        self.assertIn("readOnlyRootFilesystem: true", deployment)
        self.assertIn("drop: [ALL]", deployment)


if __name__ == "__main__":
    unittest.main()
