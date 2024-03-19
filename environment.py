import random
import pygame
import numpy as np

from entities import Player, Outpost, WoodPath
from terrains import Terrain, DeepWater, Water, Plains, Hills, Mountains, Snow

class Environment:
    def __init__(self, heightmap: np.ndarray, tile_size: int = 50, number_of_outposts: int = 3):
        self.heightmap = heightmap
        self.terrain_index_grid = np.zeros_like(self.heightmap)
        self.entity_index_grid = np.zeros_like(self.heightmap)
        self.terrain_object_grid = np.zeros_like(self.heightmap, dtype=object)
        self.changed_tiles_grid = np.full_like(self.heightmap, False)
        self.tile_size = tile_size
        self.width, self.height = heightmap.shape
        self.number_of_outposts = number_of_outposts
        self.entity_group = pygame.sprite.Group()
        self.terrain_definitions = {
            0: {'class': DeepWater, 'entity_prob': 0.4},
            1: {'class': Water, 'entity_prob': 0.3},
            2: {'class': Plains, 'entity_prob': 0.3},
            3: {'class': Hills, 'entity_prob': 0.4},
            4: {'class': Mountains, 'entity_prob': 0.4},
            5: {'class': Snow, 'entity_prob': 0.4},
        }

        self.suitable_terrain_locations = {'Plains': [], 'Hills': []}
        self.outpost_locations = [] # List of (x, y) coordinates for each outpost, no need to use an array here

        self.initialize_environment()
        self.add_outposts()
        self.player = self.add_player()

    def initialize_environment(self):
        for (x, y), terrain_code in np.ndenumerate(self.heightmap):
            self.terrain_index_grid[x, y] = terrain_code
            terrain_info = self.terrain_definitions.get(terrain_code)
            if terrain_info:
                terrain_class = terrain_info['class']
                entity_prob = terrain_info['entity_prob']
                # Instantiate the terrain with its corresponding properties
                self.terrain_object_grid[x, y] = terrain_class(x, y, self.tile_size, entity_prob)
                # Add entity to terrain if entity_prob is met
                self.add_entity(self.terrain_object_grid[x, y], x, y)

            else:
                raise ValueError(f"Invalid terrain code: {terrain_code}")
    
    def add_entity(self, terrain, x, y):
        if random.random() < terrain.entity_prob:
            entity_type = terrain.entity_type
            entity = entity_type(x, y, self.tile_size)
            self.entity_group.add(entity)
            self.entity_index_grid[x, y] = entity.id
            self.terrain_object_grid[x, y].add_entity(entity)
        else:
            if isinstance(terrain, Plains):
                self.suitable_terrain_locations['Plains'].append((x, y))
            elif isinstance(terrain, Hills):
                self.suitable_terrain_locations['Hills'].append((x, y))

    def add_outposts(self):
        possible_locations = self.suitable_terrain_locations['Plains'] + self.suitable_terrain_locations['Hills']
        selected_locations = random.sample(possible_locations, min(len(possible_locations), self.number_of_outposts))

        for x, y in selected_locations:
            outpost = Outpost(x, y, self.tile_size)
            self.entity_group.add(outpost)
            self.terrain_object_grid[x, y].entity_on_tile = outpost
            self.terrain_object_grid[x, y].passable = False
            self.outpost_locations.append((x, y))
            self.entity_index_grid[x, y] = outpost.id

            # remove the location from the list of suitable locations
            if (x, y) in self.suitable_terrain_locations['Plains']:
                self.suitable_terrain_locations['Plains'].remove((x, y))
            else:
                self.suitable_terrain_locations['Hills'].remove((x, y))

        print(f"Added {len(self.outpost_locations)} outposts.")
        return possible_locations

    def add_player(self):
        location = random.choice(self.suitable_terrain_locations['Plains'] + self.suitable_terrain_locations['Hills'])
        player = Player(location[0], location[1], self.tile_size)
        self.entity_group.add(player)
        self.entity_index_grid[location[0], location[1]] = player.id
        return player

    
    def update_terrain_passability(self, x, y, entity):
        terrain = self.terrain_object_grid[x, y]
        if isinstance(entity, WoodPath):
            terrain.passable = True
            terrain.energy_requirement = max(0, terrain.energy_requirement - 2)

    def mark_tile_as_changed(self, x, y):
        self.changed_tiles_grid[x, y] = True
    
    def move_entity(self, entity, new_x, new_y):
        if not self.is_move_valid(new_x, new_y):
            return
        old_x, old_y = entity.x, entity.y
        self.terrain_object_grid[old_x, old_y] = 0
        self.entity_index_grid[old_x, old_y] = 0
        entity.move(new_x, new_y)
        self.terrain_object_grid[new_x, new_y] = entity
        self.entity_index_grid[new_x, new_y] = entity.id
        self.mark_tile_as_changed(old_x, old_y)
        self.mark_tile_as_changed(new_x, new_y)

    def is_move_valid(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and self.terrain_object_grid[x, y].passable
