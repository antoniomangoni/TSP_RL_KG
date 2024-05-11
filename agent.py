from random import choice
import pygame
import numpy as np

from environment import Environment
from entities import Fish, Tree, MossyRock, SnowyRock, Outpost, WoodPath
from terrains import DeepWater, Water
# from agent_model import AgentModel
from knowledge_graph import KnowledgeGraph


class Agent:
    def __init__(self, environment : Environment, agent_vision_range : int, kg : KnowledgeGraph):
        self.environment = environment
        self.terrain_id_grid = self.environment.terrain_index_grid
        self.entity_id_grid = self.environment.entity_index_grid
        self.kg = kg
        self.agent = self.environment.player

        self.running = True

        self.energy_max = 100
        self.resouce_max = 5
        self.hunger_thirst_max = 20
        self.vision_range = agent_vision_range 

        self.energy = 100 # Decrease when moving or collecting resources, increase when resting
        self.hunger = 0 # Eat fish to derease
        self.thirst = 0 # Drink water to decrease
        self.wood = 0
        self.stone = 0
        self.fish = 0
        self.water = 0

    def agent_step(self):
        self.energy -= self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y].energy_requirement
        self.hunger += 1
        self.thirst += 1
        if self.energy <= 0 or self.hunger >= 20 or self.thirst >= 20:
            self.running = False
        if self.running:
            self.agent_action(self.agent_model.predict(self.environment.terrain_object_grid, self.agent.grid_x, self.agent.grid_y))

    def agent_action(self, action):
        action = choice(range(8))
        if action == 0:
            self.agent_move()
        elif action == 1:
            self.rest_and_see()
        elif action == 2:
            self.build_path()
        elif action == 3:
            self.place_rock()
        elif action == 4:
            self.collect_resource(0, 1)
        elif action == 5:
            self.collect_resource(0, -1)
        elif action == 6:
            self.collect_resource(1, 0)
        elif action == 7:
            self.collect_resource(-1, 0)

    def agent_move(self):
        (dx, dy) = choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.environment.move_entity(self.agent, dx, dy)
        self.kg.move_player_node(self.agent.grid_x, self.agent.grid_y)

    def rest_and_see(self):
        """ Looking at the environment is a deliberate action. """
        self.energy = min(self.energy_max, self.energy + 20)
        """ Adding a terrain node automatically adds the corresponding entity node"""
        for y in range(self.agent.grid_y - self.vision_range, self.agent.grid_y + self.vision_range + 1):
            for x in range(self.agent.grid_x - self.vision_range, self.agent.grid_x + self.vision_range + 1):
                if self.environment.within_bounds(x, y):
                    self.kg.discover_this_coordinate(x, y)

    def build_path(self):
        if isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], Water):
            return
        if isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], DeepWater):
            return
        # print(f'Current inventory - Wood: {self.wood})')
        # print(f'Player position: {self.agent.grid_x, self.agent.grid_y}')
        if self.wood >= 1:
            # print(f'Placing - Wood inventory: {self.wood}')
            self.wood -= 1
            self.environment.place_path(self.agent.grid_x, self.agent.grid_y)
            self.kg.build_path_node(self.agent.grid_x, self.agent.grid_y)
            # assert self.environment.entity_index_grid[self.agent.grid_x, self.agent.grid_y] == 6
            # print(self.environment.entity_index_grid[self.agent.grid_x, self.agent.grid_y])
            # print(self.environment.entity_index_grid)
            # print(f'Entity on tileis {self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y].entity_on_tile}')
            # print(f'Entity index is {self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y].entity_index}')
            self.kg.visualise_graph()

    def place_rock(self):
        if self.stone < 1:
            return
        place = -1
        if isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], DeepWater):
            place = 0
        elif isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], Water):
            place = 1
        else:
            return
        self.stone -= 1
        # print(f'Placing - Stone inventory: {self.stone}')
        self.environment.drop_rock_in_water(self.agent.grid_x, self.agent.grid_y, place)
        self.kg.elevate_terrain_node(self.agent.grid_x, self.agent.grid_y)

    def collect_resource(self, dx, dy):
        x, y = self.agent.grid_x + dx, self.agent.grid_y + dy
        assert (x, y) != (self.agent.grid_x, self.agent.grid_y)
        if self.environment.within_bounds(x, y) is False:
            return
        if self.entity_id_grid[x, y] == 0:
            return
        resource = self.environment.terrain_object_grid[x, y].entity_on_tile
        if resource is None or isinstance(resource, Outpost) or isinstance(resource, WoodPath):
            return
        else:
            """ Fish have been removed as they are uncencessary for the scope of the project. """	
            # if isinstance(resource, Fish):
            #     if self.fish >= self.resouce_max:
            #         return
            #     self.fish += 1
            if isinstance(resource, Tree):
                if self.wood >= self.resouce_max:
                    return
                self.wood += 1
                # print(f'Collecting - Wood inventory: {self.wood}')
            elif isinstance(resource, MossyRock):
                if self.stone >= self.resouce_max:
                    return
                self.stone += 1
                # print(f'Collecting - Stone inventory: {self.stone}')
            elif isinstance(resource, SnowyRock):
                if self.stone >= self.resouce_max:
                    return
                self.stone += 1
                # print(f'Collecting - Stone inventory: {self.stone}')
            self.environment.delete_entity(resource)
            self.kg.remove_entity_node(x, y)

"""
These are not implemented as they do not fall within the scope of the project.
They have been left here for future reference.


    def collect_water(self):
        if isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], Water):
            self.water += 1
        elif isinstance(self.environment.terrain_object_grid[self.agent.grid_x, self.agent.grid_y], DeepWater):
            self.water += 2

    def drink(self):
        self.rest()
        if self.water > 0:
            self.water -= 1
            self.thirst = max(0, self.thirst - 5)

    def eat(self):
        self.rest()
        if self.fish > 0:
            self.fish -= 1
            self.hunger = max(0, self.hunger - 5)

"""
