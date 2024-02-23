'''
Pick up notes:

the data has gaps in it of course so i was trying to get it to work on a tiny small sample
so clean up the data and try with larger set

how do i add in "do nothing" into the action space with buy and sell
'''


import gym
import gym_anytrading

import gymnasium
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import A2C
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



#import data into df and make the index a datetime index
df = pd.read_csv("prepared_data.csv")
if df.isnull().any().any():
    print("null values found")
else:
    print("No null Values in df")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df.set_index("Timestamp",inplace = True)
df= df.tail(30)
#print(df.head())



#all possible environment names 
list_poss = gymnasium.envs.registry.keys()


#test the environment works

#frame upper is the upper limit index of training set
frame_upper = 20
window_size = 2

env = gymnasium.make("gym_anytrading:stocks-v0",df=df,frame_bound=(2,frame_upper),window_size = window_size)

#print(f"observation space:{env.observation_space}")

state = env.reset()
counter = 1
max_steps = frame_upper-window_size
while True:
    
    action = env.action_space.sample()
    n_state,reward,done,_,info = env.step(action)
    print(f"\n#{counter}\nN_state:{n_state}\nReward: {reward}\nDone: {done}\n_: {_}\nInfo: {info}\n")
    counter+=1
    if done or counter >= max_steps:
        print(f"info:{info}")
        break


#plot figure
    
plt.figure(figsize = (15,6))
plt.cla()
plt.title("Random Agent")
env.render_all() 
plt.show()          


#train an agent
env_maker = lambda: gymnasium.make("gym_anytrading:stocks-v0",df=df,frame_bound=(2,frame_upper),window_size = window_size)
env2 = DummyVecEnv([env_maker])
model = A2C("MlpPolicy",env2,verbose=1)
model.learn(total_timesteps=100000)


#test the agent
env3 = gymnasium.make("gym_anytrading:stocks-v0",df=df,frame_bound=(2,24),window_size = 2)
state = env3.reset()[0] 
print(f"State:{state}")
counter = 1
max_steps = 22-window_size
while True:
    action,_states = model.predict(state)
    print(f"action: {action}\n_states:{_states}")
    obs,rewards,done,_,info = env3.step(action)
    counter+=1
    if done or counter >= max_steps:
        print(f"info:{info}")
        break


plt.figure(figsize = (15,6))
plt.cla()
plt.title("Trained agent")
env3.render_all()
plt.show()

print("End of program")