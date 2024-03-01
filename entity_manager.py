import numpy as np
import random
import pygame
from typing import Dict, Type
from terrain_manager import TerrainManager
from helper_functions import time_function, debug_function
from entities import Entity, Player, Outpost

class EntityManager:
    @time_function
    def __init__(self, terrain_manager: TerrainManager,
                 entity_map: Dict[str, int],
                 terrain_entity_map: Dict[int, int],
                 entity_classes: np.ndarray[Type[Entity]],
                 spawn_probs: np.ndarray[float],
                 tile_size: int = 50,
                 number_of_outposts: int = 3,
                 outpost_terrain: list[int] = [2, 3]):
        
        self.terrain_manager = terrain_manager
        self.width = terrain_manager.width
        self.height = terrain_manager.height
        self.entity_locations = np.full((self.width, self.height), 0, dtype=np.uint8)
        self.entity_map = entity_map
        self.terrain_entity_map = terrain_entity_map
        self.entity_classes = entity_classes
        self.spawn_probs = spawn_probs
        self.entity_group = pygame.sprite.Group()
        self.tile_size = tile_size
        self.number_of_outposts = number_of_outposts
        self.outpost_terrain = outpost_terrain
        self.min_outpost_distance = max(self.width, self.height) // self.number_of_outposts  # Adjust this formula as needed
        self.failed = False

        self.player = Player

        self.populate_tiles()
        self.add_player()
        self.add_outposts(self.min_outpost_distance)
        print(self.player)
        
    @time_function
    def update(self, events):
        self.player.update(events)

    @time_function
    def move_player(self, direction: str):
        dx, dy = 0, 0
        if direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1
        elif direction == "UP":
            dy = -1
        elif direction == "DOWN":
            dy = 1
        
        next_x, next_y = self.player.x + dx, self.player.y + dy
        
        # Check if the next position is within the bounds of the game world
        if self.check_location_viability(self.player.x, self.player.y, dx, dy):
            print('Moving player')
            self.player.move(dx, dy)
            self.entity_locations[self.player.y, self.player.x] = 0
            self.entity_locations[next_y, next_x] = self.entity_map['player']
            self.player.x, self.player.y = next_x, next_y

            return True
        else:
            print("Cannot move out of bounds")
            return False
    @time_function
    def check_location_viability(self, x, y, dx, dy):
        if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
            print('In bounds')
            return self.entity_locations[y + dy, x + dx] == 0
        return False

    @time_function
    def destroy_entity(self, x, y):
        entity_type = self.entity_locations[x, y]
        self.entity_locations[x, y] = 0
        self.entity_group.remove(self.entity_group.sprites()[entity_type])

    @time_function
    def populate_tiles(self):
        self.entity_group.empty()
        for x in range(self.width):
            for y in range(self.height):
                # Use heightmap from TerrainManager to get terrain code
                terrain_code = self.terrain_manager.heightmap[x, y]
                # Get the entity type which spawns on this terrain
                entity_type = self.terrain_entity_map.get(terrain_code) -1 
                if entity_type is not None and random.random() < self.spawn_probs[entity_type]: 
                    # Add entity type to the entity locations array for processing
                    self.entity_locations[x, y] = entity_type
                    # Get entity type from its one hot encoding and spawn it
                    self.create_entity(self.entity_classes[entity_type], x, y)

    @time_function
    def create_entity(self, entity_class: Entity, x: int, y: int):
        # print(f'Creating entity {entity_type} at ({x}, {y}))
        pixel_x, pixel_y = x * self.tile_size, y * self.tile_size
        entity = entity_class(pixel_x, pixel_y, self.tile_size)
        self.entity_group.add(entity) # Add entity to the sprite group for rendering
        return entity

    @time_function
    def add_player(self):
        empty_tiles = np.argwhere(self.entity_locations == 0)
        if empty_tiles.size == 0:
            self.replace_entity_for_player([2, 3])
            return
        # get empty tiles where the terrain_code == 2 or 3
        empty_tiles = [tile for tile in empty_tiles if self.terrain_manager.heightmap[tile[0], tile[1]] in [2, 3]]       

        # print(f'Entity locations: {self.entity_locations}')
        player_location = random.choice(empty_tiles)
        self.entity_locations[player_location[0], player_location[1]] = self.entity_map['player']
        self.player = self.create_entity(Player, player_location[0], player_location[1])

    @time_function
    def replace_entity_for_player(self, entity_type: list[int]):
        for entity in entity_type:
                # get the first occurence of the entity type in the entity locations array
            entity_location = np.argwhere(self.entity_locations == entity)[0]
            if entity_location.size > 0:
                break

            self.entity_locations[entity_location[0], entity_location[1]] = 0
            self.player = self.create_entity(Player, entity_location[0], entity_location[1])

    @time_function
    def add_outposts(self, min_distance: int = 5):
        # print(f'Adding {self.number_of_outposts} outposts at least {min_distance} tiles apart.')
        outpost_locations = []

        empty_tiles = np.argwhere((self.entity_locations == 0) & np.isin(self.terrain_manager.heightmap, self.outpost_terrain))

        if len(empty_tiles) < self.number_of_outposts:
            self.failed = True
            return

        # Randomly select the first outpost location
        first_outpost_location = random.choice(empty_tiles)
        outpost_locations.append(first_outpost_location)
        # Remove the first outpost location from the list of empty tiles
        empty_tiles = np.array([tile for tile in empty_tiles if not np.array_equal(tile, first_outpost_location)])

        # Attempt to place remaining outposts ensuring they are at least minimum_distance apart
        while len(outpost_locations) < self.number_of_outposts and len(empty_tiles) > 0:
            valid_tiles = [tile for tile in empty_tiles if all(np.linalg.norm(tile - outpost) >= min_distance for outpost in outpost_locations)]
            if not valid_tiles:
                # Reduce minimum distance if no valid tiles are found and try again
                min_distance -= 1
                continue

            new_outpost_location = random.choice(valid_tiles)
            outpost_locations.append(new_outpost_location)
            # Remove the new outpost location from the list of empty tiles
            empty_tiles = np.array([tile for tile in empty_tiles if not np.array_equal(tile, new_outpost_location)])

        if len(outpost_locations) < self.number_of_outposts:
            self.failed = True
            print('Failed to add all outposts due to insufficient spacing.')
            return

        # Create outposts at selected locations
        for location in outpost_locations:
            self.entity_locations[location[0], location[1]] = self.entity_map['outpost']
            self.create_entity(Outpost, location[0], location[1])
            # print(f'Outpost added at {location}')

    # @time_function
    # def move_player(self, direction: str):
    #    self.player.move(*self.player.handle_player_moved(direction))