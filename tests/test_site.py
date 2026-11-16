import http.server
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "app"


class AdvisoryUnitTests(unittest.TestCase):
    def test_advisories_are_unique_sourced_and_actionable(self):
        data = json.loads((APP / "advisories.json").read_text())
        self.assertGreaterEqual(len(data["advisories"]), 3)
        ids = set()
        for item in data["advisories"]:
            with self.subTest(cve=item["cve"]):
                self.assertRegex(item["cve"], r"^CVE-\d{4}-\d{4,}$")
                self.assertNotIn(item["cve"], ids)
                ids.add(item["cve"])
                self.assertIn(item["severity"], {"critical", "high"})
                self.assertGreater(len(item["summary"]), 40)
                self.assertGreater(len(item["action"]), 40)
                self.assertTrue(item["source"].startswith("https://"))

    def test_image_tag_updater(self):
        original = (ROOT / "k8s/k3s/kustomization.yaml").read_text()
        with tempfile.TemporaryDirectory() as temporary:
            script = pathlib.Path(temporary) / "scripts" / "set_image.py"
            script.parent.mkdir()
            script.write_text((ROOT / "scripts/set_image.py").read_text())
            manifest = pathlib.Path(temporary) / "k8s/k3s/kustomization.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(original)
            sha = "a" * 40
            subprocess.run([sys.executable, str(script), f"ghcr.io/joeaudio/gitops-demo:{sha}"], check=True)
            self.assertIn("newTag: " + sha, manifest.read_text())


class SiteIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("site_server", APP / "server.py")
        site_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(site_server)
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), site_server.SiteHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_homepage_serves_interface(self):
        with urllib.request.urlopen(self.base + "/") as response:
            body = response.read().decode()
            self.assertEqual(response.status, 200)
        self.assertIn("Vulnerability Drop", body)
        self.assertIn('src="/app.js"', body)
        with urllib.request.urlopen(self.base + "/app.js") as script:
            self.assertIn("advisories.json", script.read().decode())
        self.assertIn("default-src 'none'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_advisories_are_served_as_json(self):
        with urllib.request.urlopen(self.base + "/advisories.json") as response:
            data = json.load(response)
            self.assertEqual(response.status, 200)
        self.assertTrue(any(item["cve"] == "CVE-2024-3400" for item in data["advisories"]))

    def test_hidden_files_are_not_served(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(self.base + "/server.py")
        self.assertEqual(error.exception.code, 404)
        error.exception.close()


if __name__ == "__main__":
    unittest.main()
