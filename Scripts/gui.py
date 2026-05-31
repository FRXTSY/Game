import pygame
import sys

def show_menu(screen):
    pygame.display.set_caption("2D Dungeon - Főmenü")
    
    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    button_font = pygame.font.SysFont("Arial", 40, bold=True)
    
    width = screen.get_width()
    height = screen.get_height()
    
    button_width = 280
    button_height = 70
    spacing = 30
    
    hover_scale = 1.05  
    
    while True:
        screen.fill((20, 20, 40))  
        
        time = pygame.time.get_ticks() / 500
        pulse = 1 + abs(pygame.math.Vector2(0, 1).rotate(time).y) * 0.03
        title_surface = title_font.render("2D Dungeon", True, (255, 215, 0)) 
        title_width, title_height = title_surface.get_size()
        scaled_title = pygame.transform.scale(title_surface, (int(title_width * pulse), int(title_height * pulse)))
        title_rect = scaled_title.get_rect(center=(width/2, height/4))
        screen.blit(scaled_title, title_rect)
        
        for i in range(50):
            x = (i * 131) % width
            y = (i * 253 + pygame.time.get_ticks() * 0.2) % height
            pygame.draw.circle(screen, (100, 100, 150), (int(x), int(y)), 1)
        
        mouse_pos = pygame.mouse.get_pos()
        
        buttons = {
            "play": pygame.Rect(width/2 - button_width/2, height/2 - button_height - spacing, button_width, button_height),
            "settings": pygame.Rect(width/2 - button_width/2, height/2, button_width, button_height),
            "quit": pygame.Rect(width/2 - button_width/2, height/2 + button_height + spacing, button_width, button_height)
        }
        
       
        for key, rect in buttons.items():
            is_hover = rect.collidepoint(mouse_pos)
            
          
            if is_hover:
                current_width = int(button_width * hover_scale)
                current_height = int(button_height * hover_scale)
                current_rect = pygame.Rect(rect.centerx - current_width//2, rect.centery - current_height//2, current_width, current_height)
            else:
                current_width, current_height = button_width, button_height
                current_rect = rect
            
          
            if key == "play":
                base_color = (50, 150, 50) 
                hover_color = (80, 200, 80)
                text = "Játék"
            elif key == "settings":
                base_color = (50, 100, 200) 
                hover_color = (80, 150, 255)
                text = "Beállítások"
            else: 
                base_color = (180, 50, 50)   
                hover_color = (220, 80, 80)
                text = "Kilépés"
            
            color = hover_color if is_hover else base_color
            
           
            shadow_rect = current_rect.inflate(6, 6)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)
            
            
            pygame.draw.rect(screen, color, current_rect, border_radius=12)
            
           
            if is_hover:
                pygame.draw.rect(screen, (255, 255, 255), current_rect, 3, border_radius=12)
            
          
            text_surf = button_font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=current_rect.center)
            screen.blit(text_surf, text_rect)
        
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if key == "quit":
                            pygame.quit()
                            sys.exit()
                        return key  
        
        pygame.display.update()