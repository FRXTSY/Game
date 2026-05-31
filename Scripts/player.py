import pygame

# Sprite fájlok
SPRITE_DIR = "Assets/kenney_new-platformer-pack1.1/Sprites/Tiles/Default"


class Player:
    SPRITE_W = 128
    SPRITE_H = 128
    # Ekkora méretű lesz a játékos a képernyőn
    DRAW_W = 64
    DRAW_H = 64
    # Ütközési rect (kisebb mint a sprite – igazságos játék)
    COLL_W = 36
    COLL_H = 56

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.COLL_W, self.COLL_H)
        self.sebesseg_y = 0.0
        self.foldon_van = False
        self.ugras_ereje = -15

        # irány: 1 = jobbra, -1 = balra
        self.irany = 1

        # animáció
        self._anim_timer = 0
        self._walk_frame = 0   # 0 vagy 1 (walk_a / walk_b)
        self._state = "idle"   # "idle" | "walk" | "jump"

        # sprite-ok betöltése
        self._sprites = self._load_sprites()

    # ------------------------------------------------------------------
    def _load_sprites(self):
        def load(name):
            try:
                path = f"{SPRITE_DIR}/{name}"
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                # Ha nem találja a fájlt, rajzolt fallback
                img = pygame.Surface(
                    (self.SPRITE_W, self.SPRITE_H), pygame.SRCALPHA)
                pygame.draw.rect(img, (200, 100, 100),
                                 (16, 8, 96, 112), border_radius=12)
            return pygame.transform.scale(img, (self.DRAW_W, self.DRAW_H))

        return {
            "front":  load("character_beige_front.png"),
            "jump":   load("character_beige_jump.png"),
            "walk_a": load("character_beige_walk_a.png"),
            "walk_b": load("character_beige_walk_b.png"),
        }

    # ------------------------------------------------------------------
    def mozgas(self, billentyuk):
        gyorsulas = 5
        mozog = False

        if billentyuk[pygame.K_LEFT] or billentyuk[pygame.K_a]:
            self.rect.x -= gyorsulas
            self.irany = -1
            mozog = True
        if billentyuk[pygame.K_RIGHT] or billentyuk[pygame.K_d]:
            self.rect.x += gyorsulas
            self.irany = 1
            mozog = True

        if (billentyuk[pygame.K_SPACE] or billentyuk[pygame.K_w]
                or billentyuk[pygame.K_UP]) and self.foldon_van:
            self.sebesseg_y = self.ugras_ereje
            self.foldon_van = False

        # állapot meghatározás
        if not self.foldon_van:
            self._state = "jump"
        elif mozog:
            self._state = "walk"
        else:
            self._state = "idle"

    # ------------------------------------------------------------------
    def gravitacio_alkalmaz(self):
        if not self.foldon_van:
            self.sebesseg_y += 0.8
        self.rect.y += int(self.sebesseg_y)

    # ------------------------------------------------------------------
    def _aktualis_sprite(self):
        if self._state == "jump":
            return self._sprites["jump"]
        if self._state == "idle":
            return self._sprites["front"]
        # walk animáció – 10 frame-enként vált
        self._anim_timer += 1
        if self._anim_timer >= 10:
            self._anim_timer = 0
            self._walk_frame = 1 - self._walk_frame
        key = "walk_a" if self._walk_frame == 0 else "walk_b"
        return self._sprites[key]

    # ------------------------------------------------------------------
    def rajzolas(self, kepernyo, kamera_x, remeges_x=0):
        sprite = self._aktualis_sprite()

        # tükrözés balra nézéskor
        if self.irany == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        # rajzolási pozíció: sprite közepe = collision rect közepe
        draw_x = (self.rect.centerx - kamera_x + remeges_x
                  - self.DRAW_W // 2)
        draw_y = self.rect.bottom - self.DRAW_H

        kepernyo.blit(sprite, (draw_x, draw_y))

        # DEBUG: ütközési rect mutatása (töröld éles verzióban)
        # pygame.draw.rect(kepernyo, (255,0,0),
        #     (self.rect.x - kamera_x, self.rect.y,
        #      self.COLL_W, self.COLL_H), 1)
