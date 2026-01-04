import socket
import threading
import json
import time
import math
import random

WORLD_W, WORLD_H = 2000, 1400
TICK_RATE = 60
NUM_FOOD = 200

players = {}
foods = []
client_sockets = []
SPLIT_COOLDOWN = 15


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
                        "cells": [{
                            "x": random.uniform(0, WORLD_W),
                            "y": random.uniform(0, WORLD_H),
                            "mass": 16,
                            "tx": 0,
                            "ty": 0,
                            "split_time": 0
                        }]
                    }

                    print(f"{pid} connected")

                    welcome_msg = json.dumps({
                        "type": "welcome",
                        "id": pid,
                        "world": [WORLD_W, WORLD_H]
                    }) + "\n"

                    sock.sendall(welcome_msg.encode("utf-8"))

                elif msg["type"] == "input" and pid in players:
                    player = players[pid]
                    for cell in player["cells"]:
                        cell["tx"] = msg["tx"]
                        cell["ty"] = msg["ty"]
                
                elif msg["type"] == "split" and pid in players:
                    player = players[pid]
                    if len(player["cells"]) < 16:
                        main_cell = player["cells"][0]
                        if main_cell["mass"] >= 35:
                            dx = main_cell["tx"] - main_cell["x"]
                            dy = main_cell["ty"] - main_cell["y"]
                            d = math.hypot(dx, dy)
                            if d > 0:
                                new_mass = main_cell["mass"] // 2
                                main_cell["mass"] = new_mass
                                
                                split_dist = mass_to_radius(new_mass) * 2.5
                                new_cell = {
                                    "x": main_cell["x"] + (dx / d) * split_dist,
                                    "y": main_cell["y"] + (dy / d) * split_dist,
                                    "mass": new_mass,
                                    "tx": main_cell["tx"],
                                    "ty": main_cell["ty"],
                                    "split_time": time.time()
                                }
                                new_cell["x"] = max(0, min(WORLD_W, new_cell["x"]))
                                new_cell["y"] = max(0, min(WORLD_H, new_cell["y"]))
                                
                                player["cells"].insert(0, new_cell)
                                main_cell["split_time"] = time.time()

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

        current_time = time.time()
        
        for p in players.values():
            for cell in p["cells"]:
                dx = cell["tx"] - cell["x"]
                dy = cell["ty"] - cell["y"]
                d = math.hypot(dx, dy)

                if d > 1:
                    speed = 350 / (1 + mass_to_radius(cell["mass"]) / 25)
                    if cell["split_time"] > 0 and current_time - cell["split_time"] < SPLIT_COOLDOWN:
                        speed *= 1.3
                    cell["x"] += (dx / d) * speed * dt
                    cell["y"] += (dy / d) * speed * dt

                    cell["x"] = max(0, min(WORLD_W, cell["x"]))
                    cell["y"] = max(0, min(WORLD_H, cell["y"]))
            
            if len(p["cells"]) > 1:
                merged = []
                for i, cell1 in enumerate(p["cells"]):
                    if i in merged:
                        continue
                    for j, cell2 in enumerate(p["cells"][i+1:], i+1):
                        if j in merged:
                            continue
                        if current_time - cell1["split_time"] > SPLIT_COOLDOWN and \
                           current_time - cell2["split_time"] > SPLIT_COOLDOWN:
                            dist_cells = dist((cell1["x"], cell1["y"]), (cell2["x"], cell2["y"]))
                            if dist_cells < mass_to_radius(cell1["mass"]) + mass_to_radius(cell2["mass"]):
                                cell1["mass"] += cell2["mass"]
                                merged.append(j)
                
                p["cells"] = [c for i, c in enumerate(p["cells"]) if i not in merged]

        eaten = []
        for f in foods:
            for p in players.values():
                for cell in p["cells"]:
                    if dist((cell["x"], cell["y"]), (f["x"], f["y"])) < mass_to_radius(cell["mass"]) + 3:
                        cell["mass"] += 1
                        eaten.append(f)
                        break
                if f in eaten:
                    break

        for f in eaten:
            foods.remove(f)

        cells_to_remove = {}
        
        for pid1, p1 in list(players.items()):
            for cell1 in p1["cells"]:
                for pid2, p2 in list(players.items()):
                    if pid1 == pid2:
                        continue
                    for j, cell2 in enumerate(p2["cells"]):
                        if pid2 in cells_to_remove and j in cells_to_remove[pid2]:
                            continue
                        if cell1["mass"] > cell2["mass"] * 1.25:
                            cell_dist = dist((cell1["x"], cell1["y"]), (cell2["x"], cell2["y"]))
                            r1 = mass_to_radius(cell1["mass"])
                            r2 = mass_to_radius(cell2["mass"])
                            if cell_dist < r1 - r2 * 0.5:
                                cell1["mass"] += cell2["mass"]
                                if pid2 not in cells_to_remove:
                                    cells_to_remove[pid2] = []
                                cells_to_remove[pid2].append(j)

        for pid, indices in cells_to_remove.items():
            if pid in players:
                for idx in sorted(indices, reverse=True):
                    if idx < len(players[pid]["cells"]):
                        players[pid]["cells"].pop(idx)
        
        players_to_remove = [pid for pid, p in players.items() if len(p["cells"]) == 0]
        for pid in players_to_remove:
            del players[pid]

        while len(foods) < NUM_FOOD:
            foods.append({
                "x": random.uniform(0, WORLD_W),
                "y": random.uniform(0, WORLD_H),
                "mass": 1
            })

        player_list = []
        for pid, p in players.items():
            total_mass = sum(c["mass"] for c in p["cells"])
            for cell in p["cells"]:
                player_list.append({
                    "id": pid,
                    "name": p["name"],
                    "x": cell["x"],
                    "y": cell["y"],
                    "mass": cell["mass"],
                    "total_mass": total_mass
                })
        
        state_msg = json.dumps({
            "type": "state",
            "players": player_list,
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