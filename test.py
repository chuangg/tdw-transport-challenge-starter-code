# import gym
# import pickle
# import pkg_resources
# from tdw_transport_challenge.h_agent import H_agent
# from agent import init_logs
#
# # Create gym environment.
# env = gym.make("transport_challenge-v0", train=0, physics=True, port=1071)
#
# # Load training scenes
# with open(pkg_resources.resource_filename("tdw_transport_challenge", "train_dataset.pkl")) as fp:
#     dataset = pickle.load(fp)
#
#     # Load training scene. scene_number is from 0 - 100
# scene_number = 0
# obs, info = env.reset(dataset[scene_number])
#
# # create logger
# logger = init_logs()
# # Instantiate baseline agent
# agent = H_agent(logger=logger)
#
# while True:
#     action = agent.act(obs, info)
#     obs, rewards, done, info = env.step(action)
#     if done:
#         break
#
# env.close()



import shlex
