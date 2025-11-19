import json
import socket
import threading
from . import utilities as u
import os

class ProcessCommunicator:
    """Handle JSON communication between Python processes using Unix domain sockets."""
    global_instance = None

    def __init__(self, socket_path=None):
        """Initialize communicator with optional socket path.

        Args:
            socket_path: Path to Unix domain socket. Auto-generated if None.
        """
        self.socket_path = socket_path or f"/tmp/pygs_{u.unique_id()}.sock"
        self.server_socket = None
        self.client_socket = None

    def socket_exists(self):
        """Check if the socket file exists."""
        return os.path.exists(self.socket_path)

    def start_server(self, callback):
        """Start server to receive JSON messages.

        Args:
            callback: Function called with deserialized JSON data
        """
        # Remove existing socket file
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)


        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(1)

        def accept_connections():
            while True:
                try:
                    conn, _ = self.server_socket.accept()
                    data = b""
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    if data:
                        callback(json.loads(data.decode())["shortcut"])
                    conn.close()
                except:
                    break

        thread = threading.Thread(target=accept_connections, daemon=True)
        thread.start()

    def send_json(self, data):
        """Send JSON data to server socket.

        Args:
            data: Dictionary or JSON-serializable object to send
        """
        self.client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client_socket.connect(self.socket_path)
        json_str = json.dumps(data)
        self.client_socket.sendall(json_str.encode())
        self.client_socket.close()

    def close(self):
        """Close server and client sockets."""
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()

    def cleanup(self):
        """Close sockets and remove socket file."""
        self.close()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    @staticmethod
    def get_global_communicator():
        if ProcessCommunicator.global_instance is None:
            ProcessCommunicator.global_instance = ProcessCommunicator()
        return ProcessCommunicator.global_instance