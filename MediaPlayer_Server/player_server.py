import os
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
from otp_validator import extract_media_name
import socket
import requests

# Directory containing media files
MEDIA_DIRECTORY = r"C:\Player_Server"

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handles multiple requests in separate threads."""
    daemon_threads = True

class MediaServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handles GET requests to stream media files with support for range requests."""

        # Decode URL-encoded filename
        f_name = urllib.parse.unquote(self.path.lstrip('/'))
        l1 = f_name.split('/')
        f1 = l1[0]
        f2 = extract_media_name(f1, l1[1])
        f1_path = os.path.join(MEDIA_DIRECTORY, f1)
        file_path = os.path.join(f1_path, f2)

        print(f"Requested file: {file_path}")

        # Check if file exists
        if not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return

        # Get MIME type of file
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Get file size
        file_size = os.path.getsize(file_path)

        # Check if the client requested a specific byte range
        range_header = self.headers.get("Range")
        if range_header:
            self.send_response(206)  # Partial Content
            byte1, byte2 = self.parse_range(range_header, file_size)
            self.send_header("Content-Range", f"bytes {byte1}-{byte2}/{file_size}")
        else:
            self.send_response(200)  # Full Content
            byte1, byte2 = 0, file_size - 1

        # Send headers
        self.send_header("Content-Type", mime_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(byte2 - byte1 + 1))
        self.end_headers()

        # Stream file in chunks to prevent buffer overflow
        CHUNK_SIZE = 1024 * 1024  # 1MB
        try:
            with open(file_path, "rb") as file:
                file.seek(byte1)
                while byte1 <= byte2:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()  # Force flush to avoid buffer overflow
                    byte1 += len(chunk)
        except BrokenPipeError:
            print("[INFO] Client disconnected.")

    def parse_range(self, range_header, file_size):
        """Parses the range header and returns byte range."""
        range_str = range_header.split("=")[1]
        byte1, byte2 = range_str.split("-")

        byte1 = int(byte1) if byte1 else 0
        byte2 = int(byte2) if byte2 else file_size - 1

        return byte1, byte2

def get_ip_addresses():
    # Get Local IP (Inside Network)
    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip

def run_server():
    """Starts the HTTP server for streaming media files."""
    local_ip = str(get_ip_addresses())
    server_address = (local_ip, 8000)
    httpd = ThreadedHTTPServer(server_address, MediaServer)
    print("Server started at http://{local_ip}:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    threading.Thread(target = run_server(), daemon=True).start()