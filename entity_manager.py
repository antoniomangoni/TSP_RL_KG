import random
import pygame
import numpy as np

from terrain_manager import TerrainManager
from entities import Player, Outpost, WoodPath
from terrains import Plains, Hills

class EntityManager: 
    def __init__(self, terrain_manager: TerrainManager, number_of_outposts: int = 3):
        self.terrain_manager = terrain_manager
        self.width, self.height = terrain_manager.width, terrain_manager.height
        self.entity_grid = np.empty((self.width, self.height), dtype=object)
        self.entity_index_grid = np.zeros((self.width, self.height), dtype=int)
        self.tile_size = terrain_manager.tile_size
        self.entity_group = pygame.sprite.Group()
        self.number_of_outposts = number_of_outposts
        self.outpost_terrain = [Plains, Hills]
        self.populate_tiles()
        self.add_outposts()

    def populate_tiles(self):
        # Iterate through the terrain grid to spawn entities based on terrain type
        for x in range(self.width):
            for y in range(self.height):
                entity = self.terrain_manager.terrain_object_grid[x, y].spawn_entity()
                if entity:
                    self.entity_grid[x, y] = entity
                    self.entity_index_grid[x, y] = entity.entity_code
                    self.entity_group.add(entity)

    def add_outposts(self):
        added_outposts = 0
        attempts = 0
        max_attempts = self.width * self.height * 2  # Arbitrary limit to prevent infinite loops

        while added_outposts < self.number_of_outposts and attempts < max_attempts:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            terrain_tile = self.terrain_manager.terrain_object_grid[x][y]

            # Check if the tile's terrain is suitable for an outpost
            if isinstance(terrain_tile, (Plains, Hills)) and terrain_tile.entity_on_tile is None:
                outpost = Outpost(x * self.tile_size, y * self.tile_size, self.tile_size)
                self.entity_group.add(outpost)
                terrain_tile.entity_on_tile = outpost
                terrain_tile.passable = False  # Mark the tile as impassable due to the outpost
                added_outposts += 1
            attempts += 1

        if attempts >= max_attempts:
            print(f"Warning: Only {added_outposts} outposts were added. Could not find suitable locations for all outposts.")


    def is_move_valid(self, x: int, y: int) -> bool:
        # Implement logic to check if a move is valid (e.g., within game bounds, not blocked by terrain)
        return 0 <= x < self.width and 0 <= y < self.height and self.terrain_manager.is_passable(x, y)


    def update_terrain_passability(self, x, y, entity):
        terrain = self.terrain_manager.terrain_grid[x][y]
        if isinstance(entity, WoodPath):
            terrain.passable = True
            terrain.energy_requirement = max(0, terrain.energy_requirement - 2)  # Ensure it doesn't go below 0
        else:
            terrain.passable = False
            terrain.entity_on_tile = entity

    def move_player(self, player: Player, direction: str):
        dx, dy = 0, 0
        if direction == "LEFT": dx = -1
        elif direction == "RIGHT": dx = 1
        elif direction == "UP": dy = -1
        elif direction == "DOWN": dy = 1

        next_x, next_y = player.tile_x + dx, player.tile_y + dy

        if self.is_move_valid(next_x, next_y):
            # Update the terrain passability of the current position
            current_terrain = self.terrain_manager.terrain_grid[player.tile_x][player.tile_y]
            if current_terrain.entity_on_tile == player:
                current_terrain.passable = True  # Assuming player's previous position becomes passable
                current_terrain.entity_on_tile = None

            player.move(dx, dy)
            # Reflect player's movement on the new terrain tile
            self.update_terrain_passability(next_x, next_y, player)
