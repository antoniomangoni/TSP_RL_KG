import pygame

from terrain_manager import TerrainManager
from entity_manager import EntityManager

class Renderer:
    def __init__(self, terrain_manager: TerrainManager, entity_manager: EntityManager):
        self.terrain_manager = terrain_manager
        self.entity_manager = entity_manager
        self.tile_size = terrain_manager.tile_size
        self.surface = pygame.display.set_mode((terrain_manager.width * self.tile_size, terrain_manager.height * self.tile_size))
        self.terrain_surface = pygame.Surface(self.surface.get_size())
        self.terrain_surface.set_alpha(None)
        self.terrain_needs_update = True

    def render_terrain(self):
        if self.terrain_needs_update:
            print("Rendering terrain")
            for x in range(self.terrain_manager.width):
                for y in range(self.terrain_manager.height):
                    terrain_tile = self.terrain_manager.terrain_object_grid[x, y]
                    self.terrain_surface.blit(terrain_tile.image, (x * self.tile_size, y * self.tile_size))
            self.terrain_needs_update = False

    def render(self):
        self.surface.blit(self.terrain_surface, (0, 0))
        print(f"Number of entities to render: {len(self.entity_manager.entity_group)}")
        self.entity_manager.entity_group.draw(self.surface)
        pygame.display.flip()

    def update_tile(self, x, y):
        # Directly access and redraw the terrain tile
        terrain_tile = self.terrain_manager.terrain_object_grid[x, y]
        self.terrain_surface.blit(terrain_tile.image, (x * self.tile_size, y * self.tile_size))

        # Redraw the entity if present on this tile
        if terrain_tile.entity_on_tile is not None:
            entity = terrain_tile.entity_on_tile
            self.surface.blit(entity.image, (x * self.tile_size, y * self.tile_size))
