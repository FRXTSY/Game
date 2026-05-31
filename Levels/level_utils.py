import pygame

TILE = 50


def build_level(map_data, player):
    platformok = []
    kapu = None

    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):

            world_x = x * TILE
            world_y = y * TILE

            if cell == "X":
                platformok.append(
                    pygame.Rect(world_x, world_y, TILE, TILE)
                )

            elif cell == "P":
                player.rect.x = world_x
                player.rect.y = world_y

            elif cell == "G":
                kapu = pygame.Rect(world_x, world_y, TILE, TILE)

    return platformok, kapu
