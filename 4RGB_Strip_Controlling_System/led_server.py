#!/usr/bin/env python3

import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8180

# Suppose we have some function that does the LED handling
def handle_command(r, g, b, delay, direction, action):
    print(f"Handling LED command: r={r}, g={g}, b={b}, delay={delay}, "
          f"dir={direction}, action={action}")
    # Insert your actual LED strip code here (e.g. rpi_ws281x, etc.)

class SimpleLEDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests:
          - If 'action' is not in the query string, serve home.html.
          - Otherwise, parse the query parameters, call handle_command(), and return some response.
        """
        parsed_url = urllib.parse.urlparse(self.path)
        query_dict = urllib.parse.parse_qs(parsed_url.query)

        # If no parameters or no "action" param, just serve home.html
        if not query_dict.get('action'):
            # Attempt to serve 'home.html' from the same folder
            try:
                with open("/home/pi/hwda/4RGB_Strip_Controlling_System/home.html", "r", encoding='utf-8') as f:
                    html_content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "home.html not found")
        else:
            # We have parameters, so let's parse them:
            try:
                r = int(query_dict.get('red', ['0'])[0])
                g = int(query_dict.get('green', ['0'])[0])
                b = int(query_dict.get('blue', ['0'])[0])
                delay = int(query_dict.get('delay', ['10'])[0])
                direction = int(query_dict.get('dir', ['1'])[0])
                action = int(query_dict.get('action', ['0'])[0])
                # Now call the LED-handling logic:
                handle_command(r, g, b, delay, direction, action)
                # Return a simple OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"OK\n")
            except Exception as ex:
                self.send_error(400, f"Bad request: {str(ex)}")

    def do_POST(self):
        """
        If you want to accept POST requests (like a form submission or JavaScript fetch),
        you can do similar logic here, reading the request body.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        # Example: parse the body if it's form-encoded
        query_dict = urllib.parse.parse_qs(post_body)

        # Then do the same as do_GET basically...
        # or reuse the same handle_command(...) logic

        # Return something
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST received.\n")


if __name__ == '__main__':
    try:
        server = HTTPServer((HOST, PORT), SimpleLEDHandler)
        print(f"Starting server at http://{HOST}:{PORT}...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
        sys.exit(0)
