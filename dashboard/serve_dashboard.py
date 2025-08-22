#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard
"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "/home/karan/startup/joborra/dashboard"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving dashboard at http://localhost:{PORT}")
        print(f"Dashboard directory: {DIRECTORY}")
        httpd.serve_forever()
