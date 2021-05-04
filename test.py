import gym
import pickle
import pkg_resources
from tdw_transport_challenge.h_agent import H_agent
from agent import init_logs


# Create gym environment and load first training scene
env = gym.make("transport_challenge-v0", train=0, physics=True, port=1071)

# Reset environment and change to next training scene
env.reset()

# Load Testing scenes
with open(pkg_resources.resource_filename("tdw_transport_challenge", "test_env.pkl"), "rb") as fp:
    dataset = pickle.load(fp)

# scene_number is from 0 - 4
scene_number = 0
obs, info = env.reset(dataset[scene_number])

# create logger
logger = init_logs()
# Instantiate baseline agent
agent = H_agent(logger=logger)
agent.reset()

while True:
    action = agent.act(obs, info)
    obs, rewards, done, info = env.step(action)
    if done:
        break

env.close()
