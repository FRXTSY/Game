# ============================================================================
# 2D DUNGEON - LEVEL 1 (EPIC ISLANDS & COZY COTTAGE FINISH EDITION)
# ============================================================================
import pygame
import math
import random
import sys
import json
import os

# ============================================================================
# HANGOK (WAV/MP3) BEÁLLÍTÁSA ÉS BETÖLTÉSE
# ============================================================================
pygame.mixer.init()
COW_SOUNDS = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hang1_utvonal = os.path.join(BASE_DIR, "Assets", "cow_death1.wav")
hang2_utvonal = os.path.join(BASE_DIR, "Assets", "cow_death2.wav")

try:
    if os.path.exists(hang1_utvonal) and os.path.exists(hang2_utvonal):
        snd1 = pygame.mixer.Sound(hang1_utvonal)
        snd2 = pygame.mixer.Sound(hang2_utvonal)
        snd1.set_volume(1.0)
        snd2.set_volume(1.0)
        COW_SOUNDS = [snd1, snd2]
except Exception:
    pass

# ============================================================================
# GLOBÁLIS MUNKAMENET (SESSION) ÁLLAPOT
# ============================================================================
PROGRESS_FILE = "Level_proression.JSON"

if "SESSION_STATE" not in globals():
    global SESSION_STATE
    SESSION_STATE = {
        "coins": 0,
        "skills": {
            "dj": 0,   
            "dmg": 0,  
            "hp": 0    
        }
    }

def get_unlocked_level():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f).get("unlocked_level", 1)
        except: pass
    return 1

def save_progress_only(lvl):
    curr = get_unlocked_level()
    if lvl > curr:
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"unlocked_level": lvl}, f)

COST_DJ = 800
COST_DMG = [400, 1000, 2000]
COST_HP = [600, 1200]

# ============================================================================
# KONSTANSOK ÉS BEÁLLÍTÁSOK
# ============================================================================
TILE_SIZE = 64
FPS = 60
GRAVITY = 0.8
TERMINAL_VELOCITY = 15

# Pasztell / Brawlhalla stílusú hangulatos színvilág
COLOR_SKY_TOP = (160, 200, 235)  
COLOR_SKY_BOT = (255, 230, 210)  
COLOR_GRASS = (120, 200, 90)    
COLOR_DIRT = (140, 100, 80)       

# ============================================================================
# PÁLYAGENERÁLÁS
# ============================================================================
MAP_WIDTH = 400
MAP_HEIGHT = 18
MAP_GRID = [["." for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# 1. Fő talaj generálása
x = 0
y = 13
while x < MAP_WIDTH - 20:
    flat_len = random.randint(15, 25)
    for i in range(x, min(x + flat_len, MAP_WIDTH - 20)):
        MAP_GRID[y][i] = "G"
        for j in range(y+1, MAP_HEIGHT-1): MAP_GRID[j][i] = "X"
        MAP_GRID[MAP_HEIGHT-1][i] = "B"
    x += flat_len
    if x >= MAP_WIDTH - 20: break
    
    obstacle_type = random.choice(["gap", "spike_pit", "step_up", "step_down"])
    
    if obstacle_type == "gap":
        x += random.randint(1, 2)
    elif obstacle_type == "spike_pit":
        pit_w = random.randint(3, 5)
        for i in range(x, min(x + pit_w, MAP_WIDTH - 20)):
            MAP_GRID[y+2][i] = "G"
            MAP_GRID[y+1][i] = "^"
            for j in range(y+3, MAP_HEIGHT-1): MAP_GRID[j][i] = "X"
            MAP_GRID[MAP_HEIGHT-1][i] = "B"
        x += pit_w
    elif obstacle_type == "step_up":
        y = max(9, y - 1); x += 1
    elif obstacle_type == "step_down":
        y = min(15, y + 1); x += 1

# 2. LEBEGŐ SZIGETEK (Íves Brawlhalla stílusban)
for ix in range(15, MAP_WIDTH - 30, 20):
    if random.random() < 0.65:
        iw = random.randint(6, 10) 
        iy = random.randint(5, 8)
        
        # Teteje (Fű)
        for i in range(ix, min(ix + iw, MAP_WIDTH)):
            if MAP_GRID[iy][i] == ".": MAP_GRID[iy][i] = "P"
        # Közepe 1 (Föld)
        for i in range(ix+1, min(ix + iw - 1, MAP_WIDTH)):
            if MAP_GRID[iy+1][i] == ".": MAP_GRID[iy+1][i] = "p"
        # Alja (Lekerekített tál alakú sziklák indákkal)
        for i in range(ix+2, min(ix + iw - 2, MAP_WIDTH)):
            if MAP_GRID[iy+2][i] == ".": MAP_GRID[iy+2][i] = "b"
            
        # Trambulin a sziget alá
        for check_y in range(iy+4, MAP_HEIGHT):
            center_x = ix + iw//2
            if center_x < MAP_WIDTH and MAP_GRID[check_y][center_x] == "G":
                MAP_GRID[check_y-1][center_x] = "J"
                break

# 3. Dekoráció és NPC
for x in range(10, MAP_WIDTH - 20):
    for y in range(1, MAP_HEIGHT):
        if MAP_GRID[y][x] == "G":
            if MAP_GRID[y-1][x] == ".":
                safe = True
                for c in range(max(0, x-2), min(MAP_WIDTH, x+3)):
                    if MAP_GRID[y-1][c] == "^": safe = False
                
                r = random.random()
                if safe and r > 0.95: MAP_GRID[y-1][x] = "M" # Tehén
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

# Célzóna lerakása (#)
MAP_GRID[11][MAP_WIDTH - 15] = "#"
MAP_GRID[12][MAP_WIDTH - 15] = "#"
for rx in range(MAP_WIDTH - 25, MAP_WIDTH):
    MAP_GRID[13][rx] = "G"
    for ry in range(14, MAP_HEIGHT): MAP_GRID[ry][rx] = "X"

MAP_GRID[6][5] = "S"

for x in range(MAP_WIDTH):
    if MAP_GRID[MAP_HEIGHT - 2][x] == ".":
        MAP_GRID[MAP_HEIGHT - 1][x] = "W"

MAP = ["".join(row) for row in MAP_GRID]

# ============================================================================
# TEXTÚRA GYÁR, ANIMÁCIÓK ÉS HÁTTÉR (PARALLAX)
# ============================================================================
class GraphicsFactory:
    _cache = {}
    
    @classmethod
    def get_parallax_bg(cls, name):
        if name in cls._cache: return cls._cache[name]
        surf = pygame.Surface((1200, 720), pygame.SRCALPHA)
        
        if name == "bg_mountains_far":
            pygame.draw.polygon(surf, (220, 200, 200), [(0, 720), (300, 200), (600, 720)])
            pygame.draw.polygon(surf, (200, 180, 180), [(400, 720), (700, 150), (1000, 720)])
            pygame.draw.polygon(surf, (230, 210, 210), [(800, 720), (1100, 250), (1300, 720)])
        elif name == "bg_mountains_near":
            pygame.draw.polygon(surf, (150, 160, 140), [(-100, 720), (200, 300), (500, 720)])
            pygame.draw.polygon(surf, (130, 140, 120), [(300, 720), (600, 250), (900, 720)])
            pygame.draw.polygon(surf, (160, 170, 150), [(700, 720), (950, 350), (1200, 720)])
            
            # Nagy fantasy szoborfej a hegyen
            pygame.draw.circle(surf, (140, 150, 130), (600, 250), 50)
            pygame.draw.rect(surf, (140, 150, 130), (570, 250, 60, 100))
        elif name == "bg_clouds":
            for _ in range(12):
                cx, cy = random.randint(0, 1200), random.randint(50, 250)
                pygame.draw.circle(surf, (255, 255, 255, 180), (cx, cy), random.randint(40, 80))
                pygame.draw.circle(surf, (255, 255, 255, 140), (cx+40, cy+20), random.randint(30, 60))
                pygame.draw.circle(surf, (255, 255, 255, 140), (cx-40, cy+10), random.randint(30, 60))
                
        cls._cache[name] = surf
        return surf

    @classmethod
    def get_texture(cls, name, frame=0):
        key = f"{name}_{frame}"
        if key in cls._cache: return cls._cache[key]
        
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # --- JÁTÉKOS ANIMÁCIÓ ---
        if name.startswith("player_"):
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200, 220, 255), (25, 20, 30, 40), border_radius=8)
            pygame.draw.rect(surf, (0, 255, 255), (35, 25, 20, 12), border_radius=4)
            pygame.draw.rect(surf, (100, 120, 150), (15, 25, 10, 30), border_radius=5)
            pygame.draw.rect(surf, (80, 80, 80), (45, 45, 25, 8), border_radius=2)
            pygame.draw.rect(surf, (0, 255, 200), (65, 46, 6, 6))
            
            if name == "player_idle":
                pygame.draw.rect(surf, (150, 170, 200), (28, 60, 10, 18)) 
                pygame.draw.rect(surf, (150, 170, 200), (42, 60, 10, 18)) 
            elif name == "player_walk_0":
                pygame.draw.rect(surf, (150, 170, 200), (35, 60, 10, 18)) 
            elif name == "player_walk_1":
                pygame.draw.rect(surf, (150, 170, 200), (20, 60, 10, 15)) 
                pygame.draw.rect(surf, (150, 170, 200), (50, 60, 10, 15))
            elif name == "player_jump":
                pygame.draw.rect(surf, (150, 170, 200), (25, 55, 12, 10))
                pygame.draw.rect(surf, (150, 170, 200), (43, 55, 12, 10))
                pygame.draw.polygon(surf, (255, 150, 0), [(15, 55), (20, 75), (25, 55)])
                pygame.draw.polygon(surf, (255, 255, 0), [(17, 55), (20, 65), (23, 55)])
            cls._cache[key] = surf
            return surf

        # --- ELLENSÉG ANIMÁCIÓ ---
        elif name == "enemy":
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            is_jumping = (frame == 2)
            if is_jumping:
                pygame.draw.rect(surf, (200, 40, 80), (12, 10, 40, 40), border_radius=15)
                pygame.draw.circle(surf, (0, 0, 0), (32, 25), 10)
                pygame.draw.circle(surf, (255, 255, 0), (35, 23), 4)
                pygame.draw.polygon(surf, (100, 100, 100), [(20, 50), (32, 40), (44, 50)])
            else:
                y_offset = 4 if frame % 2 == 0 else 0
                pygame.draw.rect(surf, (200, 40, 80), (12, 15 + y_offset, 40, 40), border_radius=15)
                pygame.draw.circle(surf, (0, 0, 0), (32, 30 + y_offset), 10)
                pygame.draw.circle(surf, (255, 255, 255), (35, 28 + y_offset), 4)
                pygame.draw.rect(surf, (100, 100, 100), (20, 55 + y_offset, 8, 9))
                pygame.draw.rect(surf, (100, 100, 100), (36, 55 + y_offset, 8, 9))
            cls._cache[key] = surf
            return surf

        # --- ÚJ: KIS HÁZIKÓ CÉL TEXTÚRA ---
        elif name == "house":
            surf = pygame.Surface((128, 160), pygame.SRCALPHA) # 2 tile széles, tágas kis házikó
            # Falak (Hangulatos kő és fa keverék)
            pygame.draw.rect(surf, (150, 130, 120), (20, 50, 88, 90), border_radius=6)
            # Gerendák az oldalakon
            pygame.draw.rect(surf, (90, 60, 40), (16, 50, 8, 90))
            pygame.draw.rect(surf, (90, 60, 40), (104, 50, 8, 90))
            # Ajtó (Ahova beérkezik a hős)
            pygame.draw.rect(surf, (80, 45, 25), (48, 85, 32, 55), border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.circle(surf, (255, 215, 0), (74, 112), 3) # Arany kilincs
            # Kerek ablak fényárban
            pygame.draw.circle(surf, (255, 255, 200), (64, 30), 14)
            pygame.draw.circle(surf, (90, 60, 40), (64, 30), 14, 2)
            pygame.draw.line(surf, (90, 60, 40), (64, 16), (64, 44), 2)
            pygame.draw.line(surf, (90, 60, 40), (50, 30), (78, 30), 2)
            # Brawlhalla tető (Íves, szép lila/piros fantasy tető)
            pygame.draw.polygon(surf, (180, 50, 70), [(0, 55), (64, 5), (128, 55)])
            pygame.draw.polygon(surf, (210, 70, 90), [(10, 50), (64, 12), (118, 50)])
            # Kémény füst részecskék nélkül, stabil rajzzal
            pygame.draw.rect(surf, (80, 75, 85), (90, 15, 16, 25))
            pygame.draw.rect(surf, (50, 45, 55), (86, 12, 24, 6))
            cls._cache[key] = surf
            return surf

        # --- TALAJ ÉS SZIGETEK ---
        if name == "grass_top":
            surf.fill(COLOR_DIRT)
            pygame.draw.rect(surf, COLOR_GRASS, (0, 0, TILE_SIZE, 16))
            pygame.draw.rect(surf, (80, 160, 80), (0, 16, TILE_SIZE, 4)) 
            if random.random() > 0.5: pygame.draw.rect(surf, (80, 160, 80), (10, 20, 4, 10))
            if random.random() > 0.5: pygame.draw.rect(surf, (80, 160, 80), (40, 20, 4, 15))
        elif name == "dirt" or name == "X":
            surf.fill(COLOR_DIRT)
            for _ in range(10): pygame.draw.rect(surf, (120, 80, 60), (random.randint(0, TILE_SIZE-8), random.randint(0, TILE_SIZE-8), 8, 8))
        elif name == "dirt_bottom" or name == "B":
            surf.fill((0,0,0,0))
            pygame.draw.rect(surf, COLOR_DIRT, (0, 0, TILE_SIZE, TILE_SIZE//2))
            pygame.draw.ellipse(surf, COLOR_DIRT, (0, -TILE_SIZE//2, TILE_SIZE, TILE_SIZE*1.5))
        elif name == "platform" or name == "P": 
            surf.fill((0,0,0,0))
            pygame.draw.rect(surf, COLOR_DIRT, (0, 16, TILE_SIZE, TILE_SIZE-16))
            pygame.draw.rect(surf, COLOR_GRASS, (0, 0, TILE_SIZE, 16), border_radius=8)
            if random.random() > 0.3: pygame.draw.rect(surf, (60, 160, 80), (10, 16, 4, 20))
            if random.random() > 0.3: pygame.draw.rect(surf, (60, 160, 80), (40, 16, 4, 30))
        elif name == "p": 
            surf.fill(COLOR_DIRT)
            pygame.draw.circle(surf, (110, 70, 60), (20, 20), 10)
            pygame.draw.circle(surf, (80, 140, 80), (50, 40), 8) 
        elif name == "b": 
            # Hatalmas, mélyre nyúló sziget tál aljzat
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLOR_DIRT, (0, 0, TILE_SIZE, TILE_SIZE))
            pygame.draw.ellipse(surf, (100, 70, 60), (-TILE_SIZE//2, 0, TILE_SIZE*2, TILE_SIZE*2.5))
            pygame.draw.ellipse(surf, (80, 50, 40), (0, TILE_SIZE//2, TILE_SIZE, TILE_SIZE*2))
            pygame.draw.line(surf, (60, 160, 80), (15, 0), (15, TILE_SIZE*1.8), 3)
            pygame.draw.line(surf, (60, 160, 80), (45, 0), (45, TILE_SIZE*1.3), 2)
            cls._cache[key] = surf
            return surf

        # --- DÍSZLETEK ---
        elif name == "tree":
            surf = pygame.Surface((TILE_SIZE*2, TILE_SIZE*4), pygame.SRCALPHA)
            pygame.draw.rect(surf, (90, 60, 40), (TILE_SIZE - 12, TILE_SIZE*1.5, 24, TILE_SIZE*2.5))
            pygame.draw.circle(surf, (80, 180, 80), (TILE_SIZE, TILE_SIZE*1.5), 45)
            pygame.draw.circle(surf, (100, 200, 100), (TILE_SIZE - 25, TILE_SIZE*1.5 + 25), 40)
            pygame.draw.circle(surf, (60, 160, 60), (TILE_SIZE + 25, TILE_SIZE*1.5 + 25), 40)
        elif name == "rock":
            pygame.draw.polygon(surf, (140, 140, 150), [(10, 64), (32, 20), (54, 64)])
            pygame.draw.polygon(surf, (170, 170, 180), [(10, 64), (32, 20), (40, 64)])
        elif name == "bush":
            pygame.draw.circle(surf, (70, 170, 70), (32, 44), 22); pygame.draw.circle(surf, (90, 190, 90), (20, 54), 16); pygame.draw.circle(surf, (50, 150, 50), (44, 54), 16)
            pygame.draw.circle(surf, (255, 100, 100), (25, 40), 3) 
            pygame.draw.circle(surf, (255, 100, 100), (45, 45), 3)
        elif name == "crate":
            surf.fill((120, 80, 50)); pygame.draw.rect(surf, (90, 50, 30), (0, 0, TILE_SIZE, TILE_SIZE), 6)
            pygame.draw.line(surf, (90, 50, 30), (0, 0), (TILE_SIZE, TILE_SIZE), 5); pygame.draw.line(surf, (90, 50, 30), (TILE_SIZE, 0), (0, TILE_SIZE), 5)
        elif name == "spike":
            pygame.draw.polygon(surf, (200, 200, 220), [(8, 64), (16, 15), (24, 64)])
            pygame.draw.polygon(surf, (180, 180, 200), [(24, 64), (32, 5), (40, 64)])
            pygame.draw.polygon(surf, (220, 220, 240), [(40, 64), (48, 20), (56, 64)])
        elif name == "trampoline":
            pygame.draw.rect(surf, (200, 100, 50), (10, 50, 44, 14), border_radius=4); pygame.draw.rect(surf, (255, 200, 50), (14, 46, 36, 6), border_radius=3)
            pygame.draw.line(surf, (150, 80, 40), (18, 50), (18, 58), 3); pygame.draw.line(surf, (150, 80, 40), (46, 50), (46, 58), 3)
        elif name == "cow":
            surf = pygame.Surface((int(TILE_SIZE * 1.5), TILE_SIZE), pygame.SRCALPHA)
            leg_y = 38 if frame in [0, 2] else 36 
            head_y = 8 if frame in [0, 1] else 32 
            pygame.draw.rect(surf, (200, 200, 200), (16, leg_y, 8, 26)); pygame.draw.rect(surf, (200, 200, 200), (32, 40 - leg_y + 36, 8, 26))
            pygame.draw.rect(surf, (200, 200, 200), (60, leg_y, 8, 26)); pygame.draw.rect(surf, (200, 200, 200), (76, 40 - leg_y + 36, 8, 26))
            pygame.draw.rect(surf, (240, 240, 240), (12, 16, 76, 28), border_radius=12)
            pygame.draw.circle(surf, (40, 40, 40), (30, 24), 8); pygame.draw.circle(surf, (40, 40, 40), (55, 32), 10); pygame.draw.circle(surf, (40, 40, 40), (70, 22), 7)
            pygame.draw.ellipse(surf, (255, 180, 180), (40, 40, 16, 10))
            pygame.draw.rect(surf, (240, 240, 240), (76, head_y, 22, 26), border_radius=6)
            pygame.draw.rect(surf, (255, 180, 180), (84, head_y+10, 14, 16), border_radius=4)
            pygame.draw.circle(surf, (0, 0, 0), (80, head_y+6), 3)
            pygame.draw.polygon(surf, (255, 255, 200), [(76, head_y), (72, head_y-10), (80, head_y)]); pygame.draw.polygon(surf, (255, 255, 200), [(86, head_y), (90, head_y-10), (82, head_y)])
        elif name == "steak":
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (150, 50, 20), (4, 10, 24, 14)); pygame.draw.ellipse(surf, (180, 70, 40), (6, 12, 20, 10))
            pygame.draw.rect(surf, (255, 240, 230), (2, 14, 6, 6), border_radius=2); pygame.draw.rect(surf, (255, 240, 230), (24, 14, 6, 6), border_radius=2)
        elif name == "water":
            surf.fill((100, 150, 255, 180)); pygame.draw.line(surf, (200, 230, 255, 220), (0, 2), (TILE_SIZE, 2), 2)

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
    def __init__(self, x, y, text, color=(255,255,255), life=50):
        self.x, self.y, self.text, self.color, self.life = x, y, text, color, life
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
        self.start_x, self.dir, self.speed, self.hp, self.alive, self.hit_timer = x, 1, 0.5, 15, True, 0
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
        if is_grazing: frame += 2 
        
        sprite = GraphicsFactory.get_texture("cow", frame)
        if self.dir == -1: sprite = pygame.transform.flip(sprite, True, False)
        if self.hit_timer > 0 and (self.hit_timer // 2) % 2 == 0: sprite = sprite.copy(); sprite.set_alpha(100)
        screen.blit(sprite, (self.rect.x - cam_x, self.rect.y - cam_y))
        
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x - cam_x + 10, self.rect.y - cam_y - 10, (self.rect.width-20) * (self.hp/15), 4))

class AdvancedEnemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.start_x, self.dir, self.speed, self.hp, self.alive, self.hit_timer, self.state = x, 1, 1.8, 8, True, 0, "patrol"
        self.sebesseg_y = 0
        self.foldon_van = False

    def take_damage(self, amount, kb_dir):
        if not self.alive or self.hit_timer > 0: return False
        self.hp -= amount; self.hit_timer = 10; self.rect.y -= 5; self.rect.x += kb_dir * 15
        if self.hp <= 0: self.alive = False
        return True

    def update(self, solid_blocks, player_rect):
        if not self.alive: return
        if self.hit_timer > 0: self.hit_timer -= 1
        
        self.sebesseg_y += GRAVITY
        if self.sebesseg_y > TERMINAL_VELOCITY: self.sebesseg_y = TERMINAL_VELOCITY
        self.rect.y += int(self.sebesseg_y)
        self.foldon_van = False
        
        for p in solid_blocks:
            if self.rect.colliderect(p):
                if self.sebesseg_y > 0:
                    self.rect.bottom = p.top; self.sebesseg_y = 0; self.foldon_van = True
                elif self.sebesseg_y < 0:
                    self.rect.top = p.bottom; self.sebesseg_y = 0

        dist = math.hypot(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery)
        if dist < 300 and abs(player_rect.y - self.rect.y) < 150:
            self.state, self.dir, self.speed = "chase", 1 if player_rect.centerx > self.rect.centerx else -1, 3.5
        else:
            self.state, self.speed = "patrol", 1.8
            if abs(self.rect.x - self.start_x) > 160: self.dir = -1 if self.rect.x > self.start_x else 1
            
        if self.hit_timer == 0:
            eredeti_x = self.rect.x
            self.rect.x += self.speed * self.dir
            
            utkozott_x = False
            for p in solid_blocks:
                if self.rect.colliderect(p):
                    utkozott_x = True
                    if self.dir == 1: self.rect.right = p.left
                    else: self.rect.left = p.right
            
            edge = pygame.Rect(self.rect.right + 5 if self.dir == 1 else self.rect.left - 5, self.rect.bottom + 4, 2, 2)
            has_ground = any(edge.colliderect(p) for p in solid_blocks)
            
            if utkozott_x and self.foldon_van:
                self.sebesseg_y = -15
                self.foldon_van = False
            elif not has_ground:
                self.dir *= -1
                self.start_x = self.rect.x

    def draw(self, screen, cam_x, cam_y):
        if not self.alive: return
        frame = 2 if not self.foldon_van else (pygame.time.get_ticks() // 150) % 2
            
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
        global SESSION_STATE
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
        
        self.coins = SESSION_STATE["coins"]
        hp_level = SESSION_STATE["skills"]["hp"]
        self.player_max_hp = 100 + (20 * hp_level)
        self.player_hp = self.player_max_hp
        self.player_invincible = 0
        
        self.has_double_jump = (SESSION_STATE["skills"]["dj"] == 1)
        self.jump_count = 0 
        self.coyote_timer = 0 
        self.player_damage = 1 + SESSION_STATE["skills"]["dmg"]
        
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
                elif cell == 'p': self.platforms.append(pygame.Rect(wx, wy, TILE_SIZE, 10)); self.decor.append(("p", wx, wy))
                elif cell == 'b': self.platforms.append(pygame.Rect(wx, wy, TILE_SIZE, 10)); self.decor.append(("b", wx, wy))
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
                elif cell == '#': 
                    self.goal = pygame.Rect(wx, wy, TILE_SIZE * 2, TILE_SIZE * 2.5) # Szélesebb és magasabb kapu hitbox a háznak

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
        self.player.sebesseg_y += GRAVITY
        if self.player.sebesseg_y > TERMINAL_VELOCITY: 
            self.player.sebesseg_y = TERMINAL_VELOCITY
        self.player.rect.y += int(self.player.sebesseg_y)
        
        self.player.foldon_van = False
        
        for p in self.solid_blocks:
            if self.player.rect.colliderect(p):
                if self.player.sebesseg_y > 0:
                    self.player.rect.bottom = p.top; self.player.sebesseg_y = 0; self.player.foldon_van = True
                elif self.player.sebesseg_y < 0:
                    self.player.rect.top = p.bottom; self.player.sebesseg_y = 0
                    
        for p in self.platforms:
            if self.player.rect.colliderect(p):
                if self.player.sebesseg_y > 0 and self.player.rect.bottom <= p.top + 16:
                    self.player.rect.bottom = p.top; self.player.sebesseg_y = 0; self.player.foldon_van = True
        
        if self.player.foldon_van:
            self.coyote_timer = 10 
            self.jump_count = 0
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1
                    
        eredeti_x = self.player.rect.x
        self.player.mozgas(keys)
        delta_x = self.player.rect.x - eredeti_x
        
        for p in self.solid_blocks:
            if self.player.rect.colliderect(p):
                if delta_x > 0: self.player.rect.right = p.left
                elif delta_x < 0: self.player.rect.left = p.right
                else: self.player.rect.x = eredeti_x

    def handle_jump_event(self):
        if self.coyote_timer > 0:
            self.player.sebesseg_y = self.player.ugras_ereje
            self.coyote_timer = 0
            self.jump_count = 1
        elif self.has_double_jump and self.jump_count < 2:
            self.player.sebesseg_y = self.player.ugras_ereje
            self.jump_count = 2
            self.spawn_particles(self.player.rect.centerx, self.player.rect.bottom, (0, 255, 255), 15, 3)

    def handle_shoot(self):
        if self.shoot_cooldown == 0:
            bx = self.player.rect.right if self.player.irany == 1 else self.player.rect.left - 16
            by = self.player.rect.centery - 4
            self.bullets.append(Bullet(bx, by, self.player.irany, self.player_damage))
            self.shoot_cooldown = 15
            self.spawn_particles(bx, by, (0, 255, 255), 6, 3)

    def update(self):
        global SESSION_STATE
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
                self.player.sebesseg_y = -24; self.jump_count = 0 
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
                            if COW_SOUNDS:
                                try: random.choice(COW_SOUNDS).play(maxtime=3000)
                                except: pass

        self.bullets = [b for b in self.bullets if b.active]
        
        for c in self.items:
            c.update()
            if c.active and self.player.rect.colliderect(c.rect):
                c.active = False
                if c.kind == "coin":
                    self.score += 50
                    self.coins += 50
                    SESSION_STATE["coins"] = self.coins 
                    self.float_texts.append(FloatingText(c.rect.x, c.rect.y - 10, "+50 Coin", (255, 215, 0)))
                    self.spawn_particles(c.rect.centerx, c.rect.centery, (255, 215, 0), 8)
                elif c.kind == "steak":
                    self.heal_player(int(self.player_max_hp * 0.20))
                    self.score += 100

        for e in self.enemies: e.update(self.solid_blocks, self.player.rect)

        if self.goal and self.player.rect.colliderect(self.goal):
            self.state = "won"
            save_progress_only(2)
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (50, 255, 50), 40, 8)

    def draw_parallax_bg(self, cx, cy):
        for y in range(self.sh):
            r = int(COLOR_SKY_TOP[0] * (1 - y/self.sh) + COLOR_SKY_BOT[0] * (y/self.sh))
            g = int(COLOR_SKY_TOP[1] * (1 - y/self.sh) + COLOR_SKY_BOT[1] * (y/self.sh))
            b = int(COLOR_SKY_TOP[2] * (1 - y/self.sh) + COLOR_SKY_BOT[2] * (y/self.sh))
            pygame.draw.line(self.screen, (r,g,b), (0, y), (self.sw, y))
            
        def draw_layer(texture_name, factor, y_offset=0):
            tex = GraphicsFactory.get_parallax_bg(texture_name)
            w = tex.get_width()
            offset_x = (cx * factor) % w
            for i in range(-1, (self.sw // w) + 2):
                self.screen.blit(tex, (i * w - offset_x, y_offset))
                
        draw_layer("bg_mountains_far", 0.1, 50)
        draw_layer("bg_mountains_near", 0.3, 150)
        draw_layer("bg_clouds", 0.15, 0)

    def draw_skill_tree(self, mouse_pos, clicked):
        global SESSION_STATE
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
            
            lvl = SESSION_STATE["skills"][sk_key]
            is_max = (lvl >= max_lvl)
            price = prices[lvl] if not is_max else 0
            can_afford = (self.coins >= price) and not is_max
            hover = rect.collidepoint(mouse_pos)
            
            bg_color = (20, 15, 40) if not hover else (30, 25, 55)
            if is_max: bg_color = (10, 40, 40)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=15)
            pygame.draw.rect(self.screen, (0, 255, 255), rect, 2, border_radius=15)
            
            self.screen.blit(font_norm.render(sk_name, True, (255, 255, 255)), (bx + 15, by + 15))
            self.screen.blit(font_sm.render(f"Szint: {lvl} / {max_lvl}", True, (0, 255, 255)), (bx + 15, by + 50))
            
            btn_rect = pygame.Rect(bx + 20, by + 90, box_w - 40, 50)
            btn_color, btn_txt, txt_color = (60, 60, 80), "MAX SZINT", (150, 150, 150)
            
            if not is_max:
                btn_txt = f"Vétel: {price} Coin"
                if can_afford:
                    btn_color, txt_color = ((0, 180, 255) if btn_rect.collidepoint(mouse_pos) else (0, 120, 200)), (0, 0, 0)
                    if clicked and btn_rect.collidepoint(mouse_pos):
                        self.coins -= price
                        SESSION_STATE["coins"] = self.coins
                        SESSION_STATE["skills"][sk_key] += 1
                        
                        if sk_key == "dj": self.has_double_jump = True
                        if sk_key == "dmg": self.player_damage += 1
                        if sk_key == "hp": self.player_max_hp += 20; self.player_hp += 20
                else: btn_color = (120, 40, 60)
                    
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
            tsurf = font_norm.render(btn_txt, True, txt_color)
            self.screen.blit(tsurf, (btn_rect.centerx - tsurf.get_width()//2, btn_rect.centery - tsurf.get_height()//2))

        esc_txt = font_norm.render("Nyomd meg a 'T' vagy 'ESC' gombot a kilépéshez", True, (0, 255, 255))
        self.screen.blit(esc_txt, (self.sw//2 - esc_txt.get_width()//2, self.sh - 100))

    def draw(self):
        sx = random.randint(-2, 2) if self.shake_timer > 0 else 0
        sy = random.randint(-2, 2) if self.shake_timer > 0 else 0
        cx, cy = int(self.cam_x) + sx, int(self.cam_y) + sy

        self.draw_parallax_bg(cx, cy)

        for kind, wx, wy in self.decor:
            if cx - TILE_SIZE*2 < wx < cx + self.sw and cy - TILE_SIZE*3 < wy < cy + self.sh:
                self.screen.blit(GraphicsFactory.get_texture(kind), (wx - cx, wy - cy))

        # --- CÉL HÁZIKÓ RAJZOLÁSA ---
        if self.goal:
            hx = self.goal.x - cx - TILE_SIZE // 2
            hy = self.goal.y - cy - TILE_SIZE // 2
            self.screen.blit(GraphicsFactory.get_texture("house"), (hx, hy))

        for cow in self.cows: cow.draw(self.screen, cx, cy)
        for c in self.items: c.draw(self.screen, cx, cy)
        for e in self.enemies: e.draw(self.screen, cx, cy)
        for b in self.bullets: b.draw(self.screen, cx, cy)
        
        if self.state != "dead":
            if self.player_invincible == 0 or (self.player_invincible // 4) % 2 == 0:
                if not self.player.foldon_van: p_state = "player_jump"
                else:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]:
                        p_state = f"player_walk_{(pygame.time.get_ticks() // 150) % 2}"
                    else: p_state = "player_idle"
                        
                sprite = GraphicsFactory.get_texture(p_state)
                if self.player.irany == -1: sprite = pygame.transform.flip(sprite, True, False)
                
                px = self.player.rect.centerx - cx - 40 
                py = self.player.rect.bottom - cy - 80
                self.screen.blit(sprite, (px, py))

        for p in self.particles: p.draw(self.screen, cx, cy)
        for f in self.float_texts: f.draw(self.screen, cx, cy)

        pygame.draw.rect(self.screen, (10, 5, 20, 200), (20, 20, 320, 130), border_radius=10)
        pygame.draw.rect(self.screen, (0, 255, 255), (20, 20, 320, 130), 2, border_radius=10)
        
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