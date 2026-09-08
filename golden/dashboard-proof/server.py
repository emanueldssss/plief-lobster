from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse
class Handler(BaseHTTPRequestHandler):
    root = Path(__file__).parent
    def do_GET(self):
        path_name = urlparse(self.path).path
        if path_name == '/api/ok': self.send_response(200); self.end_headers(); self.wfile.write(b'ok'); return
        if path_name == '/api/fail': self.send_response(503); self.end_headers(); self.wfile.write(b'failure'); return
        path = self.root / ('index.html' if path_name == '/' else path_name.lstrip('/'))
        if not path.is_file(): self.send_response(404); self.end_headers(); return
        data = path.read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html' if path.suffix=='.html' else 'text/javascript' if path.suffix=='.js' else 'text/css'); self.end_headers(); self.wfile.write(data)
    def log_message(self, *args): pass
HTTPServer(('127.0.0.1', 4176), Handler).serve_forever()
