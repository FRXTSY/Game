import pygame
import sys

def show_settings(screen):
    pygame.display.set_caption("2D Dungeon - Beállítások")
    
    title_font = pygame.font.SysFont("Arial", 70, bold=True)
    button_font = pygame.font.SysFont("Arial", 40, bold=True)
    option_font = pygame.font.SysFont("Arial", 35)
    
    width = screen.get_width()
    height = screen.get_height()
    
    fullscreen = True 
    volume = 0.7  
    
    button_width = 300
    button_height = 60
    spacing = 25
    
    hover_scale = 1.05
    
    back_button = pygame.Rect(50, height - 100, 150, 50)
    
    while True:
        screen.fill((20, 20, 40))  
        
        title = title_font.render("Beállítások", True, (255, 215, 0))  
        title_rect = title.get_rect(center=(width/2, 100))
        screen.blit(title, title_rect)
        
        for i in range(50):
            x = (i * 131) % width
            y = (i * 253 + pygame.time.get_ticks() * 0.2) % height
            pygame.draw.circle(screen, (100, 100, 150), (int(x), int(y)), 1)
        
        mouse_pos = pygame.mouse.get_pos()
        
        fs_rect = pygame.Rect(width/2 - button_width/2, height/2 - 80, button_width, button_height)
        fs_hover = fs_rect.collidepoint(mouse_pos)
        fs_color = (80, 150, 255) if fs_hover else (50, 100, 200)
        
        
        fs_shadow = fs_rect.inflate(6, 6)
        pygame.draw.rect(screen, (0, 0, 0, 100), fs_shadow, border_radius=12)
        pygame.draw.rect(screen, fs_color, fs_rect, border_radius=12)
        
        if fs_hover:
            pygame.draw.rect(screen, (255, 255, 255), fs_rect, 3, border_radius=12)
        
        fs_text = f"Teljes képernyő: {'BE' if fullscreen else 'KI'}"
        fs_surf = option_font.render(fs_text, True, (255, 255, 255))
        fs_text_rect = fs_surf.get_rect(center=fs_rect.center)
        screen.blit(fs_surf, fs_text_rect)
        
        vol_rect = pygame.Rect(width/2 - button_width/2, height/2 + 20, button_width, button_height)
        vol_hover = vol_rect.collidepoint(mouse_pos)
        vol_color = (80, 150, 255) if vol_hover else (50, 100, 200)
        
        
        vol_shadow = vol_rect.inflate(6, 6)
        pygame.draw.rect(screen, (0, 0, 0, 100), vol_shadow, border_radius=12)
        pygame.draw.rect(screen, vol_color, vol_rect, border_radius=12)
        
        if vol_hover:
            pygame.draw.rect(screen, (255, 255, 255), vol_rect, 3, border_radius=12)
        
        vol_percent = int(volume * 100)
        vol_text = f"Hangerő: {vol_percent}%"
        vol_surf = option_font.render(vol_text, True, (255, 255, 255))
        vol_text_rect = vol_surf.get_rect(center=vol_rect.center)
        screen.blit(vol_surf, vol_text_rect)
        
        slider_width = 400
        slider_height = 10
        slider_x = width/2 - slider_width/2
        slider_y = height/2 + 100
        
        
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height), border_radius=5)
        
        filled_width = slider_width * volume
        pygame.draw.rect(screen, (80, 150, 255), (slider_x, slider_y, filled_width, slider_height), border_radius=5)
        
        
        knob_x = slider_x + filled_width - 10
        knob_rect = pygame.Rect(knob_x, slider_y - 10, 20, 30)
        pygame.draw.rect(screen, (255, 215, 0), knob_rect, border_radius=10)
        
       
        back_hover = back_button.collidepoint(mouse_pos)
        back_color = (180, 50, 50) if back_hover else (150, 40, 40)
        
       
        back_shadow = back_button.inflate(6, 6)
        pygame.draw.rect(screen, (0, 0, 0, 100), back_shadow, border_radius=12)
        pygame.draw.rect(screen, back_color, back_button, border_radius=12)
        
        if back_hover:
            pygame.draw.rect(screen, (255, 255, 255), back_button, 3, border_radius=12)
        
        back_text = button_font.render("Vissza", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if fs_rect.collidepoint(mouse_pos):
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                    width = screen.get_width()
                    height = screen.get_height()
                    back_button = pygame.Rect(50, height - 100, 150, 50)
                
                if vol_rect.collidepoint(mouse_pos):
                    volume += 0.1
                    if volume > 1.0:
                        volume = 0.0
                    volume = round(volume, 1)
                
               
                if knob_rect.collidepoint(mouse_pos) or (slider_x <= mouse_pos[0] <= slider_x + slider_width and slider_y - 10 <= mouse_pos[1] <= slider_y + 30):
                   
                    relative_x = max(0, min(slider_width, mouse_pos[0] - slider_x))
                    volume = relative_x / slider_width
                    volume = round(volume, 1)
                
               
                if back_button.collidepoint(mouse_pos):
                    return "back"
            
        
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  
                    if slider_x <= mouse_pos[0] <= slider_x + slider_width and slider_y - 20 <= mouse_pos[1] <= slider_y + 30:
                        relative_x = max(0, min(slider_width, mouse_pos[0] - slider_x))
                        volume = relative_x / slider_width
                        volume = round(volume, 1)
        
        pygame.display.update()