import pygame


def start_screen():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_w, screen_h = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 54)

    name = ""
    ip = "192.168.1.0"
    active = "name"

    while True:
        clock.tick(60)

        title = big_font.render("Agarta.io", True, (230, 230, 240))
        prompt = font.render("Zadaj meno a IP servera", True, (200, 200, 210))
        name_label = font.render("Meno:", True, (220, 220, 230))
        ip_label = font.render("IP:", True, (220, 220, 230))

        button_rect = pygame.Rect(screen_w // 2 - 80, screen_h // 2 + 80, 160, 50)
        name_rect = pygame.Rect(screen_w // 2 - 80, screen_h // 2 - 45, 260, 40)
        ip_rect = pygame.Rect(screen_w // 2 - 80, screen_h // 2 + 15, 260, 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None, None
            if e.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(e.pos) and name.strip() and ip.strip():
                    return name.strip(), ip.strip()
                if name_rect.collidepoint(e.pos):
                    active = "name"
                if ip_rect.collidepoint(e.pos):
                    active = "ip"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if name.strip() and ip.strip():
                        return name.strip(), ip.strip()
                elif e.key == pygame.K_BACKSPACE:
                    if active == "name":
                        name = name[:-1]
                    else:
                        ip = ip[:-1]
                else:
                    char = e.unicode
                    if char.isprintable():
                        if active == "name":
                            name += char
                        else:
                            ip += char

        screen.fill((30, 35, 60))

        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 120))
        screen.blit(prompt, (screen_w // 2 - prompt.get_width() // 2, 180))

        screen.blit(name_label, (screen_w // 2 - 200, screen_h // 2 - 40))
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

        screen.blit(ip_label, (screen_w // 2 - 200, screen_h // 2 + 20))
        pygame.draw.rect(screen, (70, 80, 110), ip_rect, border_radius=6)
        pygame.draw.rect(
            screen,
            (120, 180, 255) if active == "ip" else (120, 130, 150),
            ip_rect,
            2,
            border_radius=6,
        )
        ip_surf = font.render(ip or " ", True, (240, 240, 250))
        screen.blit(ip_surf, (ip_rect.x + 8, ip_rect.y + 8))

        ready = bool(name.strip() and ip.strip())
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

