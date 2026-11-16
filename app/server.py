"""Minimal static server for the local vulnerability briefing site."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
PUBLIC_PATHS = {"/", "/index.html", "/style.css", "/app.js", "/advisories.json"}


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _allowed(self):
        if urlsplit(self.path).path not in PUBLIC_PATHS:
            self.send_error(404)
            return False
        return True

    def do_GET(self):
        if self._allowed():
            super().do_GET()

    def do_HEAD(self):
        if self._allowed():
            super().do_HEAD()

    def list_directory(self, _path):
        self.send_error(404)
        return None

    def end_headers(self):
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), SiteHandler).serve_forever()
