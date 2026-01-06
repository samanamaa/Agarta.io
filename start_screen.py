import pygame
from client import discover_servers
import threading

def start_screen():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 54)

    name = ""
    active = "name"
    servers = []
    selected_server = None
    searching = False
    last_search_time = 0

    def search_servers():
        nonlocal servers, searching
        searching = True
        servers = discover_servers(2.0)
        searching = False

    search_servers()

    while True:
        clock.tick(60)
        current_time = pygame.time.get_ticks() / 1000.0

        title = big_font.render("Agarta.io", True, (230, 230, 240))
        name_label = font.render("Meno:", True, (220, 220, 230))
        servers_label = font.render("Dostupné servery:", True, (220, 220, 230))

        name_rect = pygame.Rect(screen_w // 2 - 200, 200, 400, 40)
        button_rect = pygame.Rect(screen_w // 2 - 80, screen_h - 100, 160, 50)
        refresh_rect = pygame.Rect(screen_w - 200, 50, 150, 40)

        server_list_y = 320
        server_item_height = 50
        server_rects = []
        for i, srv in enumerate(servers):
            server_rects.append(pygame.Rect(screen_w // 2 - 200, server_list_y + i * server_item_height, 400, server_item_height - 5))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None, None
            if e.type == pygame.MOUSEBUTTONDOWN:
                if refresh_rect.collidepoint(e.pos):
                    if not searching and current_time - last_search_time > 1.0:
                        threading.Thread(target=search_servers, daemon=True).start()
                        last_search_time = current_time
                elif button_rect.collidepoint(e.pos) and name.strip() and selected_server:
                    return name.strip(), selected_server["ip"]
                elif name_rect.collidepoint(e.pos):
                    active = "name"
                else:
                    for i, srv_rect in enumerate(server_rects):
                        if srv_rect.collidepoint(e.pos) and i < len(servers):
                            selected_server = servers[i]
                            active = None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if name.strip() and selected_server:
                        return name.strip(), selected_server["ip"]
                elif e.key == pygame.K_BACKSPACE:
                    if active == "name":
                        name = name[:-1]
                else:
                    char = e.unicode
                    if char.isprintable() and active == "name":
                        name += char

        screen.fill((30, 35, 60))

        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 50))

        screen.blit(name_label, (screen_w // 2 - 200, 170))
        pygame.draw.rect(screen, (70, 80, 110), name_rect, border_radius=6)
        pygame.draw.rect(
            screen,
            (120, 180, 255) if active == "name" else (120, 130, 150),
            name_rect,
            2,
            border_radius=6,
        )
        name_surf = font.render(name or " ", True, (240, 240, 250))
        screen.blit(name_surf, (name_rect.x + 8, name_rect.y + 8))

        screen.blit(servers_label, (screen_w // 2 - 200, 280))

        if searching:
            search_text = small_font.render("Hľadám servery...", True, (150, 150, 200))
            screen.blit(search_text, (screen_w // 2 - 200, server_list_y))
        elif not servers:
            no_servers_text = small_font.render("Žiadne servery nenájdené", True, (150, 100, 100))
            screen.blit(no_servers_text, (screen_w // 2 - 200, server_list_y))
        else:
            for i, srv in enumerate(servers):
                srv_rect = server_rects[i]
                is_selected = selected_server == srv
                color = (100, 150, 200) if is_selected else (70, 80, 110)
                border_color = (120, 180, 255) if is_selected else (100, 110, 130)
                
                pygame.draw.rect(screen, color, srv_rect, border_radius=6)
                pygame.draw.rect(screen, border_color, srv_rect, 2, border_radius=6)
                
                ip_text = font.render(srv["ip"], True, (240, 240, 250))
                players_text = small_font.render(f"{srv['players']} hráčov", True, (200, 200, 210))
                screen.blit(ip_text, (srv_rect.x + 10, srv_rect.y + 8))
                screen.blit(players_text, (srv_rect.x + 10, srv_rect.y + 30))

        pygame.draw.rect(screen, (80, 100, 130), refresh_rect, border_radius=6)
        refresh_text = font.render("Obnoviť", True, (240, 240, 250))
        screen.blit(refresh_text, (refresh_rect.x + (refresh_rect.w - refresh_text.get_width()) // 2, refresh_rect.y + 8))

        ready = bool(name.strip() and selected_server)
        pygame.draw.rect(
            screen,
            (90, 200, 130) if ready else (80, 90, 100),
            button_rect,
            border_radius=8,
        )
        btn_text = font.render("Hrať", True, (10, 15, 20))
        screen.blit(
            btn_text,
            (
                button_rect.x + (button_rect.w - btn_text.get_width()) // 2,
                button_rect.y + (button_rect.h - btn_text.get_height()) // 2,
            ),
        )

        pygame.display.flip()

