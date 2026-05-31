import pygame
from Levels.level_select import save_progress
from Levels.level_utils import build_level

map_data = [
    "XXXXXXXXXXXXXXXXXXXXXXXX",
    "X......................X",
    "X.........P............X",
    "X......................X",
    "X............G.........X",
    "XXXXXXXXXXXXXXXXXXXXXXXX"
]


def szint2_inditas(screen, player):
    clock = pygame.time.Clock()

    platformok, kapu = build_level(map_data, player)

    kamera_x = 0
    font = pygame.font.SysFont("Arial", 40, bold=True)

    fut = True
    teljesitve = False
    ido = 0

    while fut:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "level_select"

        keys = pygame.key.get_pressed()

        if not teljesitve:
            player.mozgas(keys)
            player.gravitacio_alkalmaz()

        # ütközés
        player.foldon_van = False
        for p in platformok:
            if player.rect.colliderect(p) and player.sebesseg_y >= 0:
                player.rect.bottom = p.top
                player.sebesseg_y = 0
                player.foldon_van = True

        kamera_x = player.rect.x - screen.get_width() // 2

        # DRAW
        screen.fill((10, 10, 25))

        # platformok
        for p in platformok:
            pygame.draw.rect(screen, (70, 70, 90), p.move(-kamera_x, 0))

        # kapu
        if kapu:
            pygame.draw.rect(screen, (255, 200, 50), kapu.move(-kamera_x, 0))

        # player
        player.rajzolas(screen, kamera_x, 0)

        # UI FELIRAT
        ui = font.render("Level 2", True, (255, 255, 255))
        screen.blit(ui, (20, 20))

        esc = pygame.font.SysFont("Arial", 20).render(
            "ESC - vissza", True, (180, 180, 180))
        screen.blit(esc, (20, 70))

        # kapu
        if player.rect.colliderect(kapu) and not teljesitve:
            teljesitve = True
            ido = 1
            save_progress(3)

        if teljesitve:
            ido += 1
            msg = font.render("Siker!", True, (255, 220, 100))
            screen.blit(msg, (screen.get_width()//2 - 60, 200))

            if ido > 120:
                return "level_select"

        pygame.display.update()
        clock.tick(60)
