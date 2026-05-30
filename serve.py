#!/usr/bin/env python3
"""Simple HTTP server for AXTEA HMI"""
import http.server
import socketserver
import os
from pathlib import Path

os.chdir(Path(__file__).parent)

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # No cache
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")

PORT = 8000
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"✅ Server running at http://localhost:{PORT}/hmi/index.html")
    print(f"✅ External: http://0.0.0.0:{PORT}/hmi/index.html")
    print(f"\nPress Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Stopped")
