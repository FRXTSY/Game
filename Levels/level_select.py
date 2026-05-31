import pygame
import sys
import json

PROGRESS_FILE = "Level_proression.JSON"


def load_progress():
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        return data.get("unlocked_level", 1)
    except FileNotFoundError:
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"unlocked_level": 1}, f)
        return 1


def save_progress(level):
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"unlocked_level": 1}

    if level > data.get("unlocked_level", 1):
        data["unlocked_level"] = level
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f)


def level_select(screen):

    width = screen.get_width()
    height = screen.get_height()

    # Betűtípusok létrehozása
    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    font = pygame.font.SysFont("Arial", 45, bold=True)
    small_font = pygame.font.SysFont("Arial", 30)

    # A "portalok" (szintek) mérete
    portal_size = 170

    # Szintek helye a képernyőn (Rect objektumok)
    level1 = pygame.Rect(width/2 - 300, height/2 -
                         40, portal_size, portal_size)
    level2 = pygame.Rect(width/2 - 80, height/2 - 40, portal_size, portal_size)
    level3 = pygame.Rect(width/2 + 140, height/2 -
                         40, portal_size, portal_size)

    # Vissza gomb
    back_button = pygame.Rect(50, height - 100, 150, 50)

    # Jelenleg elérhető szint (itt csak 1-3 van)
    unlocked_level = load_progress()

    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()  # Egérpozíció lekérdezése

        screen.fill((15, 20, 35))  # Háttérszín

        # Dekoráció: kis körök a háttérben
        for i in range(60):
            x = (i * 131) % width
            y = (i * 253 + pygame.time.get_ticks() * 0.1) % height
            pygame.draw.circle(screen, (80, 100, 150), (int(x), int(y)), 2)

        # Cím animáció (pulzálás)
        time = pygame.time.get_ticks() / 600
        pulse = 1 + abs(pygame.math.Vector2(0, 1).rotate(time).y) * 0.03
        title_surface = title_font.render("SZINTEK", True, (255, 200, 50))
        title_width, title_height = title_surface.get_size()
        scaled_title = pygame.transform.scale(
            title_surface, (int(title_width * pulse), int(title_height * pulse)))
        title_rect = scaled_title.get_rect(center=(width/2, height/5))
        screen.blit(scaled_title, title_rect)

        # Lista a portalokról
        portals = [level1, level2, level3]

        # Szintek kirajzolása
        for i, portal in enumerate(portals):
            level_num = i + 1
            # Ellenőrzi, hogy az egér fölé megy-e
            hover = portal.collidepoint(mouse_pos)

            # Ha a szint nyitva van és az egér fölé megy
            if hover and level_num <= unlocked_level:
                color = (100, 80, 220)
                border_color = (255, 220, 80)
                size_offset = 8  # Szint "nagyobb" lesz hoverkor
                current_rect = portal.inflate(size_offset, size_offset)
            else:
                if level_num <= unlocked_level:
                    color = (70, 50, 180)  # Nyitott szint alap színe
                else:
                    color = (60, 60, 80)  # Zárt szint színe
                border_color = (180, 180, 200)
                current_rect = portal

            # Szint kirajzolása
            pygame.draw.rect(screen, color, current_rect, border_radius=20)
            pygame.draw.rect(screen, border_color,
                             current_rect, 3, border_radius=20)

            # Szint száma és felirat
            if level_num <= unlocked_level:
                text = font.render(str(level_num), True, (255, 255, 255))
                screen.blit(text, text.get_rect(center=current_rect.center))

                level_text = small_font.render("SZINT", True, (200, 200, 220))
                screen.blit(level_text, level_text.get_rect(
                    center=(current_rect.centerx, current_rect.centery - 45)))
            else:
                lock = small_font.render("ZARVA", True, (220, 80, 80))
                screen.blit(lock, lock.get_rect(center=current_rect.center))

        # Vissza gomb kirajzolása
        back_hover = back_button.collidepoint(mouse_pos)
        back_color = (180, 50, 50) if back_hover else (150, 40, 40)
        back_shadow = back_button.inflate(6, 6)
        pygame.draw.rect(screen, (0, 0, 0, 100), back_shadow, border_radius=12)
        pygame.draw.rect(screen, back_color, back_button, border_radius=12)
        if back_hover:
            pygame.draw.rect(screen, (255, 255, 255),
                             back_button, 3, border_radius=12)
        back_text = font.render("VISSZA", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)

        # Események kezelése
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Szint kiválasztása
                if level1.collidepoint(mouse_pos) and unlocked_level >= 1:
                    return 1
                if level2.collidepoint(mouse_pos) and unlocked_level >= 2:
                    return 2
                if level3.collidepoint(mouse_pos) and unlocked_level >= 3:
                    return 3
                # Vissza gomb
                if back_button.collidepoint(mouse_pos):
                    return "back"

        pygame.display.update()  # Képernyő frissítése
        clock.tick(60)  # 60 FPS
