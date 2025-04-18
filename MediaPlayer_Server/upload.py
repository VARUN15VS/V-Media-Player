import socket
import os
import threading

SERVER_HOST = ""
SERVER_PORT = 9999

f_path = r"C:\Player_Server"

def get_unique_filename(uname, f1_path):
    media_name = os.path.basename(f1_path)
    h_path = os.path.join(f_path, uname)
    file_path = os.path.join(h_path, media_name)
    #file_path = get_unique_filename(h_path, movie_name)
    base_name, extension = os.path.splitext(file_path)  # Separate name and extension
    counter = 1
    new_file_name = file_path # Start with the original file name

    while os.path.exists(os.path.join(h_path, new_file_name)):
        new_file_name = f"{base_name}_copy_{counter}{extension}"
        counter += 1

    return os.path.join(h_path, new_file_name)

def fetch_media(file_path):
    movie_name = os.path.basename(file_path)
    '''h_path = os.path.join(f_path, uname)
    file_path = os.path.join(h_path, movie_name)
    file_path = get_unique_filename(h_path, movie_name)'''

    try:    
        # Connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall(movie_name.encode())  # Send filename to server
    
        # Receive the media
        with open(file_path, "wb") as file:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                file.write(data)

        client_socket.close()
        print("Video received successfully.")

    except Exception as e:
        print(f"Error: {e}")

    # Run the fetching process in a separate thread
    #threading.Thread(target=fetch_media, daemon=True).start()