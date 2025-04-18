import socket
import json
import os
from ftpretty import ftpretty
import threading
import time

UPLOADED = 0

B_IP = ""

def discover_server():
    """Discover the server IP address using UDP broadcast."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    udp_socket.bind(("", 5000))  # Listen on all available interfaces

    print("Listening for server broadcast...")
    server_ip, _ = udp_socket.recvfrom(1024)  # Get the first broadcasted IP
    return server_ip.decode()

def get_ip_addresses():
    # Get Local IP (Inside Network)
    local_ip = socket.gethostbyname(socket.gethostname())
    return local_ip

def send_request(request_type, *args):
    """Send a request to the server and return the server's response."""
    global B_IP
    server_ip = str(B_IP)
    server_port = 9000  # TCP server port
    
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))  # Connect to the server

    # Prepare the data in the expected format
    request_data = f"{request_type}|{'|'.join(args)}"

    # Send the request to the server
    client_socket.send(request_data.encode())

    # Receive the response from the server
    response = client_socket.recv(1024).decode()

    # Close the connection
    client_socket.close()

    return response

def movie_list_request(request_type, *args):
    """Send a request to the server and return the server's response."""
    global B_IP
    server_ip = str(B_IP)
    server_port = 9000  # TCP server port
    
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))  # Connect to the server

    # Prepare the data in the expected format
    request_data = f"{request_type}|{'|'.join(args)}"

    # Send the request to the server
    client_socket.send(request_data.encode())

    # Receive the response from the server
    response = client_socket.recv(1024).decode()
    
    # Creating dictionary
    mlist = {}

    # Clear the mlist dictionary to ensure it's empty before processing
    mlist.clear()

    # Now, handle the response
    if response.startswith("SUCCESS|"):
        # Extract the JSON part after "SUCCESS|"
        json_data = response.split("|", 1)[1]

        try:
            # Parse the JSON data
            data = json.loads(json_data)

            # Check if 'movies' key is in the response
            if "movies" in data:
                movies_list = data["movies"]
                print("Movies received from server:")

                # Loop through the movies and populate mlist
                for movie in movies_list:
                    movie_name = movie["movie_name"]
                    description = movie["description"]
                    print(f"Movie Name: {movie_name}\nDescription: {description}\n")

                    # Add the movie_name and description to the mlist dictionary
                    mlist[movie_name] = description
                        
            else:
                print("No movies found for this user.")
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
    else:
        print("Login failed or unknown response received.")

    # Close the connection
    client_socket.close()

    # Return the mlist (which contains movie_name : description pairs, or is empty)
    return mlist


def handle_client(client_socket, file_path):
    """Handle client request and stream the requested media."""
    global UPLOADED  

    try:
        filename = client_socket.recv(1024).decode()  
        print(f"Requested file: {filename}")

        if os.path.exists(file_path):  
            file_size = os.path.getsize(file_path)  
            sent_size = 0  

            print(f"Streaming file: {file_path}")
            with open(file_path, "rb") as file:
                while sent_size < file_size:
                    data = file.read(1024 * 64)  # Use 64 KB buffer instead of 4 KB
                    if not data:
                        break
                    
                    client_socket.sendall(data)  
                    sent_size += len(data)  

                    # Update UPLOADED percentage
                    UPLOADED = (sent_size / file_size) * 100

            print("File send complete.")
            UPLOADED = 100  

        else:
            print("File not found.")
            client_socket.sendall(b"ERROR: File not found")  

    except Exception as e:
        print(f"Error handling client: {e}")
    
    finally:
        client_socket.close()
        print("Client disconnected.")

def start_server(file_path):
    HOST = str(get_ip_addresses())
    PORT = 9999
    """Start the server and listen for one incoming connection."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    # Accept a single client connection (removes while True loop)
    client_socket, addr = server_socket.accept()
    print(f"New connection from {addr}")

    # Handle the client in a new thread
    client_thread = threading.Thread(target=handle_client, args=(client_socket, file_path))
    client_thread.start()

    # Optionally, wait for the thread to finish before closing server
    client_thread.join()

    print("Server finished handling the client.")
    server_socket.close()  # Close server socket after handling one client
