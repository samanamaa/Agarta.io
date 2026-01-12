import socket
import threading
import json
import time

def discover_servers(timeout=2.0):
    servers = []
    seen_ips = set()
    discovery_port = 5679
    
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(0.1)
    
    broadcast_msg = "AGARTA_DISCOVERY"
    # pokus o broadcast na lokálnu podsieť aj na 255.255.255.255
    local_ip = socket.gethostbyname(socket.gethostname())
    try:
        parts = local_ip.split(".")
        if len(parts) == 4:
            subnet_broadcast = ".".join(parts[:3] + ["255"])
            udp_sock.sendto(broadcast_msg.encode("utf-8"), (subnet_broadcast, discovery_port))
    except:
        pass
    udp_sock.sendto(broadcast_msg.encode("utf-8"), ("255.255.255.255", discovery_port))
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data, addr = udp_sock.recvfrom(1024)
            msg = json.loads(data.decode("utf-8"))
            if msg.get("type") == "server_info":
                server_ip = msg.get("ip", addr[0])
                if server_ip not in seen_ips:
                    seen_ips.add(server_ip)
                    servers.append({
                        "ip": server_ip,
                        "port": msg.get("port", 5678),
                        "players": msg.get("players", 0)
                    })
        except socket.timeout:
            continue
        except:
            continue
    
    udp_sock.close()
    return servers


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
    
    def send_split(self):
        msg = json.dumps({"type": "split"}) + "\n"
        try:
            self.sock.sendall(msg.encode("utf-8"))
        except:
            pass