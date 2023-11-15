import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Define the directory to serve
directory = os.path.dirname(os.path.realpath(__file__))

# Define the port
port = 8000

# Change to the directory to be served
os.chdir(directory)

# Start the HTTP server
httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
print(f"Server running at http://localhost:{port}/")

# Open the default web browser
webbrowser.open(f'http://localhost:{port}')

# Start serving
httpd.serve_forever()
