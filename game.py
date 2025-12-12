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
        dt = clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        me = None
        for p in state["players"]:
            if p["id"] == my_id:
                me = p
                break

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
            pygame.draw.circle(screen, (120, 200, 120), (sx, sy), 3)

        for p in state["players"]:
            sx = int(p["x"] - cam_x + screen_w / 2)
            sy = int(p["y"] - cam_y + screen_h / 2)
            r = radius(p["mass"])
            color = (80, 160, 255) if p["id"] == my_id else (200, 100, 100)
            pygame.draw.circle(screen, color, (sx, sy), r)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()