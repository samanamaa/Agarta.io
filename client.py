import socket
import threading
import json

class NetworkClient:
    def __init__(self, server_ip, name):
        self.server_ip = server_ip
        self.name = name
        self.sock = None
        self.buffer = ""
        self.state_callback = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, 5678))
        join_msg = json.dumps({"type": "join", "name": self.name}) + "\n"
        self.sock.sendall(join_msg.encode("utf-8"))
        threading.Thread(target=self.listen_thread, daemon=True).start()

    def listen_thread(self):
        while True:
            try:
                data = self.sock.recv(2048)
                if not data:
                    break

                self.buffer += data.decode("utf-8")
                while "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    msg = json.loads(line)
                    if self.state_callback:
                        self.state_callback(msg)

            except:
                break

    def send_input(self, tx, ty):
        msg = json.dumps({"type": "input", "tx": tx, "ty": ty}) + "\n"
        try:
            self.sock.sendall(msg.encode("utf-8"))
        except:
            pass