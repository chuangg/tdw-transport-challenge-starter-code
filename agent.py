import argparse
from tdw_transport_challenge.challenge import Challenge
from tdw_transport_challenge.simple_agent import TestAgent
from tdw_transport_challenge.h_agent import H_agent
import logging
import os


def init_logs():
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join("/", "results", "output.log"))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_agent(agent_class, logger, ckpt_path=""):
    if agent_class == "Test":
        return TestAgent()
    elif agent_class == "h_agent":
        return H_agent(logger=logger)
    '''elif agent_class == "Random":
        return RandomAgent()
    elif agent_class == "ForwardOnly":
        return ForwardOnlyAgent()
    elif agent_class == "SAC":
        return SACAgent(root_dir=ckpt_path)'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-class", type=str, default="Test", choices=["Test", "h_agent"])
    parser.add_argument("--ckpt-path", default="", type=str)
    parser.add_argument("--port", default=1071, type=int)
    args = parser.parse_args()
    if not os.path.exists('/results'):
        os.mkdir('/results')
    logger = init_logs()
    # Instantiate your agent here
    agent = get_agent(
        agent_class=args.agent_class,
        logger=logger,
        ckpt_path=args.ckpt_path
    )
    challenge = Challenge(logger, args.port)
    try:
        challenge.submit(agent)
    finally:
        challenge.close()


if __name__ == "__main__":
    main()