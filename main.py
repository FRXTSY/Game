import pygame
import sys

# Importok a mappaszerkezeted alapján
from Scripts.player import Player
from Scripts.load import show_loading
from Scripts.gui import show_menu
from Scripts.setting import show_settings
from Levels.level1 import szint1_inditas
from Levels.level2 import szint2_inditas
try:
    from Levels.level3 import szint3_inditas
except ImportError:
    pass # Ha a level3 még nincs teljesen kész, ne crasheljen
from Levels.level_select import level_select

def main():
    pygame.init()
    
    # A te beállításod alapján teljes képernyős nézet
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("2D Dungeon Proba 2")
    clock = pygame.time.Clock()

    # Játékos példányosítása (ahogy a te kódodban is volt)
    player = Player(100, 400)

    # Betöltőképernyő megjelenítése egyszer az elején
    show_loading(screen)

    # Játék állapotának kezdőértéke
    state = "menu"
    current_level = 1

    while True:
        if state == "menu":
            action = show_menu(screen)
            if action == "play":
                state = "level_select"
            elif action == "settings":
                state = "settings"
                
        elif state == "settings":
            action = show_settings(screen)
            if action == "back":
                state = "menu"
                
        elif state == "level_select":
            action = level_select(screen)
            if action == "back":
                state = "menu"
            elif isinstance(action, int):
                current_level = action
                state = "play_level"
                
        elif state == "play_level":
            # Szintek elindítása a választás alapján
            if current_level == 1:
                result = szint1_inditas(screen, player)
            elif current_level == 2:
                result = szint2_inditas(screen, player)
            elif current_level == 3:
                try:
                    result = szint3_inditas(screen, player)
                except NameError:
                    result = "level_select" # Ha nincs még kész a 3. szint
            else:
                result = "level_select"
                
            # Szint eredményének kezelése
            if result == "level_select":
                state = "level_select"
            elif result == "quit":
                pygame.quit()
                sys.exit()

        clock.tick(60)

if __name__ == "__main__":
    main()