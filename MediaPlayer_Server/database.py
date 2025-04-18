import socket
import json
import threading
import mysql.connector
import otp_validator
import os
from upload import fetch_media, get_unique_filename
import upload
import shutil
from player_server import get_ip_addresses

f_path = r"C:\Player_Server"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pass123",
    database="v_player"
)
cursor = db.cursor()

def handle_client(client_socket, addr):
    """Handle communication with a single client."""
    print(f"Connection from {addr}")

    try:
        # Receive data from client
        data = client_socket.recv(1024).decode()
        if not data:
            client_socket.close()
            return
        
        request_type, *args = data.split('|')

        if request_type == "login":
            user_name, password = args

            # Check if the username and password are correct
            cursor.execute("SELECT COUNT(*) FROM login WHERE user_name=%s AND password=%s", (user_name, password))
            if cursor.fetchone()[0] == 1:
                # If login is successful, fetch the folder size
                total_size = 0
                folder_name = user_name
                full_path = os.path.join(f_path, folder_name)
                for dirpath, dirnames, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(file_path)
                total_size_gb = total_size / (1024 * 1024 * 1024)
                size_left = 5.0 - float(total_size_gb)
                size_left = round(size_left, 3)
                size_left = str(size_left)
                client_socket.send(size_left.encode())
            else:
                # If login fails, send a failure message
                client_socket.send("-1".encode())

        elif request_type == "upload":
            uname, f1_path, host_ip = args
            upload.SERVER_HOST = host_ip
            path = ""
            try:
                path = get_unique_filename(uname, f1_path)
                client_socket.send(path.encode())
            except Exception as e:
                client_socket.send("1".encode())
            finally:
                threading.Thread(target=fetch_media, args=(path, ), daemon=True).start()

        elif request_type == "add_movie":
            uname, mname, description, filename = args
    
            # Retrieve user id from login table based on user_name
            cursor.execute("SELECT id FROM login WHERE user_name=%s", (uname,))
            uid = cursor.fetchone()
    
            # Check if the user exists, and if so, extract the user ID
            if uid:
                user_id = uid[0]  # Extract the first element from the tuple
        
                # Insert movie details into the movie table
                cursor.execute(
                    "INSERT INTO movie (id, user_name, movie_name, description, folder, file_name) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, uname, mname, description, uname, filename)
                )
                db.commit()
                print("Movie added successfully.")
                client_socket.send("0".encode())
            else:
                print("User not found.")
                client_socket.send("1".encode())

        elif request_type == "delete_movie":
            uname,mname,description = args
            cursor.execute("SELECT COUNT(*) FROM movie where user_name=%s and movie_name=%s", (uname, mname,))
            if cursor.fetchone()[0]==1:
                cursor.execute("select file_name from movie where user_name=%s and movie_name=%s", (uname, mname, ))
                f = f = cursor.fetchone()
                filename = str(f[0])
                cursor.execute("DELETE FROM movie where user_name=%s and movie_name=%s", (uname,mname,))
                db.commit()
            h_path = os.path.join(f_path, uname)
            full_path = os.path.join(h_path, filename)
            print(full_path)
            os.remove(full_path)
            client_socket.send("0".encode())

        elif request_type == "movie_list":
            user_name, password = args
            cursor.execute("SELECT movie_name, description FROM movie WHERE user_name=%s", (user_name,))
            movie_data = cursor.fetchall()

            # Create a list of dictionaries with movie_name and description
            movies_list = [{"movie_name": row[0], "description": row[1]} for row in movie_data]

            # Convert the list to JSON format
            response = json.dumps({"movies": movies_list})

            # Send the response back to the client with a success message
            client_socket.send(f"SUCCESS|{response}".encode())

        elif request_type == "file_size":
                user_name, password = args
                
                total_size = 0
                folder_name = user_name
                full_path = os.path.join(f_path, folder_name)
                for dirpath, dirnames, filenames in os.walk(full_path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(file_path)
                total_size_gb = total_size / (1024 * 1024 * 1024)
                size_left = 5.0 - float(total_size_gb)
                size_left = round(size_left, 3)
                size_left = str(size_left)
                client_socket.send(size_left.encode())

        elif request_type == "check":
            user_name, movie_name = args
            cursor.execute("SELECT COUNT(*) from movie where user_name=%s and movie_name=%s", (user_name, movie_name,))
            if cursor.fetchone()[0] == 0:
                client_socket.send("0".encode())
            else:
                client_socket.send("1".encode())

        elif request_type == "register":
            uname, fname, lname, email, pno, password = args
            cursor.execute("SELECT COUNT(*) FROM login WHERE email=%s", (email,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT COUNT(*) FROM login WHERE user_name=%s", (uname,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("SELECT user_id FROM id_table FOR UPDATE")
                    uid = cursor.fetchone()
                    if uid:
                        user_id = int(uid[0]) + 1
                        cursor.execute("UPDATE id_table SET user_id = %s", (user_id,))
                        cursor.execute("""INSERT INTO login (id, user_name, f_name, l_name, email, phone_no, password) 
                                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user_id, uname, fname, lname, email, pno, password))
                        db.commit()
                        client_socket.send("0".encode())
                    else:
                        client_socket.send("1".encode())
                else:
                    client_socket.send("2".encode())
            else:
                client_socket.send("3".encode())

        elif request_type == "email_verification":
            to_email = args[0]
            r = otp_validator.check_existing_email(to_email)
            client_socket.send(r.encode())

        elif request_type == "direct_otp_mail":
            to_email = args[0]
            r = otp_validator.otp_verification(to_email)
            client_socket.send(r.encode())

        elif request_type == "email_otp_verification":
            to_email, otp = args
            r = otp_validator.otp_verification_check(to_email, otp)
            client_socket.send(r.encode())

        elif request_type == 'check_username':
            uname = args[0].strip()  # Ensure there are no leading/trailing spaces
            if not uname:  # If username is empty after stripping, handle the error
                client_socket.send('2'.encode())  # Send a failure code (e.g., '2' for invalid username)
                return

            # Execute the query to check if the username already exists
            cursor.execute("SELECT COUNT(*) FROM login WHERE user_name=%s", (uname,))
            result = cursor.fetchone()
            print(result)

            if result and result[0] == 0:
                # Username doesn't exist, it's available
                client_socket.send('0'.encode())  # Send response '0' indicating username is available
            else:
                # Username already exists
                client_socket.send('1'.encode())  # Send response '1' indicating username is taken

        elif request_type == 'final_mail':
            email, uname = args
            result = otp_validator.thank_you_mail(email, uname)
            client_socket.send(result.encode())
            folder_name = uname
            full_path = os.path.join(f_path, folder_name)
            os.makedirs(full_path, exist_ok=True)

        elif request_type == "delete_mail":
            uname, password = args
            to_email = ""
            cursor.execute("Select email from login where user_name=%s and password=%s", (uname, password, ))
            to_email = cursor.fetchone()[0]
            r1 = otp_validator.delete_otp_verification(to_email)
            client_socket.send(to_email.encode())

        elif request_type == "delete_account":
            uname, password = args
            path = os.path.join(f_path, uname)
            shutil.rmtree(path, ignore_errors=True)
            cursor.execute("Delete from movie where user_name=%s", (uname, ))
            cursor.execute("Delete from login where user_name=%s and password=%s", (uname, password, ))
            try:
                db.commit()
                client_socket.send("0".encode())
            except Exception as e:
                client_socket.send("1".encode())

        elif request_type == "change_password":
            email ,new_password = args
            cursor.execute("Update login set password=%s where email=%s", (new_password, email, ))
            db.commit()
            client_socket.send("0".encode())

        elif request_type == "get_uname":
            email = args[0]
            result = "-1015101051"
            cursor.execute("Select user_name from login where email=%s", (email, ))
            result = cursor.fetchone()[0]
            client_socket.send(result.encode())

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        client_socket.send("FAIL|Database error occurred".encode())
    except Exception as e:
        print(f"Error: {e}")
        client_socket.send("FAIL|An error occurred".encode())
    finally:
        client_socket.close()

def tcp_server():
    """TCP Server for handling clients from both local and external networks."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_ip = get_ip_addresses()  # Accept connections from anywhere
    port = 9000

    server_socket.bind((server_ip, port))
    server_socket.listen(5)
    print(f"TCP Server started on {server_ip}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    tcp_server()
