import pygame
import math
import random

def show_loading(screen):

    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("arial", 70)
    font_small = pygame.font.SysFont("arial", 30)

    width = screen.get_width()
    height = screen.get_height()

    progress = 0
    angle = 0
    dots = 0
    dot_timer = 0

    particles = []
    for i in range(40):
        particles.append([
            random.randint(0,width),
            random.randint(0,height),
            random.uniform(0.5,2)
        ])

    while progress < 100:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((10,10,20))

        for p in particles:
            p[1] += p[2]
            if p[1] > height:
                p[1] = 0
                p[0] = random.randint(0,width)

            pygame.draw.circle(screen,(60,60,120),(int(p[0]),int(p[1])),2)

        dot_timer += 1
        if dot_timer > 20:
            dots = (dots + 1) % 4
            dot_timer = 0

        text = font_big.render("Betöltés" + "." * dots, True, (255,255,255))
        text_rect = text.get_rect(center=(width/2, height/2 - 140))
        screen.blit(text, text_rect)

        percent = font_small.render(f"{int(progress)}%",True,(0,255,150))
        percent_rect = percent.get_rect(center=(width/2,height/2 + 120))
        screen.blit(percent,percent_rect)

        circle_x = width / 2
        circle_y = height / 2

        for i in range(12):

            a = angle + i * (math.pi*2/12)

            x = circle_x + math.cos(a) * 60
            y = circle_y + math.sin(a) * 60

            size = 4 + i % 3

            color = (0, 150 + i*8, 255)

            pygame.draw.circle(screen,color,(int(x),int(y)),size)

        angle += 0.08

        bar_width = 500
        bar_height = 30

        bar_x = width/2 - bar_width/2
        bar_y = height/2 + 75

        pygame.draw.rect(screen,(50,50,70),(bar_x,bar_y,bar_width,bar_height),border_radius=15)

        progress_width = bar_width * (progress/100)

        pygame.draw.rect(screen,(0,255,150),(bar_x,bar_y,progress_width,bar_height),border_radius=15)


        pygame.draw.rect(screen,(0,200,120),(bar_x-2,bar_y-2,bar_width+4,bar_height+4),2,border_radius=15)

        progress += 0.4

        pygame.display.update()
        clock.tick(60)