from stable_baselines3 import PPO

from custom_env import CustomEnv
from agent_model import AgentModel

# Define the arguments for the environment and model
model_args = {
    'num_actions': 11
}

simulation_manager_args = {
    'number_of_environments': 10,
    'number_of_curricula': 3
}

game_manager_args = {
    'num_tiles': 8,
    'screen_size': 400,
    'kg_completeness': 1,
    'vision_range': 1
}

# Initialize the custom environment
env = CustomEnv(game_manager_args, simulation_manager_args, model_args, plot=False)

# Print the observation space details
print("Observation Space:", env.observation_space)
print("Sample Observation from reset:", env.reset())

# Check if observation matches the defined space
sample_obs = env.reset()
# assert env.observation_space.contains(sample_obs), "The sample observation does not match the defined observation space"

# Bind the new method to the CustomEnv instance
CustomEnv.evaluate_policy = env.evaluate_policy

# Define model initialization parameters directly from environment setup
vision_shape = (3, 2 * game_manager_args['vision_range'] + 1, 2 * game_manager_args['vision_range'] + 1)
num_graph_features = env.kg.graph.x.shape[1]
num_edge_features = env.kg.graph.edge_attr.shape[1]

print("training.py")
print(f"Vision shape: {vision_shape} (channels, height, width)")
print(f"Number of graph features: {num_graph_features}")
print(f"Number of edge features: {num_edge_features}")

"""
the observation is the vision and the whole graph.
Then the graph is separated into its nodes and egdes in the model.
"""
print("Observation Space:", env.observation_space)

# Get details from the initialized environment necessary for the model
vision_shape = env.observation_space['vision'].shape
num_nodes = env.kg.graph.num_nodes
num_node_features = env.kg.graph.num_node_features
num_edge_features = env.kg.graph.num_edge_features

# Define features extractor configuration
features_extractor_kwargs = {
    'vision_shape': vision_shape,
    'num_graph_features': num_node_features,
    'num_edge_features': num_edge_features,
    'num_actions': env.num_actions
}

# Instantiate the PPO agent with MultiInputPolicy
rl_model = PPO("MultiInputPolicy", env, policy_kwargs={
    'features_extractor_class': AgentModel,
    'features_extractor_kwargs': features_extractor_kwargs
}, verbose=1)

# Train the model
total_timesteps = 100000
rl_model.learn(total_timesteps=total_timesteps)

# Save the trained model
rl_model.save("ppo_custom_env")
env.simulation_manager.save_data()

# Evaluate the model
mean_reward, std_reward = env.evaluate_policy(rl_model, rl_model.get_env(), n_eval_episodes=10)
print(f"Mean reward: {mean_reward} +/- {std_reward}")

# Close the environment
env.close()
