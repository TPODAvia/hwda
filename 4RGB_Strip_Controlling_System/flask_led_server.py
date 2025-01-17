#!/usr/bin/env python3

from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

def handle_command(r, g, b, delay, direction, action):
    print(f"Handling LED command: r={r}, g={g}, b={b}, delay={delay}, "
          f"dir={direction}, action={action}")
    # Insert your actual LED-control code here

@app.route('/home.html')
def serve_home():
    # Serve the actual HTML file from the same folder
    return send_from_directory(os.path.dirname(__file__), 'home.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    # If no 'action' parameter, just serve home.html
    if 'action' not in request.args:
        return serve_home()
    else:
        # Parse parameters from the query string
        r = int(request.args.get('red', '0'))
        g = int(request.args.get('green', '0'))
        b = int(request.args.get('blue', '0'))
        delay = int(request.args.get('delay', '10'))
        direction = int(request.args.get('dir', '1'))
        action = int(request.args.get('action', '0'))
        handle_command(r, g, b, delay, direction, action)
        return "OK\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8180, debug=False)
