import socket
import threading
import json
import time
import math
import random

WORLD_W, WORLD_H = 2000, 1400
TICK_RATE = 60
NUM_FOOD = 150

players = {}
foods = []
client_sockets = []


def mass_to_radius(m):
    return int(math.sqrt(m) * 3) + 4


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def spawn_food():
    foods.clear()
    for _ in range(NUM_FOOD):
        foods.append({
            "x": random.uniform(0, WORLD_W),
            "y": random.uniform(0, WORLD_H),
            "mass": 1
        })


spawn_food()


def broadcast(msg):
    msg = msg + "\n"
    dead = []
    for s in client_sockets:
        try:
            s.sendall(msg.encode("utf-8"))
        except:
            dead.append(s)

    for d in dead:
        client_sockets.remove(d)


def handle_client(sock, addr):
    pid = None
    buffer = ""

    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break

            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)

                if msg["type"] == "join":
                    pid = f"{addr[0]}_{addr[1]}"

                    players[pid] = {
                        "id": pid,
                        "name": msg["name"],
                        "x": random.uniform(0, WORLD_W),
                        "y": random.uniform(0, WORLD_H),
                        "mass": 16,
                        "tx": 0,
                        "ty": 0
                    }

                    print(f"{pid} connected")

                    # --- SEND WELCOME ---
                    welcome_msg = json.dumps({
                        "type": "welcome",
                        "id": pid,
                        "world": [WORLD_W, WORLD_H]
                    }) + "\n"

                    sock.sendall(welcome_msg.encode("utf-8"))

                elif msg["type"] == "input" and pid in players:
                    players[pid]["tx"] = msg["tx"]
                    players[pid]["ty"] = msg["ty"]

    except:
        pass

    if pid in players:
        print(f"{pid} disconnected")
        del players[pid]

    sock.close()


def game_loop():
    last = time.time()

    while True:
        now = time.time()
        dt = now - last
        if dt < 1 / TICK_RATE:
            time.sleep(0.001)
            continue

        last = now

        # --- MOVE PLAYERS ---
        for p in players.values():
            dx = p["tx"] - p["x"]
            dy = p["ty"] - p["y"]
            d = math.hypot(dx, dy)

            if d > 1:
                speed = 350 / (1 + mass_to_radius(p["mass"]) / 25)
                p["x"] += (dx / d) * speed * dt
                p["y"] += (dy / d) * speed * dt

                p["x"] = max(0, min(WORLD_W, p["x"]))
                p["y"] = max(0, min(WORLD_H, p["y"]))

        # --- FOOD COLLISIONS ---
        eaten = []
        for f in foods:
            for p in players.values():
                if dist((p["x"], p["y"]), (f["x"], f["y"])) < mass_to_radius(p["mass"]) + 3:
                    p["mass"] += 1
                    eaten.append(f)
                    break

        for f in eaten:
            foods.remove(f)

        while len(foods) < NUM_FOOD:
            foods.append({
                "x": random.uniform(0, WORLD_W),
                "y": random.uniform(0, WORLD_H),
                "mass": 1
            })

        # --- SEND STATE ---
        state_msg = json.dumps({
            "type": "state",
            "players": list(players.values()),
            "foods": foods
        })

        broadcast(state_msg)


def start_server():
    host = socket.gethostbyname(socket.gethostname())
    port = 5678
    print(f"Server running at {host}:{port}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    threading.Thread(target=game_loop, daemon=True).start()

    while True:
        sock, addr = server.accept()
        client_sockets.append(sock)
        threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()