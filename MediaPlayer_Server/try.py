import os
import mimetypes
import threading
import mysql.connector
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import urllib.parse
from socketserver import ThreadingMixIn
from database import tcp_server
from player_server import run_server
#from upload import run_server_upload

def broadcast_ip():
    """Broadcast the server's IP so clients can discover it."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server_ip = socket.gethostbyname(socket.gethostname())  # Get local IP
    port = 5000

    while True:
        udp_socket.sendto(server_ip.encode(), ("<broadcast>", port))

# ✅ Start HTTP & TCP Servers
def start_servers():
    threading.Thread(target=broadcast_ip, daemon=True).start()
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=tcp_server, daemon=True).start()
    #threading.Thread(target=run_server_upload, daemon=True).start()

if __name__ == "__main__":
    start_servers()
    while True:
        pass  # Keep main thread alive