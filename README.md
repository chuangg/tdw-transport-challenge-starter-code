## Setting up the Environment
To get started setup the required environments by following below steps
   
### Setting TDW Transport Challenge environment

1. Install [Transport Challenge API and TDW build](https://github.com/alters-mit/transport_challenge)
2. Install [Transport Challenge Gym API](https://github.com/chuangg/tdw-transport-challenge)
3. Download [Transport Challenge data](https://tdw-transport-challenge-storage-bucket-au.s3.au-syd.cloud-object-storage.appdomain.cloud/model_library.zip). By downloading this data you are agreeing to these [terms and conditions ](#terms-and-conditions)

If you install `transport_challenge` , it will automatically install `tdw` and `magnebot`. The `transport_challenge` repo has instructions for how to downgrade `magnebot` and `tdw` .

## Working with code
### Gym Scenes
The dataset is modular in its design, consisting of several physical floor plan geometries with a wall and floor texture 
variations (e.g. parquet flooring, ceramic tile, stucco, carpet etc.) and various furniture and prop layouts (tables, 
chairs, cabinets etc.), for a total of 15 separate environments. There are 10 kinds of scenes in training dataset and 
5 kinds of scenes in testing. Every scene has 6 to 8 rooms, 8 objects, and some containers.
### Gym Actions
* move forward at 0.5
```
dict {"type": 0} 
```
* turn left 15 degrees
```
dict {"type": 1} 
```
* turn right 15 degrees
```
dict {"type": 2} 
```
* grasp the object with arm
```
dict {"type": 3, "object": object_id, "arm": "left" or "right"} 
```
* put the object into the container
```
dict {"type": 4, "object": object_id, "container": container_id} 
```
* drop objects
```
dict {"type": 5}
```
### Not using Docker
* Makesure the environment is setup by following above instructions
  
* Here is an example of how to instantiate an environment and use a simple baseline agent.
  ```python
    import gym
    import pickle
    import pkg_resources
    from tdw_transport_challenge.h_agent import H_agent
    from agent import init_logs
    
    # Create gym environment. 
    env = gym.make("transport_challenge-v0", train = 0, physics = True, port = 1071, launch_build=False)
    
    # Load training scenes
    with open(pkg_resources.resource_filename("tdw_transport_challenge", "train_dataset.pkl"), 'rb') as fp:
        dataset = pickle.load(fp)  
  
    # Load training scene. scene_number is from 0 - 100
    scene_number = 0
    obs, info = env.reset(scene_info=dataset[scene_number])
    
    # create logger
    logger = init_logs()
    # Instantiate baseline agent
    agent = H_agent(logger=logger)
  
    while True:
        action = agent.act(obs, info)
        obs, rewards, done, info = env.step(action)
        if done:
            break
  
    env.close()
   ```
  Set the `TRANSPORT_CHALLENGE` environment variable to path of the downloaded data.
    ```shell
    # Run TDW with port 1071
    ./TDW/TDW.x86_64 -port 1071 &
  
    # Run the python file
    python test.py
    ```
  If you set `launch_build=True` then build will automatically launch with your controller and running `./TDW/TDW.x86_64 -port 1071 &` separately is not required. 
    
* To run multiple environments / vectorize environments you can use 
  [stable baselines](https://github.com/hill-a/stable-baselines). Here is an example:
  ```python
  from stable_baselines.common.vec_env.subproc_vec_env import SubprocVecEnv
  import gym
  import random
  
  def create_env(port):
    env = gym.make("transport_challenge-v0",train = 0, physics = True, port = port, launch_build=True)
    env.reset()
    return env
  
  def make_env(port):
    def _init():
        env = create_env(port)
        return env
    return _init
  
  def make_vec_env(num_processes):
    ports = random.sample(range(1071, 1171), num_processes)
    env = SubprocVecEnv([make_env( port=ports[i]) for i in range(num_processes)])
    return env
  
  def main():
    num_env = 5
    v_env = make_vec_env(num_env)
    obs = v_env.reset()
    for i in range(10):
        action = get_action(obs)
        obs, rewards, dones, info = v_env.step(action)
        v_env.render()
    v_env.close()
  
  if __name__ == '__main__':
      main()

    ```
### Using Docker
* Follow [these steps](#running-in-docker-container) to set up the environment to run docker container. Once completed 
  you can edit the `run_locally.sh` file to run your python code.
* Next build the container 
  ```shell script
      docker build --no-cache -t submission_image .
  ```
* Run container
  ```shell
    nvidia-docker run --network host --env="DISPLAY=:4" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" --volume="/tmp/output:/results" -e NVIDIA_DRIVER_CAPABILITIES=all -e TRANSPORT_CHALLENGE=file:////model_library -e NUM_EVAL_EPISODES=1 -d submission_image sh run_baseline_agent.sh 7845
  ```
* Running multiple environments 
### Online Submission
To prepare your agent for submission instantiate your agent in agent.py. This file will
test your agent on testing scenes. Use docker build command 
`docker build --no-cache -t tdwbase --build-arg TDW_VERSION=1.8.4 .` to create final submission image. You can follow
the instructions on [EvalAI Challenge page](https://eval.ai/web/challenges/challenge-page/825/overview) for submission of the image. 
To Make a submission:
* Create account on `https://eval.ai/`
* Find the challenge: Dashboard -> All Challenges, and look for TDW-Transport Challenge
* Clickl on participation tab :
    * Create a new team if you don't already have one
    * Enter the competition
* Then click on submit tab and follow steps to setup Evalai cli and submit the image
### Local Evaluation
Before submitting the image make sure that the docker image works by evaluating locally. To do this use this docker run 
command
```shell script
mkdir /tmp/output
nvidia-docker run --network host --env="DISPLAY=:4" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" --volume="/tmp/output:/results" -e NVIDIA_DRIVER_CAPABILITIES=all -e TRANSPORT_CHALLENGE=file:////model_library -e NUM_EVAL_EPISODES=1 -d submission_image sh run_submission.sh 7845
```
In this command the Display server is :4 ([see this](#setting-up-headless-x-server) for setting up display server). Local directory /tmp/output is volume 
mapped. The evaluation result will be generated in this directory and can be accessed even after the container has 
finished.

## Running in Docker container
TDW can be run in a docker container on a remote server with GPU. The container needs access to x-server
in order to leverage GPU for 3-D acceleration. The contanerization process mentioned here is only supported on a headless
remote machine with Ubuntu. 
#### Setting up Headless X-server
At this point we have only tested this on a remote ubuntu machine (16.04 and 18.04). The user will need to have sudo
access in-order for x-server to work
1. Download and install latest Nvidia drivers for the machine
2. Install xorg and depencies `sudo apt-get install -y gcc make pkg-config xorg`
3. Run `nvidia-xconfig --query-gpu-info`. This will list all the GPUs and their bus ids
4. Run `nvidia-xconfig --no-xinerama --probe-all-gpus --use-display-device=none`. This will generate xorg.conf 
   (/etc/X11/xorg.conf) file 
5. Make n copies of this file for n gpus. You can name each file as xorg-1.conf, xorg-2.conf ... xorg-n.conf
6. Edit each file:
    1. Remove ServerLayout and Screen section
    2. Edit Device section to include the BusID and BoardName field of the corresponding GPU. You can get GPU list by 
       running `nvidia-xconfig --query-gpu-info`  
7. For example if `nvidia-xconfig --query-gpu-info` outputs two gpus:
```text
Number of GPUs: 2

GPU #0:
  Name      : Tesla V100-PCIE-16GB
  UUID      : GPU-bbf6c915-de29-6e08-90e6-0da7981a590b
  PCI BusID : PCI:0:7:0

  Number of Display Devices: 0


GPU #1:
  Name      : Tesla V100-PCIE-16GB
  UUID      : GPU-2a69c672-c895-5671-00ba-14ac43a9ec39
  PCI BusID : PCI:0:8:0

  Number of Display Devices: 0
```
Then create two xorg.conf files and edit the device section for first file:
```text 
This ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
To ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "Tesla V100-PCIE-16GB"
    BusID          "PCI:0:7:0"
EndSection

```
And for the second file:
```text 
This ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
EndSection
To ->
Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "Tesla V100-PCIE-16GB"
    BusID          "PCI:0:8:0"
EndSection
```
8. Run x-server. For each xorg configuration file run `sudo nohup Xorg :<Display server name> -config <configuration file name> & `
```text
e.g.
sudo nohup Xorg :1 -config /etc/X11/xorg-1.conf & 
sudo nohup Xorg :2 -config /etc/X11/xorg-2.conf &
.
.
.
sudo nohup Xorg :n -config /etc/X11/xorg-n.conf &
```
9. When successfully done, running `nvidia-smi` should show the x-server proccess with corresponding gpu version
#### Install docker and nvidia-docker
You can follow docker and nvidia-docker installation [instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
### Building and running container
Finally, build the container by doing 
```shell script
docker build --no-cache -t submission_image .
```
You can test the code by running a simple baseline agent. You can replace `/tmp/output` with any other directory. 
Replace :4 with display server name created in previous step
```shell
nvidia-docker run --network none --env="DISPLAY=:4" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" --volume="/tmp/output:/results" -e NVIDIA_DRIVER_CAPABILITIES=all -e TRANSPORT_CHALLENGE=file:////model_library -e NUM_EVAL_EPISODES=1 -d submission_image sh run_baseline_agent.sh 7845
```
### Terms and Conditions
1. Challenge Dataset License: The dataset provided in this challenge are licensed under the MIT License (https://github.com/threedworld-mit/tdw/blob/master/LICENSE.txt) and are solely owned by Massachusetts Institute of Technology. International Business Machines Corporation only hosts this data. You accept full responsibility for your use of the datasets and shall defend and indemnify Massachusetts Institute of Technology and International Business Machines Corporation, including its employees, officers and agents, against any and all claims arising from your use of the datasets
 2. Massachusetts Institute of Technology and the International Business Machines Corporation make no representations or warranties regarding the datasets, including but not limited to warranties of non-infringement or fitness for a particular purpose.
 3. International Business Machines Corporation does not store or distribute any user information including username, email address, team name etc. and only uses email address and team name for updating leaderboard information. 
 4. User submission including user reinforcement learning policy is evaluated by International Business Machines Corporation on its own terms and evaluation result is reported to leaderboard. International Business Machines Corporation does not store or distribute user submission.
