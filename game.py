import pygame
from client import NetworkClient
import math
from start_screen import start_screen


def radius(m):
    return int(math.sqrt(m) * 3) + 4


def show_error(message):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    timer = 0
    while timer < 1.8:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
        screen.fill((40, 30, 30))
        text = font.render(message, True, (230, 100, 100))
        screen.blit(
            text,
            (screen_w // 2 - text.get_width() // 2, screen_h // 2 - text.get_height() // 2),
        )
        pygame.display.flip()
        timer += clock.tick(60) / 1000
    return True


def main():
    while True:
        name, ip = start_screen()
        if not name or not ip:
            return
        net = NetworkClient(ip, name)
        try:
            net.connect()
            break
        except Exception:
            if not show_error("Nepodarilo sa pripojiť k serveru"):
                return

    state = {"players": [], "foods": [], "viruses": []}
    prev_state = {"players": [], "foods": [], "viruses": []}
    state_time = 0.0
    my_id = None
    split_cooldown = 0

    def update_state(msg):
        nonlocal state, prev_state, state_time, my_id
        if msg["type"] == "state":
            prev_state = state.copy()
            state = msg
            state_time = 0.0
        if msg["type"] == "welcome":
            my_id = msg["id"]

    net.state_callback = update_state

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 24)
    font_title = pygame.font.SysFont(None, 28)
    name_fonts = {}
    
    cam_x, cam_y = 1000, 700
    zoom = 1.0
    input_timer = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if split_cooldown > 0:
            split_cooldown -= dt
        input_timer += dt
        state_time += dt
        alpha = min(1.0, state_time * 60.0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_SPACE:
                    if split_cooldown <= 0:
                        net.send_split()
                        split_cooldown = 0.3

        player_groups = {}
        for p in state["players"]:
            if p["id"] not in player_groups:
                player_groups[p["id"]] = []
            player_groups[p["id"]].append(p)
        
        main_cells = {}
        for pid, cells in player_groups.items():
            if cells:
                main_cells[pid] = max(cells, key=lambda c: c["mass"])
        
        me = main_cells.get(my_id)
        prev_player_dict = {p["id"]: p for p in prev_state.get("players", [])}

        if me:
            prev_me = prev_player_dict.get(my_id)
            if prev_me and alpha < 1.0:
                interp_me_x = prev_me["x"] + (me["x"] - prev_me["x"]) * alpha
                interp_me_y = prev_me["y"] + (me["y"] - prev_me["y"]) * alpha
            else:
                interp_me_x = me["x"]
                interp_me_y = me["y"]
            
            cam_x = interp_me_x
            cam_y = interp_me_y
            base_mass = 16
            mass_over_base = max(0, me["mass"] - base_mass)
            zoom_steps = int(mass_over_base / 50)
            zoom = 1.0 + zoom_steps * 0.08
            zoom = max(1.0, min(2.0, zoom))
        elif state["players"]:
            first_player = state["players"][0]
            cam_x = first_player["x"]
            cam_y = first_player["y"]

        if me and input_timer >= 0.016:
            mx, my = pygame.mouse.get_pos()
            world_mx = (mx - screen_w / 2) * zoom + cam_x
            world_my = (my - screen_h / 2) * zoom + cam_y
            net.send_input(world_mx, world_my)
            input_timer = 0.0

        if me:
            view_w = screen_w * zoom
            view_h = screen_h * zoom
            min_x = cam_x - view_w / 2 - 50
            max_x = cam_x + view_w / 2 + 50
            min_y = cam_y - view_h / 2 - 50
            max_y = cam_y + view_h / 2 + 50
        else:
            min_x = -1000
            max_x = 1000
            min_y = -1000
            max_y = 1000

        screen.fill((220, 220, 230))

        for f in state["foods"]:
            if min_x <= f["x"] <= max_x and min_y <= f["y"] <= max_y:
                sx = int((f["x"] - cam_x) / zoom + screen_w / 2)
                sy = int((f["y"] - cam_y) / zoom + screen_h / 2)
                if 0 <= sx < screen_w and 0 <= sy < screen_h:
                    food_r = max(2, int(4 / zoom))
                    pygame.draw.circle(screen, (120, 200, 120), (sx, sy), food_r)
                    pygame.draw.circle(screen, (100, 180, 100), (sx, sy), max(1, int(3 / zoom)))

        for v in state.get("viruses", []):
            if min_x <= v["x"] <= max_x and min_y <= v["y"] <= max_y:
                sx = int((v["x"] - cam_x) / zoom + screen_w / 2)
                sy = int((v["y"] - cam_y) / zoom + screen_h / 2)
                if -50 <= sx < screen_w + 50 and -50 <= sy < screen_h + 50:
                    virus_r = int(radius(v["mass"]) / zoom)
                    pygame.draw.circle(screen, (50, 200, 50), (sx, sy), virus_r)
                    pygame.draw.circle(screen, (30, 180, 30), (sx, sy), virus_r - 2)
                    for i in range(6):
                        angle = i * math.pi / 3
                        spike_x = sx + int(math.cos(angle) * virus_r * 0.8)
                        spike_y = sy + int(math.sin(angle) * virus_r * 0.8)
                        pygame.draw.circle(screen, (40, 190, 40), (spike_x, spike_y), max(2, int(virus_r / 4)))

        for p in state["players"]:
            if min_x <= p["x"] <= max_x and min_y <= p["y"] <= max_y:
                prev_p = prev_player_dict.get(p["id"])
                if prev_p and alpha < 1.0:
                    interp_x = prev_p["x"] + (p["x"] - prev_p["x"]) * alpha
                    interp_y = prev_p["y"] + (p["y"] - prev_p["y"]) * alpha
                else:
                    interp_x = p["x"]
                    interp_y = p["y"]
                
                sx = int((interp_x - cam_x) / zoom + screen_w / 2)
                sy = int((interp_y - cam_y) / zoom + screen_h / 2)
                if -100 <= sx < screen_w + 100 and -100 <= sy < screen_h + 100:
                    r = int(radius(p["mass"]) / zoom)
                    is_me = p["id"] == my_id
                    color = (80, 160, 255) if is_me else (200, 100, 100)
                    pygame.draw.circle(screen, color, (sx, sy), r)
                    pygame.draw.circle(screen, (color[0]//2, color[1]//2, color[2]//2), (sx, sy), r, 2)
                    
                    if p == main_cells.get(p["id"]):
                        font_size = max(16, min(24, int(r // 2)))
                        if font_size not in name_fonts:
                            name_fonts[font_size] = pygame.font.SysFont(None, font_size)
                        font = name_fonts[font_size]
                        name_text = font.render(p["name"], True, (255, 255, 255))
                        name_rect = name_text.get_rect(center=(sx, sy - r - 15))
                        bg_rect = name_rect.inflate(8, 4)
                        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                        screen.blit(name_text, name_rect)
        
        player_scores = {}
        for pid, cells in player_groups.items():
            if cells:
                total_mass = cells[0].get("total_mass", sum(c["mass"] for c in cells))
                player_scores[pid] = {
                    "name": cells[0]["name"],
                    "mass": total_mass,
                    "is_me": pid == my_id
                }
        
        sorted_players = sorted(player_scores.items(), key=lambda x: x[1]["mass"], reverse=True)[:10]
        
        scoreboard_w = 250
        scoreboard_h = 30 + len(sorted_players) * 28
        scoreboard_rect = pygame.Rect(10, 10, scoreboard_w, scoreboard_h)
        pygame.draw.rect(screen, (40, 40, 50, 200), scoreboard_rect)
        pygame.draw.rect(screen, (100, 100, 120), scoreboard_rect, 2)
        
        title_text = font_title.render("TOP HRÁČI", True, (255, 255, 255))
        screen.blit(title_text, (scoreboard_rect.x + 10, scoreboard_rect.y + 5))
        
        for i, (pid, info) in enumerate(sorted_players):
            y_pos = scoreboard_rect.y + 35 + i * 28
            color = (100, 200, 255) if info["is_me"] else (255, 255, 255)
            rank_text = font_small.render(f"{i+1}. {info['name']}", True, color)
            mass_text = font_small.render(f"{int(info['mass'])}", True, color)
            screen.blit(rank_text, (scoreboard_rect.x + 10, y_pos))
            screen.blit(mass_text, (scoreboard_rect.x + scoreboard_w - mass_text.get_width() - 10, y_pos))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()