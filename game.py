import pygame
from client import NetworkClient
import math

SCREEN_W, SCREEN_H = 1000, 700

def radius(m):
    return int(math.sqrt(m) * 3) + 4


def main():
    name = input("Zadajte meno hráča: ")
    ip = input("IP servera: ")

    net = NetworkClient(ip, name)
    net.connect()

    state = {"players": [], "foods": []}
    my_id = None

    def update_state(msg):
        nonlocal state, my_id
        if msg["type"] == "state":
            state = msg
        if msg["type"] == "welcome":
            my_id = msg["id"]

    net.state_callback = update_state

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    cam_x, cam_y = 0, 0

    running = True
    while running:
        dt = clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # find me
        me = None
        for p in state["players"]:
            if p["id"] == my_id:
                me = p
                break

        # move camera
        if me:
            cam_x = me["x"]
            cam_y = me["y"]

        mx, my = pygame.mouse.get_pos()
        world_mx = mx + cam_x - SCREEN_W/2
        world_my = my + cam_y - SCREEN_H/2

        net.send_input(world_mx, world_my)

        screen.fill((220,220,230))

        # foods
        for f in state["foods"]:
            sx = int(f["x"] - cam_x + SCREEN_W/2)
            sy = int(f["y"] - cam_y + SCREEN_H/2)
            pygame.draw.circle(screen, (120,200,120), (sx,sy), 3)

        # players
        for p in state["players"]:
            sx = int(p["x"] - cam_x + SCREEN_W/2)
            sy = int(p["y"] - cam_y + SCREEN_H/2)
            r = radius(p["mass"])
            color = (80,160,255) if p["id"] == my_id else (200,100,100)
            pygame.draw.circle(screen, color, (sx,sy), r)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()