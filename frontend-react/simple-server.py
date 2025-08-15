#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

# Change to the dist directory
os.chdir('dist')

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        # Serve index.html for all routes (React Router)
        if not os.path.exists(self.path[1:]) and not self.path.startswith('/assets/'):
            self.path = '/index.html'
        return super().do_GET()

print(f"""
🚀 ESG Compass React App Server Starting...

📱 Access the app in your browser:
   http://localhost:{PORT}
   http://127.0.0.1:{PORT}

🌐 For Windows access, try:
   - Open Windows Command Prompt as Administrator
   - Run: netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport={PORT} connectaddress=127.0.0.1
   - Then access: http://localhost:3000

Press Ctrl+C to stop the server
""")

try:
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n👋 Server stopped!")
    sys.exit(0)