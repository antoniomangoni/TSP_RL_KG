import pygame
import os 

class Entity(pygame.sprite.Sprite):
    _images = {}

    def __init__(self, x, y, art, tile_size):
        super().__init__()
        # Ensure the image is loaded
        if art not in self._images:
            full_path = f'Pixel_Art/{art}'
            if os.path.exists(full_path):  
                self._images[art] = pygame.transform.scale(pygame.image.load(full_path), (tile_size, tile_size))
            else:
                raise FileNotFoundError(f"Image file {art} not found in Pixel_Art directory.")
        
        self.image = self._images[art]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tile_x = x // tile_size
        self.tile_y = y // tile_size
        self.tile_size = tile_size

        self.entity_code = None
        print(f"Size of entity image: {self.image.get_size()}")

    def move(self, dx, dy):
        self.rect.x += dx * self.tile_size
        self.rect.y += dy * self.tile_size
        self.tile_x += dx
        self.tile_y += dy

    def move(self, dx, dy):
        """
        Moves the entity by dx, dy tiles, rather than pixel coordinates.
        """
        # Update the pixel position
        self.rect.x += dx * self.tile_size
        self.rect.y += dy * self.tile_size
        # Update the logical tile position
        self.tile_x += dx
        self.tile_y += dy


class Player(Entity):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='player.png', tile_size=tile_size)
        self.entity_code = 7
        self.tile_size = tile_size
        self.x = x // tile_size
        self.y = y // tile_size

    def move(self, dx, dy):
        self.rect.x += dx * self.tile_size 
        self.rect.y += dy * self.tile_size
        self.x += dx
        self.y += dy

class Outpost(Entity):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='outpost_2.png', tile_size=tile_size)
        self.entity_code = 6

class WoodPath(Entity):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='wood_path.png', tile_size=tile_size)
        self.entity_code = 5

class Fish(Entity):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='fish.png', tile_size=tile_size)
        self.entity_code = 0

class Tree(Entity):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='tree_1.png', tile_size=tile_size)
        self.entity_code = 1

class Rock(Entity):
    def __init__(self, x, y, art, tile_size):
        super().__init__(x, y, art, tile_size)
        self.entity_code = 2

class MossyRock(Rock):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='rock_moss.png', tile_size=tile_size)
        self.entity_code = 3

class SnowyRock(Rock):
    def __init__(self, x, y, tile_size):
        super().__init__(x, y, art='rock_snow.png', tile_size=tile_size)
        self.entity_code = 4