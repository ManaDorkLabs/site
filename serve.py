"""Local preview server.

Rebuilds the site from content/pages/ before serving each page, so editing a
content file and refreshing the browser is enough to see the change.

Vercel is configured with `cleanUrls`, so `/vision` serves `vision.html` in
production and every link on the site is written without the extension. Plain
`python -m http.server` would 404 on those, so this adds the same rewrite.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

import build

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class SiteHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        # Cheap enough to redo on every page view, and it means a stale build
        # can never be what you are looking at.
        if not os.path.splitext(self.path)[1] or self.path.endswith(".html"):
            try:
                build.build()
            except Exception as exc:  # a typo in a content file, usually
                self.send_error(500, "Build failed", str(exc))
                return None
        return super().send_head()

    def translate_path(self, path):
        local = super().translate_path(path)
        if not os.path.exists(local) and not os.path.splitext(local)[1]:
            html = local.rstrip("/\\") + ".html"
            if os.path.isfile(html):
                return html
        return local


if __name__ == "__main__":
    build.build()
    print(f"Serving on http://localhost:{PORT}")
    HTTPServer(("127.0.0.1", PORT), SiteHandler).serve_forever()
