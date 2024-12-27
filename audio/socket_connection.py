import socket, os
from config.settings import Config

def connect_unix_socket():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print(f"Attempting to connect to socket at {Config.SOCKET_PATH}")

    if not os.path.exists(Config.SOCKET_PATH):
        print(f"Socket file does not exist: {Config.SOCKET_PATH}")
    else:
        try:
            sock.connect(Config.SOCKET_PATH)
            print(f"Connected to socket at {Config.SOCKET_PATH}")
        except socket.error as e:
            print(f"Error connecting to socket: {e}")
            return None

        return sock