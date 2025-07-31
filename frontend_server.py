#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend
Serves the frontend files and handles CORS for API requests
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_frontend_server(port=8000):
    """Start the frontend server"""
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory '{frontend_dir}' not found!")
        return
    
    os.chdir(frontend_dir)
    
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print("=" * 60)
            print("         FRONTEND SERVER")
            print("=" * 60)
            print(f"Server starting on port {port}")
            print(f"Frontend URL: http://localhost:{port}")
            print(f"API URL: http://localhost:5000")
            print("=" * 60)
            print("Make sure the API server is running on port 5000!")
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            print(f"Error: Port {port} is already in use!")
            print("Try using a different port or stop the service using that port.")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    
    start_frontend_server(port)
