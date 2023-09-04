from renderer import TerrainRenderer
from heightmap_generator import HeightmapGenerator
from river import RiverPathFinder

if __name__ == '__main__':
    thresholds = {'deep_water': 0.15, 'water': 0.30, 'plains': 0.5, 'hills': 0.7, 'mountains': 0.85, 'snow': 1.0}
    colors = {0: (0, 0, 128), 1: (0, 0, 255), 2: (0, 255, 0), 3: (0, 128, 0), 4: (128, 128, 128), 5: (255, 255, 255), 6: (80, 127, 255)}

    generator = HeightmapGenerator(800, 800, 350.0, thresholds, 6, 0.6, 1.8)
    heightmap = generator.generate()
    
    river_path_finder = RiverPathFinder(heightmap)  # Assuming this is your river algorithm class
    updated_heightmap = river_path_finder.find_path()  # Assuming this function updates the heightmap to add the river
    
    renderer = TerrainRenderer(updated_heightmap, colors)
    renderer.real_time_update()
