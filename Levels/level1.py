# ============================================================================
# 2D DUNGEON - LEVEL 1 (DEFINITIVE SCI-FI SURVIVAL EDITION)
# ============================================================================
import pygame
import math
import random
import sys
import json
import os

# --- GOLYÓÁLLÓ HANG BETÖLTÉS ---
pygame.mixer.init()
COW_SOUNDS = []

# Kiszámoljuk a projekt főkönyvtárát (Game-main) dinamikusan
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hang1_utvonal = os.path.join(BASE_DIR, "Assets", "cow_death1.wav")
hang2_utvonal = os.path.join(BASE_DIR, "Assets", "cow_death2.wav")

try:
    if os.path.exists(hang1_utvonal) and os.path.exists(hang2_utvonal):
        snd1 = pygame.mixer.Sound(hang1_utvonal)
        snd2 = pygame.mixer.Sound(hang2_utvonal)
        snd1.set_volume(1.0) # Maximum hangerő
        snd2.set_volume(1.0)
        COW_SOUNDS = [snd1, snd2]
        print(f"\n[+] SIKER: Hangok betöltve innen: {BASE_DIR}\\Assets\\\n")
    else:
        print("\n[-] HIBA: Nem találom a hangfájlokat!")
        print(f"PONTOSAN ITT KERESTEM:\n1. {hang1_utvonal}\n2. {hang2_utvonal}\n")
except Exception as e:
    print(f"\n[-] RENDSZERHIBA A HANGOKKAL: {e}\n")

# ============================================================================
# MENTÉS ÉS KÉPESSÉGFA RENDSZER (Ideiglenes Coinokkal)
# ============================================================================
PROGRESS_FILE = "Level_proression.JSON"

# ============================================================================
# MENTÉS ÉS KÉPESSÉGFA RENDSZER (Ideiglenes Coinokkal)
# ============================================================================
PROGRESS_FILE = "Level_proression.JSON"

# GLOBÁLIS COIN VÁLTOZÓ (Ha kilépsz a játékból, ez törlődik, ahogy kérted!)
if "SESSION_COINS" not in globals():
    global SESSION_COINS
    SESSION_COINS = 0

def load_save_data():
    default_data = {
        "unlocked_level": 1,
        "skills": {
            "dj": 0,   # Dupla Ugrás (0 vagy 1)
            "dmg": 0,  # Sebzés (0, 1, 2, 3)
            "hp": 0    # HP (0, 1, 2)
        }
    }
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                if "skills" not in data:
                    data["skills"] = default_data["skills"]
                return data
        except:
            pass
    return default_data

def save_save_data(data):
    # A Coinokat NEM mentjük a JSON-be, mert csak a játékmenet idejére kérted!
    # A skillek és a pályaszint viszont megmarad.
    safe_data = {
        "unlocked_level": data.get("unlocked_level", 1),
        "skills": data.get("skills", {"dj":0, "dmg":0, "hp":0})
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(safe_data, f)

# Árak
COST_DJ = 800
COST_DMG = [400, 1000, 2000]
COST_HP = [600, 1200]

# ============================================================================
# KONSTANSOK ÉS BEÁLLÍTÁSOK
# ============================================================================
TILE_SIZE = 64
FPS = 60
GRAVITY = 0.8
TERMINAL_VELOCITY = 14

COLOR_SKY_TOP = (15, 5, 30)
COLOR_SKY_BOT = (60, 20, 80)
COLOR_DIRT = (45, 35, 55)
COLOR_DARK_DIRT = (25, 15, 35)
COLOR_GRASS = (0, 200, 150) # Neon sci-fi fű
COLOR_WIND = (100, 255, 200, 30)

# ============================================================================
# ÚJ PÁLYAGENERÁLÁS (Kulturált, strukturált, logikus)
# ============================================================================
MAP_WIDTH = 400
MAP_HEIGHT = 18

MAP_GRID = [["." for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# 1. Fő talaj generálása (Kisimított domborzat)
x = 0
y = 12
while x < MAP_WIDTH - 20:
    # Stabil sík terület
    flat_len = random.randint(15, 25)
    for i in range(x, min(x + flat_len, MAP_WIDTH - 20)):
        MAP_GRID[y][i] = "G"
        for j in range(y+1, MAP_HEIGHT-1): MAP_GRID[j][i] = "X"
        MAP_GRID[MAP_HEIGHT-1][i] = "B"
    x += flat_len
    
    if x >= MAP_WIDTH - 20: break
    
    # Akadály vagy szintkülönbség
    obstacle_type = random.choice(["gap", "spike_pit", "step_up", "step_down"])
    
    if obstacle_type == "gap":
        gap_w = random.randint(1, 2) # Szigorúan max 2 blokk
        x += gap_w
    elif obstacle_type == "spike_pit":
        pit_w = random.randint(3, 5)
        for i in range(x, min(x + pit_w, MAP_WIDTH - 20)):
            MAP_GRID[y+2][i] = "G"
            MAP_GRID[y+1][i] = "^" # Tüskék szépen a gödörben!
            for j in range(y+3, MAP_HEIGHT-1): MAP_GRID[j][i] = "X"
            MAP_GRID[MAP_HEIGHT-1][i] = "B"
        x += pit_w
    elif obstacle_type == "step_up":
        y = max(8, y - 1)
        x += 1
    elif obstacle_type == "step_down":
        y = min(14, y + 1)
        x += 1

# 2. Szép Lebegő Szigetek (Íves aljjal)
for ix in range(20, MAP_WIDTH - 30, 25):
    if random.random() < 0.6:
        iw = random.randint(4, 7)
        iy = random.randint(5, 8)
        
        # Sziget test
        for i in range(ix, min(ix + iw, MAP_WIDTH)):
            if MAP_GRID[iy][i] == ".": MAP_GRID[iy][i] = "P"     # Teteje
            if MAP_GRID[iy+1][i] == ".": MAP_GRID[iy+1][i] = "p" # Közepe
            # Sziget aljának lekerekítése
            if MAP_GRID[iy+2][i] == ".":
                if i == ix or i == ix+iw-1: MAP_GRID[iy+2][i] = "b" # Széle
                else: 
                    MAP_GRID[iy+2][i] = "p"
                    if MAP_GRID[iy+3][i] == ".": MAP_GRID[iy+3][i] = "b"
                    
        # Trambulin a sziget alá
        for check_y in range(iy+3, MAP_HEIGHT):
            center_x = ix + iw//2
            if center_x < MAP_WIDTH and MAP_GRID[check_y][center_x] == "G":
                MAP_GRID[check_y-1][center_x] = "J"
                break

# 3. Logikus Dekoráció és NPC lehelyezés
for x in range(10, MAP_WIDTH - 20):
    for y in range(1, MAP_HEIGHT):
        if MAP_GRID[y][x] == "G":
            # Szabad a hely felette?
            if MAP_GRID[y-1][x] == ".":
                # Biztonságos-e (nincs tüske a közelben)?
                safe = True
                for c in range(max(0, x-2), min(MAP_WIDTH, x+3)):
                    if MAP_GRID[y-1][c] == "^": safe = False
                
                r = random.random()
                if safe and r > 0.96: MAP_GRID[y-1][x] = "M" # Tehén csak biztonságos helyen
                elif safe and r > 0.90: MAP_GRID[y-1][x] = "E" # Ellenség
                elif r > 0.85: MAP_GRID[y-1][x] = "C" # Láda
                elif r > 0.80: MAP_GRID[y-1][x] = "T" # Fa
                elif r > 0.75: MAP_GRID[y-1][x] = "F" # Bokor
                elif r > 0.70: MAP_GRID[y-1][x] = "R" # Szikla
                elif r > 0.60: MAP_GRID[y-1][x] = "O" # Érme
            break
        elif MAP_GRID[y][x] == "P":
            if random.random() > 0.6 and MAP_GRID[y-1][x] == ".":
                MAP_GRID[y-1][x] = random.choice(["O", "O", "C", "E"])
            break

# Alap struktúrák
MAP_GRID[9][MAP_WIDTH - 15] = "#"
MAP_GRID[10][MAP_WIDTH - 15] = "#"
for rx in range(MAP_WIDTH - 20, MAP_WIDTH):
    MAP_GRID[11][rx] = "G"
    for ry in range(12, MAP_HEIGHT): MAP_GRID[ry][rx] = "X"

MAP_GRID[6][5] = "S"

for x in range(MAP_WIDTH):
    if MAP_GRID[MAP_HEIGHT - 2][x] == ".":
        MAP_GRID[MAP_HEIGHT - 1][x] = "W"

MAP = ["".join(row) for row in MAP_GRID]

# ============================================================================
# TEXTÚRA GYÁR ÉS ANIMÁCIÓK
# ============================================================================
class GraphicsFactory:
    _cache = {}
    @classmethod
    def get_texture(cls, name, frame=0):
        key = f"{name}_{frame}"
        if key in cls._cache: return cls._cache[key]
        
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # TALAJ
        if name == "grass_top":
            surf.fill(COLOR_DIRT); pygame.draw.rect(surf, COLOR_GRASS, (0, 0, TILE_SIZE, 12))
            for i in range(0, TILE_SIZE, 4): pygame.draw.rect(surf, COLOR_GRASS, (i, -random.randint(2, 6), 2, 8))
        elif name == "dirt" or name == "p":
            surf.fill(COLOR_DIRT)
            for _ in range(12): pygame.draw.rect(surf, COLOR_DARK_DIRT, (random.randint(0, TILE_SIZE-6), random.randint(0, TILE_SIZE-6), 6, 6))
        elif name == "dirt_bottom" or name == "b":
            surf.fill(COLOR_DIRT); pygame.draw.rect(surf, (20, 10, 30), (0, TILE_SIZE-16, TILE_SIZE, 16), border_bottom_left_radius=10, border_bottom_right_radius=10)
        elif name == "platform":
            surf.fill((60, 40, 80)); pygame.draw.rect(surf, COLOR_GRASS, (0, 0, TILE_SIZE, 8))
        
        # DÍSZLETEK
        elif name == "tree":
            surf = pygame.Surface((TILE_SIZE*2, TILE_SIZE*4), pygame.SRCALPHA)
            pygame.draw.rect(surf, (60, 40, 80), (TILE_SIZE - 10, TILE_SIZE*2, 20, TILE_SIZE*2))
            pygame.draw.circle(surf, (0, 255, 200), (TILE_SIZE, TILE_SIZE*2), 40)
            pygame.draw.circle(surf, (50, 200, 255), (TILE_SIZE - 20, TILE_SIZE*2 + 20), 35)
            pygame.draw.circle(surf, (0, 150, 200), (TILE_SIZE + 20, TILE_SIZE*2 + 20), 35)
        elif name == "rock":
            pygame.draw.polygon(surf, (100, 80, 120), [(10, 64), (32, 24), (54, 64)])
            pygame.draw.polygon(surf, (130, 110, 150), [(10, 64), (32, 24), (40, 64)])
        elif name == "bush":
            pygame.draw.circle(surf, (0, 200, 150), (32, 44), 20); pygame.draw.circle(surf, (0, 255, 200), (20, 54), 15); pygame.draw.circle(surf, (0, 150, 100), (44, 54), 15)
        elif name == "crate":
            surf.fill((80, 60, 100)); pygame.draw.rect(surf, (50, 30, 70), (0, 0, TILE_SIZE, TILE_SIZE), 5)
            pygame.draw.line(surf, (50, 30, 70), (0, 0), (TILE_SIZE, TILE_SIZE), 4); pygame.draw.line(surf, (50, 30, 70), (TILE_SIZE, 0), (0, TILE_SIZE), 4)
        elif name == "spike":
            pygame.draw.polygon(surf, (255, 50, 50), [(8, 64), (16, 20), (24, 64)])
            pygame.draw.polygon(surf, (200, 40, 40), [(24, 64), (32, 10), (40, 64)])
            pygame.draw.polygon(surf, (220, 50, 50), [(40, 64), (48, 25), (56, 64)])
        elif name == "trampoline":
            pygame.draw.rect(surf, (100, 200, 255), (10, 50, 44, 14), border_radius=4); pygame.draw.rect(surf, (200, 255, 255), (14, 46, 36, 6), border_radius=3)
            pygame.draw.line(surf, (50, 150, 200), (18, 50), (18, 58), 2); pygame.draw.line(surf, (50, 150, 200), (46, 50), (46, 58), 2)
            
        # ANIMÁLT TEHÉN
        elif name == "cow":
            surf = pygame.Surface((int(TILE_SIZE * 1.5), TILE_SIZE), pygame.SRCALPHA)
            leg_y = 38 if frame in [0, 2] else 36 # Lábak mozgása
            head_y = 8 if frame in [0, 1] else 32 # Fej mozgása (legel)
            
            # Lábak
            pygame.draw.rect(surf, (200, 200, 200), (16, leg_y, 8, 26)); pygame.draw.rect(surf, (200, 200, 200), (32, 40 - leg_y + 36, 8, 26))
            pygame.draw.rect(surf, (200, 200, 200), (60, leg_y, 8, 26)); pygame.draw.rect(surf, (200, 200, 200), (76, 40 - leg_y + 36, 8, 26))
            # Test
            pygame.draw.rect(surf, (240, 240, 240), (12, 16, 76, 28), border_radius=12)
            pygame.draw.circle(surf, (40, 40, 40), (30, 24), 8); pygame.draw.circle(surf, (40, 40, 40), (55, 32), 10); pygame.draw.circle(surf, (40, 40, 40), (70, 22), 7)
            pygame.draw.ellipse(surf, (255, 150, 150), (40, 40, 16, 10))
            # Fej
            pygame.draw.rect(surf, (240, 240, 240), (76, head_y, 22, 26), border_radius=6)
            pygame.draw.rect(surf, (255, 150, 150), (84, head_y+10, 14, 16), border_radius=4)
            pygame.draw.circle(surf, (0, 0, 0), (80, head_y+6), 3)
            pygame.draw.polygon(surf, (255, 255, 200), [(76, head_y), (72, head_y-10), (80, head_y)]); pygame.draw.polygon(surf, (255, 255, 200), [(86, head_y), (90, head_y-10), (82, head_y)])

        # ANIMÁLT ELLENSÉG
        elif name == "enemy":
            surf = pygame.Surface((40, 52), pygame.SRCALPHA)
            y_offset = 2 if frame % 2 == 0 else 0
            pygame.draw.rect(surf, (255, 50, 100), (0, y_offset, 40, 52), border_radius=10)
            pygame.draw.circle(surf, (0, 0, 0), (26, y_offset + 15), 6)
            pygame.draw.circle(surf, (255, 255, 0), (28, y_offset + 14), 2)
            
        elif name == "steak":
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (150, 50, 20), (4, 10, 24, 14)); pygame.draw.ellipse(surf, (180, 70, 40), (6, 12, 20, 10))
            pygame.draw.rect(surf, (255, 240, 230), (2, 14, 6, 6), border_radius=2); pygame.draw.rect(surf, (255, 240, 230), (24, 14, 6, 6), border_radius=2)
        elif name == "water":
            surf.fill((150, 50, 255, 180)); pygame.draw.line(surf, (255, 150, 255, 220), (0, 2), (TILE_SIZE, 2), 2)

        cls._cache[key] = surf
        return surf

# ============================================================================
# EFFEKTEK ÉS FEGYVEREK
# ============================================================================
class Particle:
    def __init__(self, x, y, dx, dy, color, size, life):
        self.x, self.y, self.dx, self.dy, self.color, self.size, self.life, self.max_life = x, y, dx, dy, color, size, life, life
    def update(self):
        self.x += self.dx; self.y += self.dy; self.dy += 0.15; self.size = max(0.1, self.size - 0.08); self.life -= 1
    def draw(self, screen, cam_x, cam_y):
        if self.life > 0:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(255 * (self.life / self.max_life))), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (int(self.x - cam_x - self.size), int(self.y - cam_y - self.size)))

class FloatingText:
    def __init__(self, x, y, text, color=(255,255,255)):
        self.x, self.y, self.text, self.color, self.life = x, y, text, color, 50
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
    def update(self): self.y -= 1.2; self.life -= 1
    def draw(self, screen, cam_x, cam_y):
        if self.life > 0:
            surf = self.font.render(self.text, True, self.color); surf.set_alpha(min(255, self.life * 6))
            screen.blit(surf, (int(self.x - cam_x), int(self.y - cam_y)))

class Bullet:
    def __init__(self, x, y, dir, damage):
        self.rect = pygame.Rect(x, y, 16, 6)
        self.dir, self.speed, self.active, self.life, self.damage = dir, 15, True, 100, damage
    def update(self):
        self.rect.x += self.speed * self.dir; self.life -= 1
        if self.life <= 0: self.active = False
    def draw(self, screen, cam_x, cam_y):
        if not self.active: return
        px, py = self.rect.x - cam_x, self.rect.y - cam_y
        pygame.draw.rect(screen, (0, 255, 255), (px, py, self.rect.width, self.rect.height), border_radius=3)
        pygame.draw.rect(screen, (255, 255, 255), (px+4, py+2, self.rect.width-8, self.rect.height-4))

# ============================================================================
# NPC-K ÉS ELLENSÉGEK
# ============================================================================
class Cow:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, int(TILE_SIZE * 1.5), TILE_SIZE)
        self.start_x, self.dir, self.speed, self.hp, self.alive, self.hit_timer = x, 1, 0.5, 2, True, 0
    def take_damage(self, amount):
        if not self.alive or self.hit_timer > 0: return False
        self.hp -= amount; self.hit_timer = 10; self.rect.y -= 5; self.rect.x -= self.dir * 10
        if self.hp <= 0: self.alive = False
        return True
    def update(self, solid_blocks):
        if not self.alive: return
        if self.hit_timer > 0: self.hit_timer -= 1
        self.rect.y += 4
        for p in solid_blocks:
            if self.rect.colliderect(p): self.rect.bottom = p.top
            
        time_ms = pygame.time.get_ticks()
        is_grazing = (time_ms % 4000) < 1500
        
        if not is_grazing and self.hit_timer == 0:
            self.rect.x += self.speed * self.dir
            if abs(self.rect.x - self.start_x) > 100: self.dir *= -1; self.start_x = self.rect.x
            edge = pygame.Rect(self.rect.right + 5 if self.dir == 1 else self.rect.left - 5, self.rect.bottom + 4, 2, 2)
            if not any(edge.colliderect(p) for p in solid_blocks): self.dir *= -1; self.start_x = self.rect.x
            for p in solid_blocks:
                if self.rect.colliderect(p):
                    if self.dir == 1: self.rect.right = p.left; self.dir = -1
                    else: self.rect.left = p.right; self.dir = 1
                    self.start_x = self.rect.x
    def draw(self, screen, cam_x, cam_y):
        if not self.alive: return
        time_ms = pygame.time.get_ticks()
        is_grazing = (time_ms % 4000) < 1500
        frame = (time_ms // 200) % 2
        if is_grazing: frame += 2 # 2 vagy 3 a legelés frame
        
        sprite = GraphicsFactory.get_texture("cow", frame)
        if self.dir == -1: sprite = pygame.transform.flip(sprite, True, False)
        if self.hit_timer > 0 and (self.hit_timer // 2) % 2 == 0: sprite = sprite.copy(); sprite.set_alpha(100)
        screen.blit(sprite, (self.rect.x - cam_x, self.rect.y - cam_y))

class AdvancedEnemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 52)
        self.start_x, self.dir, self.speed, self.hp, self.alive, self.hit_timer, self.state = x, 1, 1.6, 5, True, 0, "patrol"
    def take_damage(self, amount, kb_dir):
        if not self.alive or self.hit_timer > 0: return False
        self.hp -= amount; self.hit_timer = 10; self.rect.y -= 5; self.rect.x += kb_dir * 15
        if self.hp <= 0: self.alive = False
        return True
    def update(self, solid_blocks, player_rect):
        if not self.alive: return
        if self.hit_timer > 0: self.hit_timer -= 1
        self.rect.y += 4
        for p in solid_blocks:
            if self.rect.colliderect(p): self.rect.bottom = p.top
        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        if dist < 300 and abs(player_rect.y - self.rect.y) < 150:
            self.state, self.dir, self.speed = "chase", 1 if player_rect.centerx > self.rect.centerx else -1, 3.0
        else:
            self.state, self.speed = "patrol", 1.6
            if abs(self.rect.x - self.start_x) > 160: self.dir = -1 if self.rect.x > self.start_x else 1
        if self.hit_timer == 0:
            self.rect.x += self.speed * self.dir
            edge = pygame.Rect(self.rect.right + 5 if self.dir == 1 else self.rect.left - 5, self.rect.bottom + 4, 2, 2)
            if not any(edge.colliderect(p) for p in solid_blocks): self.dir *= -1; self.start_x = self.rect.x
            for p in solid_blocks:
                if self.rect.colliderect(p):
                    if self.dir == 1: self.rect.right = p.left; self.dir = -1
                    else: self.rect.left = p.right; self.dir = 1
                    self.start_x = self.rect.x
    def draw(self, screen, cam_x, cam_y):
        if not self.alive: return
        frame = (pygame.time.get_ticks() // 150) % 2
        sprite = GraphicsFactory.get_texture("enemy", frame)
        if self.dir == -1: sprite = pygame.transform.flip(sprite, True, False)
        if self.hit_timer > 0 and (self.hit_timer // 2) % 2 == 0: sprite = sprite.copy(); sprite.set_alpha(100)
        screen.blit(sprite, (self.rect.x - cam_x, self.rect.y - cam_y))
        
class Item:
    def __init__(self, x, y, kind):
        self.rect, self.base_y, self.kind, self.time, self.active = pygame.Rect(x, y, 32, 32), y, kind, random.uniform(0, 5), True
    def update(self):
        self.time += 0.1; self.rect.y = self.base_y + int(math.sin(self.time) * 6)
    def draw(self, screen, cam_x, cam_y):
        if not self.active: return
        px, py = self.rect.x - cam_x, self.rect.y - cam_y
        if self.kind == "coin":
            pygame.draw.circle(screen, (255, 215, 0), (px + 16, py + 16), 11); pygame.draw.circle(screen, (255, 255, 255), (px + 16, py + 16), 11, 2)
        elif self.kind == "steak": screen.blit(GraphicsFactory.get_texture("steak"), (px, py))

# ============================================================================
# PÁLYAKEZELŐ (LEVEL MANAGER)
# ============================================================================
class LevelManager:
    def __init__(self, screen, player):
        global SESSION_COINS
        self.screen, self.player = screen, player
        self.sw, self.sh = screen.get_width(), screen.get_height()
        self.map_w = MAP_WIDTH * TILE_SIZE; self.map_h = MAP_HEIGHT * TILE_SIZE
        self.cam_x = 0; self.cam_y = self.map_h - self.sh
        
        self.solid_blocks, self.platforms, self.spikes, self.trampolines, self.water_zones, self.decor = [], [], [], [], [], []
        self.enemies, self.cows, self.items, self.particles, self.float_texts, self.bullets = [], [], [], [], [], []
        
        self.score = 0
        self.shake_timer = 0
        self.state = "playing"
        self.fade_alpha = 255
        self.goal = None
        self.shoot_cooldown = 0
        
        self.save_data = load_save_data()
        self.coins = SESSION_COINS # A coinokat a memóriából olvassuk!
        
        hp_level = self.save_data["skills"]["hp"]
        self.player_max_hp = 100 + (20 * hp_level)
        self.player_hp = self.player_max_hp
        self.player_invincible = 0
        
        self.has_double_jump = (self.save_data["skills"]["dj"] == 1)
        self.dj_used = False
        
        dmg_level = self.save_data["skills"]["dmg"]
        self.player_damage = 1 + dmg_level 
        
        self.build_level()

    def build_level(self):
        for y, row in enumerate(MAP):
            for x, cell in enumerate(row):
                wx, wy = x * TILE_SIZE, y * TILE_SIZE
                if cell == 'G': self.solid_blocks.append(pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)); self.decor.append(("grass_top", wx, wy))
                elif cell == 'X': self.solid_blocks.append(pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)); self.decor.append(("dirt", wx, wy))
                elif cell == 'B': self.solid_blocks.append(pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)); self.decor.append(("dirt_bottom", wx, wy))
                elif cell == 'C': self.solid_blocks.append(pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)); self.decor.append(("crate", wx, wy))
                elif cell == 'P': self.platforms.append(pygame.Rect(wx, wy, TILE_SIZE, 10)); self.decor.append(("platform", wx, wy))
                elif cell == 'p': self.platforms.append(pygame.Rect(wx, wy, TILE_SIZE, 10)); self.decor.append(("dirt", wx, wy))
                elif cell == 'b': self.platforms.append(pygame.Rect(wx, wy, TILE_SIZE, 10)); self.decor.append(("dirt_bottom", wx, wy))
                elif cell == 'W': self.water_zones.append(pygame.Rect(wx, wy + 20, TILE_SIZE, TILE_SIZE - 20)); self.decor.append(("water", wx, wy))
                elif cell == '^': self.spikes.append(pygame.Rect(wx + 10, wy + 30, TILE_SIZE - 20, TILE_SIZE - 30)); self.decor.append(("spike", wx, wy))
                elif cell == 'J': self.trampolines.append(pygame.Rect(wx + 10, wy + 46, 44, 18)); self.decor.append(("trampoline", wx, wy))
                elif cell == 'T': self.decor.append(("tree", wx, wy - TILE_SIZE*3))
                elif cell == 'F': self.decor.append(("bush", wx, wy))
                elif cell == 'R': self.decor.append(("rock", wx, wy))
                elif cell == 'M': self.cows.append(Cow(wx, wy))
                elif cell == 'S': self.player.rect.x, self.player.rect.y = wx, wy; self.player.sebesseg_y = 0
                elif cell == 'E': self.enemies.append(AdvancedEnemy(wx, wy))
                elif cell == 'O': self.items.append(Item(wx, wy + 15, "coin"))
                elif cell == '#': self.goal = pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE*2)

    def spawn_particles(self, x, y, color, count, speed=4):
        for _ in range(count): self.particles.append(Particle(x, y, random.uniform(-speed, speed), random.uniform(-speed, speed), color, random.randint(3, 7), random.randint(15, 30)))

    def damage_player(self, amount, kb_x=0, kb_y=-8):
        if self.player_invincible == 0:
            self.player_hp -= amount; self.player_invincible = 60; self.shake_timer = 15; self.player.sebesseg_y = kb_y; self.player.rect.x += kb_x
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (255, 50, 50), 20, 6)
            if self.player_hp <= 0:
                self.player_hp = 0; self.state, self.fade_alpha = "dead", 0

    def heal_player(self, amount):
        healed = min(amount, self.player_max_hp - self.player_hp)
        if healed > 0:
            self.player_hp += healed
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (50, 255, 50), 15, 4)
            self.float_texts.append(FloatingText(self.player.rect.centerx, self.player.rect.top - 20, f"+{healed} HP", (50, 255, 50)))

    def handle_player_physics(self, keys):
        if not self.player.foldon_van:
            self.player.sebesseg_y = min(self.player.sebesseg_y + GRAVITY, TERMINAL_VELOCITY)
        self.player.rect.y += int(self.player.sebesseg_y)
        
        self.player.foldon_van = False
        for p in self.solid_blocks:
            if self.player.rect.colliderect(p):
                if self.player.sebesseg_y > 0:
                    self.player.rect.bottom = p.top; self.player.sebesseg_y = 0; self.player.foldon_van = True; self.dj_used = False
                elif self.player.sebesseg_y < 0:
                    self.player.rect.top = p.bottom; self.player.sebesseg_y = 0
                    
        for p in self.platforms:
            if self.player.rect.colliderect(p):
                if self.player.sebesseg_y > 0 and self.player.rect.bottom <= p.top + 16:
                    self.player.rect.bottom = p.top; self.player.sebesseg_y = 0; self.player.foldon_van = True; self.dj_used = False
                    
        eredeti_x = self.player.rect.x
        self.player.mozgas(keys)
        for p in self.solid_blocks:
            if self.player.rect.colliderect(p): self.player.rect.x = eredeti_x

    def handle_jump_event(self):
        # TÖKÉLETES DUPLA UGRÁS LOGIKA
        if self.player.foldon_van:
            self.player.sebesseg_y = self.player.ugras_ereje
            self.player.foldon_van = False
            self.dj_used = False
        elif self.has_double_jump and not self.dj_used:
            self.player.sebesseg_y = self.player.ugras_ereje
            self.dj_used = True
            self.spawn_particles(self.player.rect.centerx, self.player.rect.bottom, (100, 255, 255), 15, 3)

    def handle_shoot(self):
        if self.shoot_cooldown == 0:
            bx = self.player.rect.right if self.player.irany == 1 else self.player.rect.left - 16
            by = self.player.rect.centery - 4
            self.bullets.append(Bullet(bx, by, self.player.irany, self.player_damage))
            self.shoot_cooldown = 15
            self.spawn_particles(bx, by, (0, 255, 255), 6, 3)

    def update(self):
        global SESSION_COINS
        if self.state != "playing": return
        
        if self.fade_alpha > 0: self.fade_alpha -= 6
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.player_invincible > 0: self.player_invincible -= 1
        
        target_cam_x = self.player.rect.centerx - self.sw // 2
        target_cam_y = self.player.rect.centery - self.sh // 2
        self.cam_x += (target_cam_x - self.cam_x) * 0.1; self.cam_y += (target_cam_y - self.cam_y) * 0.1
        self.cam_x = max(0, min(self.cam_x, self.map_w - self.sw)); self.cam_y = max(0, min(self.cam_y, self.map_h - self.sh))
        
        if self.shake_timer > 0: self.shake_timer -= 1

        if self.player.rect.y > self.map_h or any(self.player.rect.colliderect(w) for w in self.water_zones):
            if self.state == "playing": self.state, self.fade_alpha = "dead", 0

        for s in self.spikes:
            if self.player.rect.colliderect(s): self.damage_player(20, kb_y=-12) 
                
        for j in self.trampolines:
            if self.player.rect.colliderect(j) and self.player.sebesseg_y >= 0:
                self.player.sebesseg_y = -24; self.dj_used = False
                self.spawn_particles(j.centerx, j.top, (100, 200, 255), 15, 6); self.float_texts.append(FloatingText(j.centerx, j.top - 20, "BOING!", (255, 255, 255)))

        for e in self.enemies:
            if e.alive and self.player.rect.colliderect(e.rect):
                self.damage_player(25, kb_x=-20 if self.player.rect.centerx < e.rect.centerx else 20)

        for cow in self.cows: cow.update(self.solid_blocks)
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for f in self.float_texts: f.update()
        self.float_texts = [f for f in self.float_texts if f.life > 0]
        
        for b in self.bullets:
            b.update()
            for p in self.solid_blocks:
                if b.active and b.rect.colliderect(p): b.active = False; self.spawn_particles(b.rect.centerx, b.rect.centery, (0, 255, 255), 5, 2); break
            for e in self.enemies:
                if b.active and e.alive and b.rect.colliderect(e.rect):
                    b.active = False
                    if e.take_damage(b.damage, b.dir):
                        self.spawn_particles(e.rect.centerx, e.rect.centery, (255, 50, 100), 10, 4)
                        if not e.alive: self.score += 150; self.shake_timer = 5
            for cow in self.cows:
                if b.active and cow.alive and b.rect.colliderect(cow.rect):
                    b.active = False
                    if cow.take_damage(b.damage):
                        self.spawn_particles(cow.rect.centerx, cow.rect.centery, (200, 50, 50), 10, 4)
                        if not cow.alive:
                            self.score += 200
                            self.items.append(Item(cow.rect.centerx - 16, cow.rect.centery, "steak"))
                            
                            # HANG LEJÁTSZÁSA KIKÉNYSZERÍTVE
                            if COW_SOUNDS:
                                snd = random.choice(COW_SOUNDS)
                                csatorna = pygame.mixer.find_channel(True) # Keres egy szabad audiocsatornát
                                if csatorna:
                                    csatorna.play(snd, maxtime=3000)
                                print("--> TEHÉN LELÖVVE: Hang lejátszási parancs kiadva!")

        self.bullets = [b for b in self.bullets if b.active]
        
        for c in self.items:
            c.update()
            if c.active and self.player.rect.colliderect(c.rect):
                c.active = False
                if c.kind == "coin":
                    self.score += 50
                    self.coins += 50
                    SESSION_COINS = self.coins # Szinkronizáljuk a globálissal
                    self.float_texts.append(FloatingText(c.rect.x, c.rect.y - 10, "+50 Coin", (255, 215, 0)))
                    self.spawn_particles(c.rect.centerx, c.rect.centery, (255, 215, 0), 8)
                elif c.kind == "steak":
                    self.heal_player(int(self.player_max_hp * 0.20))
                    self.score += 100

        for e in self.enemies: e.update(self.solid_blocks, self.player.rect)

        if self.goal and self.player.rect.colliderect(self.goal):
            self.state = "won"
            save_progress(2)
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (50, 255, 50), 40, 8)

    def draw_skill_tree(self, mouse_pos, clicked):
        global SESSION_COINS
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA); overlay.fill((10, 5, 20, 220)); self.screen.blit(overlay, (0, 0))
        
        font_title = pygame.font.SysFont("Arial", 50, bold=True); font_norm = pygame.font.SysFont("Arial", 25, bold=True); font_sm = pygame.font.SysFont("Arial", 18)
        
        title = font_title.render("KÉPESSÉGFA (SKILL TREE)", True, (0, 255, 200))
        self.screen.blit(title, (self.sw//2 - title.get_width()//2, 50))
        coins_txt = font_norm.render(f"Pénztárca: {self.coins} Coin", True, (255, 215, 0))
        self.screen.blit(coins_txt, (self.sw//2 - coins_txt.get_width()//2, 110))
        
        skills_info = [
            ("dj", "Dupla Ugrás", 1, [COST_DJ]),
            ("dmg", "Nagyobb Sebzés", 3, COST_DMG),
            ("hp", "Több Életerő (+20)", 2, COST_HP)
        ]
        
        box_w, box_h = 320, 160
        start_x = self.sw // 2 - (box_w * 3 + 40) // 2
        
        for i, (sk_key, sk_name, max_lvl, prices) in enumerate(skills_info):
            bx, by = start_x + i * (box_w + 20), 220
            rect = pygame.Rect(bx, by, box_w, box_h)
            
            lvl = self.save_data["skills"][sk_key]
            is_max = (lvl >= max_lvl)
            price = prices[lvl] if not is_max else 0
            can_afford = (self.coins >= price) and not is_max
            hover = rect.collidepoint(mouse_pos)
            
            bg_color = (30, 20, 50) if not hover else (40, 30, 60)
            if is_max: bg_color = (10, 50, 40)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=15)
            pygame.draw.rect(self.screen, (0, 200, 255), rect, 2, border_radius=15)
            
            self.screen.blit(font_norm.render(sk_name, True, (255, 255, 255)), (bx + 15, by + 15))
            self.screen.blit(font_sm.render(f"Szint: {lvl} / {max_lvl}", True, (0, 255, 200)), (bx + 15, by + 50))
            
            btn_rect = pygame.Rect(bx + 20, by + 90, box_w - 40, 50)
            btn_color, btn_txt, txt_color = (60, 60, 80), "MAX SZINT", (150, 150, 150)
            
            if not is_max:
                btn_txt = f"Vétel: {price} Coin"
                if can_afford:
                    btn_color, txt_color = ((0, 180, 120) if btn_rect.collidepoint(mouse_pos) else (0, 120, 80)), (255, 255, 255)
                    if clicked and btn_rect.collidepoint(mouse_pos):
                        self.coins -= price
                        SESSION_COINS = self.coins
                        self.save_data["skills"][sk_key] += 1
                        save_save_data(self.save_data)
                        
                        if sk_key == "dj": self.has_double_jump = True
                        if sk_key == "dmg": self.player_damage += 1
                        if sk_key == "hp": self.player_max_hp += 20; self.player_hp += 20
                else: btn_color = (120, 40, 60)
                    
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
            tsurf = font_norm.render(btn_txt, True, txt_color)
            self.screen.blit(tsurf, (btn_rect.centerx - tsurf.get_width()//2, btn_rect.centery - tsurf.get_height()//2))

        esc_txt = font_norm.render("Nyomd meg a 'T' vagy 'ESC' gombot a kilépéshez", True, (0, 200, 255))
        self.screen.blit(esc_txt, (self.sw//2 - esc_txt.get_width()//2, self.sh - 100))

    def draw(self):
        sx = random.randint(-2, 2) if self.shake_timer > 0 else 0
        sy = random.randint(-2, 2) if self.shake_timer > 0 else 0
        cx, cy = int(self.cam_x) + sx, int(self.cam_y) + sy

        for y in range(self.sh):
            r = int(COLOR_SKY_TOP[0] * (1 - y/self.sh) + COLOR_SKY_BOT[0] * (y/self.sh))
            g = int(COLOR_SKY_TOP[1] * (1 - y/self.sh) + COLOR_SKY_BOT[1] * (y/self.sh))
            b = int(COLOR_SKY_TOP[2] * (1 - y/self.sh) + COLOR_SKY_BOT[2] * (y/self.sh))
            pygame.draw.line(self.screen, (r,g,b), (0, y), (self.sw, y))

        for kind, wx, wy in self.decor:
            if cx - TILE_SIZE*2 < wx < cx + self.sw and cy - TILE_SIZE*3 < wy < cy + self.sh:
                self.screen.blit(GraphicsFactory.get_texture(kind), (wx - cx, wy - cy))

        if self.goal:
            pygame.draw.rect(self.screen, (0, 255, 100), (self.goal.x - cx, self.goal.y - cy, self.goal.width, self.goal.height), border_radius=8)

        for cow in self.cows: cow.draw(self.screen, cx, cy)
        for c in self.items: c.draw(self.screen, cx, cy)
        for e in self.enemies: e.draw(self.screen, cx, cy)
        for b in self.bullets: b.draw(self.screen, cx, cy)
        
        if self.state != "dead":
            if self.player_invincible == 0 or (self.player_invincible // 4) % 2 == 0:
                sprite = self.player._aktualis_sprite()
                if self.player.irany == -1: sprite = pygame.transform.flip(sprite, True, False)
                px = self.player.rect.centerx - cx - self.player.DRAW_W // 2
                py = self.player.rect.bottom - cy - self.player.DRAW_H
                self.screen.blit(sprite, (px, py))
                
                gun_x = px + (40 if self.player.irany == 1 else 10)
                pygame.draw.rect(self.screen, (150, 150, 180), (gun_x, py + 35, 22, 8), border_radius=2)
                pygame.draw.rect(self.screen, (0, 255, 255), (gun_x + (18 if self.player.irany == 1 else 0), py + 36, 6, 6))

        for p in self.particles: p.draw(self.screen, cx, cy)
        for f in self.float_texts: f.draw(self.screen, cx, cy)

        # HUD / UI
        pygame.draw.rect(self.screen, (10, 5, 20, 200), (20, 20, 320, 130), border_radius=10)
        pygame.draw.rect(self.screen, (0, 200, 255), (20, 20, 320, 130), 2, border_radius=10)
        
        f_big = pygame.font.SysFont("Arial", 24, bold=True)
        f_sm = pygame.font.SysFont("Arial", 18, bold=True)
        self.screen.blit(f_big.render("PÁLYA 1 - Idegen Világ", True, (255, 255, 255)), (35, 25))
        self.screen.blit(f_sm.render(f"PONT: {self.score}", True, (0, 255, 200)), (35, 55))
        self.screen.blit(f_sm.render(f"COIN: {self.coins}", True, (255, 215, 0)), (170, 55))
        
        self.screen.blit(f_sm.render("HP:", True, (255, 255, 255)), (35, 76))
        hp_ratio = max(0, self.player_hp / self.player_max_hp)
        bar_width = 180
        pygame.draw.rect(self.screen, (80, 20, 40), (75, 78, bar_width, 16), border_radius=4)
        if hp_ratio > 0: pygame.draw.rect(self.screen, (0, 255, 100), (75, 78, int(bar_width * hp_ratio), 16), border_radius=4)
        pygame.draw.rect(self.screen, (255, 255, 255), (75, 78, bar_width, 16), 2, border_radius=4)
        
        self.screen.blit(f_sm.render("Nyomd meg a 'T' gombot a Képességfához", True, (0, 200, 255)), (35, 110))

        if self.fade_alpha > 0 and self.state == "playing":
            s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA); s.fill((0,0,0,self.fade_alpha)); self.screen.blit(s, (0,0))
        elif self.state == "dead":
            self.fade_alpha = min(255, self.fade_alpha + 6)
            s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA); s.fill((60, 0, 20, self.fade_alpha)); self.screen.blit(s, (0,0))
            txt = pygame.font.SysFont("Arial", 75, bold=True).render("MEGHALTÁL", True, (255, 255, 255))
            self.screen.blit(txt, (self.sw//2 - txt.get_width()//2, self.sh//2 - 40))
        elif self.state == "won":
            self.fade_alpha = min(255, self.fade_alpha + 4)
            s = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA); s.fill((255, 255, 255, self.fade_alpha)); self.screen.blit(s, (0,0))
            if self.fade_alpha > 140:
                txt = pygame.font.SysFont("Arial", 75, bold=True).render("SZINT TELJESÍTVE!", True, (40, 180, 40))
                self.screen.blit(txt, (self.sw//2 - txt.get_width()//2, self.sh//2 - 40))

# ============================================================================
# FŐ FUTTATÓ CIKLUS
# ============================================================================
def szint1_inditas(screen, player):
    clock = pygame.time.Clock()
    manager = LevelManager(screen, player)
    pygame.event.clear()

    while True:
        clicked = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return "quit"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1: clicked = True
            
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if manager.state == "skill_tree": manager.state = "playing"
                    else: return "level_select"
                if ev.key == pygame.K_t:
                    if manager.state == "playing": manager.state = "skill_tree"
                    elif manager.state == "skill_tree": manager.state = "playing"
                
                # Ugrás kezelése (A Dupla Ugrás logika miatt így a legjobb)
                if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) and manager.state == "playing":
                    manager.handle_jump_event()
                    
        keys = pygame.key.get_pressed()
        
        if manager.state == "playing":
            if keys[pygame.K_e]: manager.handle_shoot()
            manager.handle_player_physics(keys)
            manager.update()
        
        manager.draw()
        
        if manager.state == "skill_tree":
            manager.draw_skill_tree(pygame.mouse.get_pos(), clicked)
            
        pygame.display.update()
        clock.tick(FPS)
        
        if (manager.state == "dead" or manager.state == "won") and manager.fade_alpha >= 255:
            pygame.time.wait(800)
            return "level_select"