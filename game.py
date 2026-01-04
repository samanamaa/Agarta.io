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

    state = {"players": [], "foods": []}
    my_id = None
    split_cooldown = 0

    def update_state(msg):
        nonlocal state, my_id
        if msg["type"] == "state":
            state = msg
        if msg["type"] == "welcome":
            my_id = msg["id"]

    net.state_callback = update_state

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    clock = pygame.time.Clock()

    cam_x, cam_y = 0, 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if split_cooldown > 0:
            split_cooldown -= dt

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

        if me:
            cam_x = me["x"]
            cam_y = me["y"]

        mx, my = pygame.mouse.get_pos()
        world_mx = mx + cam_x - screen_w / 2
        world_my = my + cam_y - screen_h / 2

        net.send_input(world_mx, world_my)

        screen.fill((220, 220, 230))

        for f in state["foods"]:
            sx = int(f["x"] - cam_x + screen_w / 2)
            sy = int(f["y"] - cam_y + screen_h / 2)
            if -10 < sx < screen_w + 10 and -10 < sy < screen_h + 10:
                pygame.draw.circle(screen, (120, 200, 120), (sx, sy), 4)
                pygame.draw.circle(screen, (100, 180, 100), (sx, sy), 3)

        for p in state["players"]:
            sx = int(p["x"] - cam_x + screen_w / 2)
            sy = int(p["y"] - cam_y + screen_h / 2)
            if -100 < sx < screen_w + 100 and -100 < sy < screen_h + 100:
                r = radius(p["mass"])
                is_me = p["id"] == my_id
                color = (80, 160, 255) if is_me else (200, 100, 100)
                pygame.draw.circle(screen, color, (sx, sy), r)
                pygame.draw.circle(screen, (color[0]//2, color[1]//2, color[2]//2), (sx, sy), r, 2)
                
                if p == main_cells.get(p["id"]):
                    font = pygame.font.SysFont(None, max(16, min(24, r // 2)))
                    name_text = font.render(p["name"], True, (255, 255, 255))
                    name_rect = name_text.get_rect(center=(sx, sy - r - 15))
                    bg_rect = name_rect.inflate(8, 4)
                    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                    screen.blit(name_text, name_rect)

        font_small = pygame.font.SysFont(None, 24)
        font_title = pygame.font.SysFont(None, 28)
        
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