"""Local preview server.

Vercel is configured with `cleanUrls`, so `/vision` serves `vision.html` in
production and every link on the site is written without the extension. Plain
`python -m http.server` would 404 on those, so this adds the same rewrite.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class CleanURLHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        local = super().translate_path(path)
        if not os.path.exists(local) and not os.path.splitext(local)[1]:
            html = local.rstrip("/\\") + ".html"
            if os.path.isfile(html):
                return html
        return local


if __name__ == "__main__":
    print(f"Serving on http://localhost:{PORT}")
    HTTPServer(("127.0.0.1", PORT), CleanURLHandler).serve_forever()
