import pygame
import numpy as np 

from terrains import DeepWater, Water, Plains, Hills, Mountains, Snow  # Assuming terrains.py contains the Terrain classes
from entities import Tree, MossyRock  

class TerrainManager:
    def __init__(self, heightmap: np.ndarray, tile_size: int = 50):
        self.heightmap = heightmap
        self.tile_size = tile_size
        self.width, self.height = heightmap.shape
        self.terrain_types = [DeepWater, Water, Plains, Hills, Mountains, Snow]
        self.entity_init_prob = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.terrain_object_grid = self.initialize_terrain()

    def initialize_terrain(self):
        terrain_grid = np.empty((self.width, self.height), dtype=object)
        for x in range(self.width):
            for y in range(self.height):
                entity_prob = self.entity_init_prob[self.heightmap[x, y]]
                terrain_grid[x, y] = self.terrain_types[self.heightmap[x, y]](x * self.tile_size, y * self.tile_size, self.tile_size, entity_prob)
        return terrain_grid
