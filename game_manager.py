import numpy as np
import pygame

from heightmap_generator import HeightmapGenerator
from environment import Environment
from agent import Agent
from renderer import Renderer
from target import Target_Manager

from knowledge_graph import KnowledgeGraph

class GameManager:
    def __init__(self, map_pixel_size=32, screen_size=800, kg_completness=1):
        self.map_size = map_pixel_size
        self.tile_size = screen_size // map_pixel_size
        self.environment = None
        self.kg_completness = kg_completness
        self.agent_controler = None
        self.agent = None
        self.target_manager = None

        self.agent_vision_range = 2

        self.renderer = None
        self.running = True

        self.init_pygame()
        self.load_resources()
        self.initialize_components()
        # self.test()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Game World")
    
    def load_resources(self):
        # If you have any resources to load, do it here
        pass

    def initialize_components(self):
        # Generate heightmap
        heightmap_generator = HeightmapGenerator(
            width=self.map_size, 
            height=self.map_size, 
            scale=10, 
            terrain_thresholds=np.array([0.2, 0.38, 0.5, 0.7, 0.9, 1.0]), 
            octaves=3, persistence=0.2, lacunarity=2.0
        )
        heightmap = heightmap_generator.generate()
        self.environment = Environment(heightmap, self.tile_size, number_of_outposts=3)
        self.kg = KnowledgeGraph(self.environment, self.agent_vision_range, self.kg_completness)
        self.agent_controler = Agent(self.environment, self.kg)
        self.agent = self.agent_controler.agent
        self.target_manager = Target_Manager(self.environment)

    def initialise_rendering(self):
        self.renderer = Renderer(self.environment, self.agent_controler)
        self.screen = pygame.display.set_mode((self.map_size * self.tile_size, self.map_size * self.tile_size))
        self.renderer.init_render()

    def handle_keyboard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.agent_controler.agent_action(11)

    def render(self):
        self.renderer.render()
        pygame.display.flip()

    def run(self):
        self.initialise_rendering()
        while self.running:
            pygame.time.delay(1500)
            exit()
            self.handle_keyboard()
            self.update()
            self.renderer.render_updated_tiles()

        pygame.quit()
        print('Game closed')
        self.environment.print_entities()